"""
Core async uploader with pipelined parallel multipart uploads.

Architecture:
- Large chunks (max_workers * part_size * prefetch_factor) for disk reads
- Parts uploaded in parallel within each large chunk (max_workers at a time)
- Pipeline: upload large chunk N while reading large chunk N+1
"""

import asyncio
import logging
from pathlib import Path
from typing import BinaryIO, Callable

import aiofiles
import httpx

from ..progress import NoopProgressTracker, ProgressTracker
from .config import UploadConfig
from .result import MultiFileUploadResult, PartResult, UploadResult

logger = logging.getLogger(__name__)


class Uploader:
    """
    Async HTTP/S3 uploader with pipelined parallel uploads.

    Pipeline approach (mirror of download):
    1. Read large chunk from disk (max_workers * part_size bytes)
    2. Upload all parts within that chunk in parallel
    3. While uploading, read next large chunk
    4. Overlap I/O for maximum throughput
    """

    def __init__(self, config: UploadConfig | None = None):
        self.config = config or UploadConfig()

    # -------------------------------------------------------------------------
    # Single Part Upload
    # -------------------------------------------------------------------------

    async def upload_single_part(
        self,
        url: str,
        file_path: Path | str,
        client: httpx.AsyncClient,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> UploadResult:
        """Upload entire file as single PUT request."""
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        req_headers = {**self.config.headers, **(headers or {})}

        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await client.put(
                    url,
                    content=content,
                    headers=req_headers,
                )
                response.raise_for_status()

                if progress_callback:
                    progress_callback(file_size)

                etag = response.headers.get("etag", "").strip('"')
                return UploadResult(
                    success=True,
                    path=file_path,
                    total_bytes=file_size,
                    parts=[PartResult(part_number=1, etag=etag, size=file_size)],
                )

            except (httpx.HTTPError, httpx.StreamError) as e:
                last_error = e
                if attempt < self.config.max_retries:
                    await asyncio.sleep(min(2**attempt, 30))

        return UploadResult(
            success=False,
            path=file_path,
            total_bytes=0,
            error=last_error,
        )

    # -------------------------------------------------------------------------
    # Part Upload
    # -------------------------------------------------------------------------

    async def upload_part(
        self,
        url: str,
        part_number: int,
        data: bytes,
        client: httpx.AsyncClient,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> PartResult:
        """Upload a single part with retry."""
        req_headers = {**self.config.headers, **(headers or {})}
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries + 1):
            try:
                response = await client.put(
                    url,
                    content=data,
                    headers=req_headers,
                )
                response.raise_for_status()

                if progress_callback:
                    progress_callback(len(data))

                etag = response.headers.get("etag", "").strip('"')
                if not etag:
                    raise ValueError(f"Part {part_number}: server did not return ETag")

                return PartResult(
                    part_number=part_number,
                    etag=etag,
                    size=len(data),
                )

            except (httpx.HTTPError, httpx.StreamError, ValueError) as e:
                last_error = e
                if attempt < self.config.max_retries:
                    await asyncio.sleep(min(2**attempt, 30))

        raise last_error or RuntimeError(f"Failed to upload part {part_number}")

    # -------------------------------------------------------------------------
    # Large Chunk Upload (parallel parts with semaphore)
    # -------------------------------------------------------------------------

    async def upload_large_chunk(
        self,
        part_urls: list[str],
        part_data: list[bytes],
        start_part_number: int,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> list[PartResult]:
        """Upload multiple parts in parallel, limited by semaphore."""

        async def upload_with_semaphore(idx: int) -> PartResult:
            async with semaphore:
                return await self.upload_part(
                    url=part_urls[idx],
                    part_number=start_part_number + idx,
                    data=part_data[idx],
                    client=client,
                    headers=headers,
                    progress_callback=progress_callback,
                )

        tasks = [
            asyncio.create_task(upload_with_semaphore(i)) for i in range(len(part_data))
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        part_results: list[PartResult] = []
        for result in results:
            if isinstance(result, Exception):
                raise result
            part_results.append(result)

        return part_results

    # -------------------------------------------------------------------------
    # Pipelined Multipart Upload
    # -------------------------------------------------------------------------

    async def upload_multipart_pipelined(
        self,
        part_urls: list[str],
        file_path: Path | str,
        chunk_size: int,
        client: httpx.AsyncClient,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> list[PartResult]:
        """
        Upload file with pipeline: upload large chunk N while reading large chunk N+1.

        Large chunk = max_workers * prefetch_factor * part_size bytes
        Within each large chunk, parts upload in parallel (limited by max_workers).
        """
        file_path = Path(file_path)
        file_size = file_path.stat().st_size
        num_parts = len(part_urls)

        # Calculate parts per large chunk
        parts_per_chunk = self.config.max_workers_per_file * self.config.prefetch_factor
        large_chunk_size = parts_per_chunk * chunk_size
        semaphore = asyncio.Semaphore(self.config.max_workers_per_file)

        logger.info(
            f"Upload config: file_size={file_size / 1024 / 1024:.1f}MB, "
            f"num_parts={num_parts}, part_size={chunk_size / 1024 / 1024:.1f}MB, "
            f"parts_per_chunk={parts_per_chunk}, "
            f"large_chunk_size={large_chunk_size / 1024 / 1024:.1f}MB, "
            f"max_workers={self.config.max_workers_per_file}"
        )

        all_results: list[PartResult] = []

        async with aiofiles.open(file_path, "rb") as f:
            part_idx = 0

            # Read first large chunk (multiple parts)
            current_parts_data: list[bytes] = []
            for _ in range(min(parts_per_chunk, num_parts - part_idx)):
                data = await f.read(chunk_size)
                if data:
                    current_parts_data.append(data)

            logger.debug(f"Read first chunk: {len(current_parts_data)} parts")

            # Pipeline: upload current large chunk while reading next
            while part_idx < num_parts and current_parts_data:
                num_current_parts = len(current_parts_data)
                current_urls = part_urls[part_idx : part_idx + num_current_parts]

                # Check if there are more parts to read
                next_part_idx = part_idx + num_current_parts
                has_more = next_part_idx < num_parts

                if has_more:
                    # Start reading next large chunk while uploading current
                    async def read_next_chunk():
                        parts_data: list[bytes] = []
                        for _ in range(min(parts_per_chunk, num_parts - next_part_idx)):
                            data = await f.read(chunk_size)
                            if data:
                                parts_data.append(data)
                        return parts_data

                    read_task = asyncio.create_task(read_next_chunk())

                    # Upload current large chunk (parts in parallel, limited by semaphore)
                    logger.debug(
                        f"Uploading parts {part_idx + 1}-{part_idx + num_current_parts} "
                        f"while reading next chunk"
                    )
                    results = await self.upload_large_chunk(
                        part_urls=current_urls,
                        part_data=current_parts_data,
                        start_part_number=part_idx + 1,  # 1-indexed
                        client=client,
                        semaphore=semaphore,
                        headers=headers,
                        progress_callback=progress_callback,
                    )
                    all_results.extend(results)

                    # Get next chunk data
                    current_parts_data = await read_task
                else:
                    # Last chunk - just upload
                    logger.debug(
                        f"Uploading final parts {part_idx + 1}-{part_idx + num_current_parts}"
                    )
                    results = await self.upload_large_chunk(
                        part_urls=current_urls,
                        part_data=current_parts_data,
                        start_part_number=part_idx + 1,
                        client=client,
                        semaphore=semaphore,
                        headers=headers,
                        progress_callback=progress_callback,
                    )
                    all_results.extend(results)
                    current_parts_data = []

                part_idx += num_current_parts

        logger.info(f"Upload complete: {len(all_results)} parts uploaded")

        # Sort by part number
        all_results.sort(key=lambda r: r.part_number)
        return all_results

    # -------------------------------------------------------------------------
    # Public API: Upload File
    # -------------------------------------------------------------------------

    async def upload_file_async(
        self,
        file_path: Path | str,
        upload_url: str | None = None,
        part_urls: list[str] | None = None,
        chunk_size: int | None = None,
        completion_url: str | None = None,
        headers: dict[str, str] | None = None,
        progress_tracker: ProgressTracker | None = None,
    ) -> UploadResult:
        """
        Upload a file using single or multipart upload.

        Args:
            file_path: Path to file to upload
            upload_url: URL for single-part upload
            part_urls: List of pre-signed URLs for multipart upload
            chunk_size: Size of each part (required for multipart)
            completion_url: URL to POST completion (optional)
            headers: Additional headers
            progress_tracker: Progress tracker

        Returns:
            UploadResult with success status and ETags
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return UploadResult(
                success=False,
                path=file_path,
                total_bytes=0,
                error=FileNotFoundError(f"File not found: {file_path}"),
            )

        file_size = file_path.stat().st_size
        progress = progress_tracker or NoopProgressTracker()
        progress.set_total(file_size)

        try:
            timeout = httpx.Timeout(self.config.timeout, read=self.config.timeout * 2)
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Single part upload
                if upload_url and not part_urls:
                    return await self.upload_single_part(
                        url=upload_url,
                        file_path=file_path,
                        client=client,
                        headers=headers,
                        progress_callback=progress.update,
                    )

                # Multipart upload
                if part_urls and chunk_size:
                    parts = await self.upload_multipart_pipelined(
                        part_urls=part_urls,
                        file_path=file_path,
                        chunk_size=chunk_size,
                        client=client,
                        headers=headers,
                        progress_callback=progress.update,
                    )

                    # Send completion request if URL provided
                    if completion_url:
                        await self._send_completion(
                            client=client,
                            completion_url=completion_url,
                            parts=parts,
                            headers=headers,
                        )

                    return UploadResult(
                        success=True,
                        path=file_path,
                        total_bytes=file_size,
                        parts=parts,
                    )

                raise ValueError(
                    "Must provide either upload_url (single) or part_urls + chunk_size (multipart)"
                )

        except Exception as e:
            return UploadResult(
                success=False,
                path=file_path,
                total_bytes=0,
                error=e,
            )
        finally:
            progress.close()

    async def _send_completion(
        self,
        client: httpx.AsyncClient,
        completion_url: str,
        parts: list[PartResult],
        headers: dict[str, str] | None = None,
    ) -> None:
        """Send multipart completion request."""
        payload = {
            "parts": [
                {"partNumber": p.part_number, "etag": p.etag}
                for p in sorted(parts, key=lambda x: x.part_number)
            ]
        }

        req_headers = {
            **self.config.headers,
            **(headers or {}),
            "Content-Type": "application/json",
        }

        response = await client.post(
            completion_url,
            json=payload,
            headers=req_headers,
        )
        response.raise_for_status()

    # -------------------------------------------------------------------------
    # Public API: Upload Multiple Files
    # -------------------------------------------------------------------------

    async def upload_files_async(
        self,
        files: list[dict],
        headers: dict[str, str] | None = None,
        progress_tracker: ProgressTracker | None = None,
    ) -> MultiFileUploadResult:
        """
        Upload multiple files concurrently.

        Args:
            files: List of dicts with keys:
                - file_path: Path to file
                - upload_url: URL for single-part (optional)
                - part_urls: List of URLs for multipart (optional)
                - chunk_size: Part size for multipart (optional)
                - completion_url: Completion URL (optional)
            headers: Additional headers for all uploads
            progress_tracker: Progress tracker for total progress

        Returns:
            MultiFileUploadResult with individual results
        """
        progress = progress_tracker or NoopProgressTracker()

        # Calculate total size
        total_size = 0
        for f in files:
            path = Path(f["file_path"])
            if path.exists():
                total_size += path.stat().st_size
        progress.set_total(total_size)

        # Semaphore for file concurrency
        file_semaphore = asyncio.Semaphore(self.config.max_file_concurrency)

        async def upload_one(file_info: dict) -> UploadResult:
            async with file_semaphore:
                return await self.upload_file_async(
                    file_path=file_info["file_path"],
                    upload_url=file_info.get("upload_url"),
                    part_urls=file_info.get("part_urls"),
                    chunk_size=file_info.get("chunk_size"),
                    completion_url=file_info.get("completion_url"),
                    headers=headers,
                    progress_tracker=None,
                )

        async def upload_with_progress(file_info: dict) -> UploadResult:
            result = await upload_one(file_info)
            if result.success:
                progress.update(result.total_bytes)
            return result

        tasks = [asyncio.create_task(upload_with_progress(f)) for f in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_results: list[UploadResult] = []
        failed: list[tuple[Path | str, Exception]] = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed.append((files[i]["file_path"], result))
            elif result.success:
                success_results.append(result)
            else:
                failed.append(
                    (
                        result.path or files[i]["file_path"],
                        result.error or RuntimeError("Unknown error"),
                    )
                )

        progress.close()

        return MultiFileUploadResult(
            success=len(failed) == 0,
            results=success_results,
            failed=failed,
        )

    # -------------------------------------------------------------------------
    # Upload from File Object (for HF patcher)
    # -------------------------------------------------------------------------

    async def upload_fileobj_async(
        self,
        fileobj: BinaryIO,
        upload_url: str | None = None,
        part_urls: list[str] | None = None,
        chunk_size: int | None = None,
        headers: dict[str, str] | None = None,
        progress_callback: Callable[[int], None] | None = None,
    ) -> list[PartResult]:
        """
        Upload from file object (for HF patcher integration).
        """
        timeout = httpx.Timeout(self.config.timeout, read=self.config.timeout * 2)

        async with httpx.AsyncClient(timeout=timeout) as client:
            # Single part
            if upload_url and not part_urls:
                content = fileobj.read()
                req_headers = {**self.config.headers, **(headers or {})}

                response = await client.put(
                    upload_url, content=content, headers=req_headers
                )
                response.raise_for_status()

                if progress_callback:
                    progress_callback(len(content))

                etag = response.headers.get("etag", "").strip('"')
                return [PartResult(part_number=1, etag=etag, size=len(content))]

            # Multipart - read and upload in parallel batches
            if part_urls and chunk_size:
                num_parts = len(part_urls)
                parts_per_chunk = (
                    self.config.max_workers_per_file * self.config.prefetch_factor
                )
                semaphore = asyncio.Semaphore(self.config.max_workers_per_file)
                all_results: list[PartResult] = []
                part_idx = 0

                logger.info(
                    f"Fileobj upload: num_parts={num_parts}, "
                    f"parts_per_chunk={parts_per_chunk}, "
                    f"max_workers={self.config.max_workers_per_file}"
                )

                while part_idx < num_parts:
                    # Read batch of parts
                    batch_data: list[bytes] = []
                    batch_urls: list[str] = []

                    for _ in range(min(parts_per_chunk, num_parts - part_idx)):
                        data = fileobj.read(chunk_size)
                        if not data:
                            break
                        batch_data.append(data)
                        batch_urls.append(part_urls[part_idx + len(batch_data) - 1])

                    if not batch_data:
                        break

                    # Upload batch in parallel
                    logger.debug(
                        f"Uploading parts {part_idx + 1}-{part_idx + len(batch_data)}"
                    )
                    results = await self.upload_large_chunk(
                        part_urls=batch_urls,
                        part_data=batch_data,
                        start_part_number=part_idx + 1,
                        client=client,
                        semaphore=semaphore,
                        headers=headers,
                        progress_callback=progress_callback,
                    )
                    all_results.extend(results)
                    part_idx += len(batch_data)

                all_results.sort(key=lambda r: r.part_number)
                return all_results

            raise ValueError(
                "Must provide either upload_url (single) or part_urls + chunk_size (multipart)"
            )
