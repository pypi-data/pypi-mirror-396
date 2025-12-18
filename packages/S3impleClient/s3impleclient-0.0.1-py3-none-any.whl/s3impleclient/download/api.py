"""
Public API for download operations with sync/async support.
"""

import asyncio
import sys
from pathlib import Path

from ..progress import ProgressTracker, TqdmProgressTracker, NoopProgressTracker
from .config import DownloadConfig
from .core import Downloader
from .result import DownloadResult


# Module-level default downloader
_default_downloader: Downloader | None = None


def get_default_downloader() -> Downloader:
    """Get or create the default downloader instance."""
    global _default_downloader
    if _default_downloader is None:
        _default_downloader = Downloader()
    return _default_downloader


def configure(config: DownloadConfig) -> None:
    """Configure the default downloader."""
    global _default_downloader
    _default_downloader = Downloader(config)


async def download_async(
    url: str,
    dest: Path | str,
    headers: dict[str, str] | None = None,
    expected_size: int | None = None,
    show_progress: bool = True,
    progress_desc: str | None = None,
) -> DownloadResult:
    """
    Download URL to file asynchronously.

    Args:
        url: URL to download
        dest: Destination file path
        headers: Additional HTTP headers
        expected_size: Expected file size for validation
        show_progress: Whether to show progress bar
        progress_desc: Description for progress bar

    Returns:
        DownloadResult with success status
    """
    downloader = get_default_downloader()

    progress: ProgressTracker
    if show_progress:
        progress = TqdmProgressTracker(desc=progress_desc)
    else:
        progress = NoopProgressTracker()

    return await downloader.download_to_file_async(
        url=url,
        dest=dest,
        headers=headers,
        expected_size=expected_size,
        progress_tracker=progress,
    )


def download(
    url: str,
    dest: Path | str,
    headers: dict[str, str] | None = None,
    expected_size: int | None = None,
    show_progress: bool = True,
    progress_desc: str | None = None,
) -> DownloadResult:
    """
    Download URL to file synchronously.

    This is a sync wrapper around download_async that properly manages
    the event loop.

    Args:
        url: URL to download
        dest: Destination file path
        headers: Additional HTTP headers
        expected_size: Expected file size for validation
        show_progress: Whether to show progress bar
        progress_desc: Description for progress bar

    Returns:
        DownloadResult with success status
    """
    return run_async(
        download_async(
            url=url,
            dest=dest,
            headers=headers,
            expected_size=expected_size,
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
        # On Windows, ensure proper event loop policy
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return asyncio.run(coro)
    else:
        # Already in an async context (e.g., Jupyter, async framework)
        # Try nest_asyncio first
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
