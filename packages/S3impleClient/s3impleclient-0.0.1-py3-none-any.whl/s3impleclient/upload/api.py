"""
Public API for upload operations with sync/async support.
"""

import asyncio
import sys
from pathlib import Path

from ..progress import NoopProgressTracker, ProgressTracker, TqdmProgressTracker
from .config import UploadConfig
from .core import Uploader
from .result import MultiFileUploadResult, UploadResult


# Module-level default uploader
_default_uploader: Uploader | None = None


def get_default_uploader() -> Uploader:
    """Get or create the default uploader instance."""
    global _default_uploader
    if _default_uploader is None:
        _default_uploader = Uploader()
    return _default_uploader


def configure(config: UploadConfig) -> None:
    """Configure the default uploader."""
    global _default_uploader
    _default_uploader = Uploader(config)


async def upload_async(
    file_path: Path | str,
    upload_url: str | None = None,
    part_urls: list[str] | None = None,
    chunk_size: int | None = None,
    completion_url: str | None = None,
    headers: dict[str, str] | None = None,
    show_progress: bool = True,
    progress_desc: str | None = None,
) -> UploadResult:
    """
    Upload a file asynchronously.

    Args:
        file_path: Path to file to upload
        upload_url: URL for single-part upload
        part_urls: List of pre-signed URLs for multipart
        chunk_size: Size of each part (required for multipart)
        completion_url: URL to POST completion (optional)
        headers: Additional HTTP headers
        show_progress: Whether to show progress bar
        progress_desc: Description for progress bar

    Returns:
        UploadResult with success status
    """
    uploader = get_default_uploader()

    progress: ProgressTracker
    if show_progress:
        progress = TqdmProgressTracker(desc=progress_desc)
    else:
        progress = NoopProgressTracker()

    return await uploader.upload_file_async(
        file_path=file_path,
        upload_url=upload_url,
        part_urls=part_urls,
        chunk_size=chunk_size,
        completion_url=completion_url,
        headers=headers,
        progress_tracker=progress,
    )


def upload(
    file_path: Path | str,
    upload_url: str | None = None,
    part_urls: list[str] | None = None,
    chunk_size: int | None = None,
    completion_url: str | None = None,
    headers: dict[str, str] | None = None,
    show_progress: bool = True,
    progress_desc: str | None = None,
) -> UploadResult:
    """
    Upload a file synchronously.

    Args:
        file_path: Path to file to upload
        upload_url: URL for single-part upload
        part_urls: List of pre-signed URLs for multipart
        chunk_size: Size of each part (required for multipart)
        completion_url: URL to POST completion (optional)
        headers: Additional HTTP headers
        show_progress: Whether to show progress bar
        progress_desc: Description for progress bar

    Returns:
        UploadResult with success status
    """
    return run_async(
        upload_async(
            file_path=file_path,
            upload_url=upload_url,
            part_urls=part_urls,
            chunk_size=chunk_size,
            completion_url=completion_url,
            headers=headers,
            show_progress=show_progress,
            progress_desc=progress_desc,
        )
    )


async def upload_files_async(
    files: list[dict],
    headers: dict[str, str] | None = None,
    show_progress: bool = True,
    progress_desc: str | None = None,
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
        show_progress: Whether to show progress bar
        progress_desc: Description for progress bar

    Returns:
        MultiFileUploadResult with individual results
    """
    uploader = get_default_uploader()

    progress: ProgressTracker
    if show_progress:
        progress = TqdmProgressTracker(desc=progress_desc or "Uploading")
    else:
        progress = NoopProgressTracker()

    return await uploader.upload_files_async(
        files=files,
        headers=headers,
        progress_tracker=progress,
    )


def upload_files(
    files: list[dict],
    headers: dict[str, str] | None = None,
    show_progress: bool = True,
    progress_desc: str | None = None,
) -> MultiFileUploadResult:
    """
    Upload multiple files synchronously.

    Args:
        files: List of dicts with keys:
            - file_path: Path to file
            - upload_url: URL for single-part (optional)
            - part_urls: List of URLs for multipart (optional)
            - chunk_size: Part size for multipart (optional)
            - completion_url: Completion URL (optional)
        headers: Additional headers for all uploads
        show_progress: Whether to show progress bar
        progress_desc: Description for progress bar

    Returns:
        MultiFileUploadResult with individual results
    """
    return run_async(
        upload_files_async(
            files=files,
            headers=headers,
            show_progress=show_progress,
            progress_desc=progress_desc,
        )
    )


def run_async(coro):
    """
    Run async coroutine in sync context with proper event loop management.

    Handles three cases:
    1. No running loop: use asyncio.run()
    2. Running loop (e.g., Jupyter): use nest_asyncio or run in thread
    3. Windows: use WindowsSelectorEventLoopPolicy for compatibility
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        # No running loop - safe to use asyncio.run()
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return asyncio.run(coro)
    else:
        # Already in an async context (e.g., Jupyter, async framework)
        try:
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(coro)
        except ImportError:
            pass

        # Fallback: run in a separate thread with its own loop
        import concurrent.futures

        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(run_in_thread)
            return future.result()
