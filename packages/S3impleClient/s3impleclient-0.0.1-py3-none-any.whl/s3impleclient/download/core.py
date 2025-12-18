"""
Core async downloader implementation with parallel range requests.

Uses pipelined parallel download + write:
- Large chunks (128MB) for disk writes
- Small chunks (4MB) for HTTP requests within each large chunk
- Pipeline: download chunk N+1 while writing chunk N
"""

import asyncio
from pathlib import Path
from typing import BinaryIO, Callable

import aiofiles
import httpx

from ..progress import NoopProgressTracker, ProgressTracker
from .config import DownloadConfig
from .result import DownloadResult, ShardInfo


class Downloader:
    """
    Async HTTP/S3 downloader with pipelined parallel downloads.

    Pipeline approach:
    1. Download large chunk (using parallel small chunk requests)
    2. While writing that chunk, start downloading next chunk
    3. Overlap I/O for maximum throughput
    """

    def __init__(self, config: DownloadConfig | None = None):
        self.config = config or DownloadConfig()

    # -------------------------------------------------------------------------
    # URL Probing
    # -------------------------------------------------------------------------

    async def probe_url(
        self,
        url: str,
        client: httpx.AsyncClient,
        headers: dict[str, str] | None = None,
    ) -> tuple[str, int | None, bool]:
        """
        Probe URL to get final URL (after redirects), content length, and range support.

        Returns:
            (final_url, content_length, supports_range)
        """
        req_headers = {**self.config.headers, **(headers or {})}

        response = await client.head(
            url,
            headers=req_headers,
            follow_redirects=self.config.follow_redirects,
        )
        response.raise_for_status()

        final_url = str(response.url)
        content_length: int | None = None
        supports_range = False

        if "content-length" in response.headers:
            content_length = int(response.headers["content-length"])

        accept_ranges = response.headers.get("accept-ranges", "").lower()
        if accept_ranges == "bytes":
            supports_range = True

        if not supports_range and content_length and content_length > 0:
            try:
                range_headers = {**req_headers, "Range": "bytes=0-0"}
                range_response = await client.head(
                    final_url,
                    headers=range_headers,
                    follow_redirects=False,
                )
                if range_response.status_code == 206:
                    supports_range = True
            except httpx.HTTPError:
                pass

        return final_url, content_length, supports_range

    # -------------------------------------------------------------------------
    # Chunk Calculation
    # -------------------------------------------------------------------------

    def calculate_write_chunks(self, total_size: int) -> list[tuple[int, int]]:
        """Calculate large chunks for disk writes. Returns list of (start, end) inclusive."""
        write_size = self.config.write_chunk_size
        chunks: list[tuple[int, int]] = []
        offset = 0

        while offset < total_size:
            end = min(offset + write_size - 1, total_size - 1)
            chunks.append((offset, end))
            offset = end + 1

        return chunks

    def calculate_shards(self, start: int, end: int) -> list[ShardInfo]:
        """Calculate small HTTP request shards within a range."""
        chunk_size = self.config.chunk_size
        shards: list[ShardInfo] = []
        offset = start
        index = 0

        while offset <= end:
            shard_end = min(offset + chunk_size - 1, end)
            shards.append(ShardInfo(index=index, start=offset, end=shard_end))
            offset = shard_end + 1
            index += 1

        return shards

    # -------------------------------------------------------------------------
    # Shard Download
    # -------------------------------------------------------------------------

    async def _stream_shard_to_buffer(
        self,
        response: httpx.Response,
        buffer: bytearray,
        buf_start: int,
        shard: ShardInfo,
        progress_callback: Callable[[int], None] | None,
    ) -> None:
        """Stream response content into buffer at correct position."""
        buf_pos = buf_start

        async for chunk in response.aiter_bytes(self.config.buffer_size):
            buffer[buf_pos : buf_pos + len(chunk)] = chunk
            buf_pos += len(chunk)
            if progress_callback:
                progress_callback(len(chunk))

        # Verify downloaded size
        downloaded = buf_pos - buf_start
        if downloaded != shard.size:
            raise ValueError(
                f"Shard {shard.index} size mismatch: expected {shard.size}, got {downloaded}"
            )

    async def download_shard(
        self,
        url: str,
        shard: ShardInfo,
        client: httpx.AsyncClient,
        buffer: bytearray,
        buffer_offset: int,
        semaphore: asyncio.Semaphore,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> None:
        """Download a single small shard into buffer with retry."""
        req_headers = {
            **self.config.headers,
            **(headers or {}),
            "Range": f"bytes={shard.start}-{shard.end}",
        }
        buf_start = shard.start - buffer_offset
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                async with semaphore:
                    async with client.stream(
                        "GET", url, headers=req_headers, follow_redirects=False
                    ) as response:
                        response.raise_for_status()
                        await self._stream_shard_to_buffer(
                            response, buffer, buf_start, shard, progress_callback
                        )
                return

            except (httpx.HTTPError, httpx.StreamError, ValueError) as e:
                last_error = e
                if attempt < self.config.max_retries:
                    await asyncio.sleep(min(2**attempt, 30))

        raise last_error or RuntimeError(f"Failed to download shard {shard.index}")

    # -------------------------------------------------------------------------
    # Large Chunk Download
    # -------------------------------------------------------------------------

    async def download_write_chunk(
        self,
        url: str,
        client: httpx.AsyncClient,
        chunk_start: int,
        chunk_end: int,
        semaphore: asyncio.Semaphore,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> bytearray:
        """Download a large chunk using parallel small requests. Returns buffer."""
        buffer = bytearray(chunk_end - chunk_start + 1)
        shards = self.calculate_shards(chunk_start, chunk_end)

        tasks = [
            asyncio.create_task(
                self.download_shard(
                    url=url,
                    shard=shard,
                    client=client,
                    buffer=buffer,
                    buffer_offset=chunk_start,
                    semaphore=semaphore,
                    headers=headers,
                    progress_callback=progress_callback,
                )
            )
            for shard in shards
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                raise result

        return buffer

    # -------------------------------------------------------------------------
    # Pipelined Download
    # -------------------------------------------------------------------------

    async def download_parallel_pipelined(
        self,
        url: str,
        client: httpx.AsyncClient,
        dest_path: Path | str,
        total_size: int,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> int:
        """
        Download with pipelined parallel: download chunk N+1 while writing chunk N.
        """
        semaphore = asyncio.Semaphore(self.config.max_workers)
        write_chunks = self.calculate_write_chunks(total_size)

        if not write_chunks:
            return 0

        async with aiofiles.open(dest_path, "wb") as f:
            # Pre-allocate file
            await f.seek(total_size - 1)
            await f.write(b"\0")
            await f.seek(0)

            # Download first chunk
            current_chunk_idx = 0
            chunk_start, chunk_end = write_chunks[current_chunk_idx]
            current_buffer = await self.download_write_chunk(
                url=url,
                client=client,
                chunk_start=chunk_start,
                chunk_end=chunk_end,
                semaphore=semaphore,
                headers=headers,
                progress_callback=progress_callback,
            )

            # Pipeline: write current while downloading next
            while current_chunk_idx < len(write_chunks):
                chunk_start, chunk_end = write_chunks[current_chunk_idx]

                if current_chunk_idx + 1 < len(write_chunks):
                    # Start downloading next chunk while writing current
                    next_start, next_end = write_chunks[current_chunk_idx + 1]
                    download_task = asyncio.create_task(
                        self.download_write_chunk(
                            url=url,
                            client=client,
                            chunk_start=next_start,
                            chunk_end=next_end,
                            semaphore=semaphore,
                            headers=headers,
                            progress_callback=progress_callback,
                        )
                    )

                    # Write current chunk
                    await f.seek(chunk_start)
                    await f.write(current_buffer)

                    # Wait for next download to complete
                    current_buffer = await download_task
                else:
                    # Last chunk - just write
                    await f.seek(chunk_start)
                    await f.write(current_buffer)

                current_chunk_idx += 1

        return total_size

    # -------------------------------------------------------------------------
    # Single Stream Fallback
    # -------------------------------------------------------------------------

    async def download_single_stream(
        self,
        url: str,
        client: httpx.AsyncClient,
        output_file: BinaryIO,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> int:
        """Fallback single-stream download when range requests not supported."""
        req_headers = {**self.config.headers, **(headers or {})}
        total_downloaded = 0

        async with client.stream(
            "GET",
            url,
            headers=req_headers,
            follow_redirects=self.config.follow_redirects,
        ) as response:
            response.raise_for_status()

            async for chunk in response.aiter_bytes(self.config.buffer_size):
                output_file.write(chunk)
                total_downloaded += len(chunk)
                if progress_callback:
                    progress_callback(len(chunk))

        return total_downloaded

    async def download_single_stream_to_path(
        self,
        url: str,
        client: httpx.AsyncClient,
        dest_path: Path | str,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> int:
        """Single-stream download to file path using aiofiles."""
        req_headers = {**self.config.headers, **(headers or {})}
        total_downloaded = 0

        async with client.stream(
            "GET",
            url,
            headers=req_headers,
            follow_redirects=self.config.follow_redirects,
        ) as response:
            response.raise_for_status()

            async with aiofiles.open(dest_path, "wb") as f:
                async for chunk in response.aiter_bytes(self.config.buffer_size):
                    await f.write(chunk)
                    total_downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(len(chunk))

        return total_downloaded

    # -------------------------------------------------------------------------
    # Download to File Object (for HF patcher)
    # -------------------------------------------------------------------------

    async def download_parallel_to_fileobj(
        self,
        url: str,
        client: httpx.AsyncClient,
        output_file: BinaryIO,
        total_size: int,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> int:
        """
        Download with pipeline to a file object (for HF patcher).
        """
        file_path = getattr(output_file, "name", None)

        if file_path:
            output_file.close()
            return await self.download_parallel_pipelined(
                url=url,
                client=client,
                dest_path=file_path,
                total_size=total_size,
                headers=headers,
                progress_callback=progress_callback,
            )
        else:
            # Fallback: download all to RAM then write
            semaphore = asyncio.Semaphore(self.config.max_workers)
            shards = self.calculate_shards(0, total_size - 1)
            full_buffer = bytearray(total_size)

            tasks = [
                asyncio.create_task(
                    self.download_shard(
                        url=url,
                        shard=shard,
                        client=client,
                        buffer=full_buffer,
                        buffer_offset=0,
                        semaphore=semaphore,
                        headers=headers,
                        progress_callback=progress_callback,
                    )
                )
                for shard in shards
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    raise result

            output_file.seek(0)
            output_file.truncate(total_size)
            output_file.write(full_buffer)

            return total_size

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    async def download_to_file_async(
        self,
        url: str,
        dest: Path | str,
        headers: dict[str, str] | None = None,
        expected_size: int | None = None,
        progress_tracker: ProgressTracker | None = None,
    ) -> DownloadResult:
        """Download URL to file asynchronously."""
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)

        progress = progress_tracker or NoopProgressTracker()

        try:
            timeout = httpx.Timeout(self.config.timeout, read=self.config.timeout * 2)
            async with httpx.AsyncClient(timeout=timeout) as client:
                final_url, content_length, supports_range = await self.probe_url(
                    url, client, headers
                )

                total_size = expected_size or content_length

                if total_size:
                    progress.set_total(total_size)

                use_parallel = (
                    supports_range
                    and total_size
                    and total_size > self.config.chunk_size
                )

                if use_parallel:
                    downloaded = await self.download_parallel_pipelined(
                        url=final_url,
                        client=client,
                        dest_path=dest,
                        total_size=total_size,
                        headers=headers,
                        progress_callback=progress.update,
                    )
                else:
                    downloaded = await self.download_single_stream_to_path(
                        url=final_url,
                        client=client,
                        dest_path=dest,
                        headers=headers,
                        progress_callback=progress.update,
                    )

                if expected_size and downloaded != expected_size:
                    raise ValueError(
                        f"Size mismatch: expected {expected_size}, got {downloaded}"
                    )

                return DownloadResult(
                    success=True,
                    path=dest,
                    total_bytes=downloaded,
                )

        except Exception as e:
            # Clean up partial file on failure
            if dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass
            return DownloadResult(
                success=False,
                path=None,
                total_bytes=0,
                error=e,
            )
        finally:
            progress.close()

    async def download_to_fileobj_async(
        self,
        url: str,
        fileobj: BinaryIO,
        headers: dict[str, str] | None = None,
        expected_size: int | None = None,
        progress_tracker: ProgressTracker | None = None,
        resume_size: int = 0,
    ) -> int:
        """Download URL to file object asynchronously (for HF patcher)."""
        progress = progress_tracker or NoopProgressTracker()

        try:
            timeout = httpx.Timeout(self.config.timeout, read=self.config.timeout * 2)
            async with httpx.AsyncClient(timeout=timeout) as client:
                final_url, content_length, supports_range = await self.probe_url(
                    url, client, headers
                )

                total_size = expected_size or content_length
                remaining_size = (total_size - resume_size) if total_size else None

                if total_size:
                    progress.set_total(total_size)
                if resume_size:
                    progress.update(resume_size)

                use_parallel = (
                    supports_range
                    and remaining_size
                    and remaining_size > self.config.chunk_size
                    and resume_size == 0
                )

                if use_parallel:
                    downloaded = await self.download_parallel_to_fileobj(
                        url=final_url,
                        client=client,
                        output_file=fileobj,
                        total_size=remaining_size,
                        headers=headers,
                        progress_callback=progress.update,
                    )
                else:
                    req_headers = {**(headers or {})}
                    if resume_size > 0:
                        req_headers["Range"] = f"bytes={resume_size}-"

                    downloaded = await self.download_single_stream(
                        url=final_url,
                        client=client,
                        output_file=fileobj,
                        headers=req_headers,
                        progress_callback=progress.update,
                    )
                    downloaded += resume_size

                return downloaded

        finally:
            progress.close()
