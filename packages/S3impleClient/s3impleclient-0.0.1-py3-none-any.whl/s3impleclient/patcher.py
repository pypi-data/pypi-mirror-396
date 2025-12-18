"""
Patcher for HuggingFace Hub's download and upload functions.

Replaces the default implementations with S3impleClient's
pipelined parallel operations for faster model downloads/uploads.
"""

import asyncio
import copy
import logging
from math import ceil
from typing import TYPE_CHECKING, Any, BinaryIO

from .download import DownloadConfig, Downloader
from .download.api import run_async as download_run_async
from .progress import TqdmProgressTracker
from .upload import UploadConfig, Uploader
from .upload.api import run_async as upload_run_async

if TYPE_CHECKING:
    from huggingface_hub._commit_api import CommitOperationAdd

logger = logging.getLogger(__name__)


# =============================================================================
# Module State
# =============================================================================

# Download patching state
_original_http_get = None
_is_download_patched = False

# Upload patching state
_original_upload_lfs_files = None
_is_upload_patched = False


# =============================================================================
# Progress Tracker Wrappers
# =============================================================================


class _ExternalBarWrapper:
    """Wraps an external tqdm bar to match our ProgressTracker interface."""

    def __init__(self, bar):
        self._bar = bar

    def set_total(self, total: int) -> None:
        self._bar.total = total
        self._bar.refresh()

    def update(self, n: int) -> None:
        self._bar.update(n)

    def close(self) -> None:
        pass  # Don't close external bar


def _create_progress_tracker(
    displayed_filename: str | None,
    url: str,
    expected_size: int | None,
    resume_size: int,
    tqdm_class: type | None,
    external_bar: Any | None,
):
    """Create appropriate progress tracker for downloads."""
    if external_bar is not None:
        return _ExternalBarWrapper(external_bar)

    desc = displayed_filename or url
    if len(desc) > 40:
        desc = f"(...){desc[-40:]}"

    return TqdmProgressTracker(
        desc=desc,
        total=expected_size,
        initial=resume_size,
        tqdm_class=tqdm_class,
    )


# =============================================================================
# Download Patching
# =============================================================================


def _create_patched_http_get(downloader: Downloader):
    """Create patched http_get function."""

    def patched_http_get(
        url: str,
        temp_file: BinaryIO,
        *,
        resume_size: int = 0,
        headers: dict[str, Any] | None = None,
        expected_size: int | None = None,
        displayed_filename: str | None = None,
        tqdm_class: type | None = None,
        _nb_retries: int = 5,
        _tqdm_bar: Any | None = None,
    ) -> None:
        """Patched http_get using S3impleClient's parallel downloader."""
        if expected_size is not None and resume_size == expected_size:
            return

        req_headers = copy.deepcopy(headers) if headers else {}
        progress = _create_progress_tracker(
            displayed_filename, url, expected_size, resume_size, tqdm_class, _tqdm_bar
        )

        try:
            downloaded = download_run_async(
                downloader.download_to_fileobj_async(
                    url=url,
                    fileobj=temp_file,
                    headers=req_headers,
                    expected_size=expected_size,
                    progress_tracker=progress,
                    resume_size=resume_size,
                )
            )

            if expected_size is not None and downloaded != expected_size:
                raise EnvironmentError(
                    f"Consistency check failed: file should be of size {expected_size} "
                    f"but has size {downloaded} ({displayed_filename or url}).\n"
                    "Please retry with `force_download=True`."
                )
        finally:
            progress.close()

    return patched_http_get


def patch_huggingface_hub(config: DownloadConfig | None = None) -> bool:
    """
    Patch huggingface_hub to use S3impleClient for downloads.

    Args:
        config: Optional download configuration

    Returns:
        True if patched successfully, False if already patched or module not found
    """
    global _original_http_get, _is_download_patched

    if _is_download_patched:
        return False

    try:
        from huggingface_hub import file_download
    except ImportError:
        return False

    _original_http_get = file_download.http_get
    file_download.http_get = _create_patched_http_get(Downloader(config))
    _is_download_patched = True

    return True


def unpatch_huggingface_hub() -> bool:
    """
    Restore original http_get function.

    Returns:
        True if unpatched successfully, False if not patched
    """
    global _original_http_get, _is_download_patched

    if not _is_download_patched or _original_http_get is None:
        return False

    try:
        from huggingface_hub import file_download
    except ImportError:
        return False

    file_download.http_get = _original_http_get
    _original_http_get = None
    _is_download_patched = False

    return True


def is_patched() -> bool:
    """Check if huggingface_hub download is currently patched."""
    return _is_download_patched


# =============================================================================
# Upload Patching
# =============================================================================


def _get_sorted_parts_urls(header: dict, file_size: int, chunk_size: int) -> list[str]:
    """Extract and sort part URLs from LFS batch header."""
    sorted_part_upload_urls = [
        upload_url
        for _, upload_url in sorted(
            [
                (int(part_num, 10), upload_url)
                for part_num, upload_url in header.items()
                if part_num.isdigit() and len(part_num) > 0
            ],
            key=lambda t: t[0],
        )
    ]
    num_parts = len(sorted_part_upload_urls)
    expected_parts = ceil(file_size / chunk_size)
    if num_parts != expected_parts:
        raise ValueError(
            f"Invalid server response: expected {expected_parts} parts, got {num_parts}"
        )
    return sorted_part_upload_urls


async def _upload_single_file_async(
    operation: "CommitOperationAdd",
    lfs_batch_action: dict,
    uploader: Uploader,
    headers: dict[str, str] | None = None,
    endpoint: str | None = None,
) -> None:
    """Upload a single file using our parallel uploader."""
    from huggingface_hub.lfs import (
        LFS_HEADERS,
        _validate_batch_actions,
        _validate_lfs_action,
    )
    from huggingface_hub.utils import (
        build_hf_headers,
        fix_hf_endpoint_in_url,
        hf_raise_for_status,
        get_session,
        logging,
    )

    logger = logging.get_logger(__name__)

    # Validate and check if already uploaded
    _validate_batch_actions(lfs_batch_action)
    actions = lfs_batch_action.get("actions")
    if actions is None:
        logger.debug(
            f"Content of file {operation.path_in_repo} is already present upstream - skipping upload"
        )
        return

    # Get upload action
    upload_action = lfs_batch_action["actions"]["upload"]
    _validate_lfs_action(upload_action)
    verify_action = lfs_batch_action["actions"].get("verify")
    if verify_action is not None:
        _validate_lfs_action(verify_action)

    # Prepare upload
    header = upload_action.get("header", {})
    chunk_size = header.get("chunk_size")
    upload_url = fix_hf_endpoint_in_url(upload_action["href"], endpoint=endpoint)
    file_size = operation.upload_info.size

    # Create progress tracker
    desc = operation.path_in_repo
    if len(desc) > 40:
        desc = f"(...){desc[-40:]}"
    progress = TqdmProgressTracker(desc=desc, total=file_size)

    try:
        import httpx

        timeout = httpx.Timeout(
            uploader.config.timeout, read=uploader.config.timeout * 2
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            if chunk_size is not None:
                # Multipart upload
                try:
                    chunk_size = int(chunk_size)
                except (ValueError, TypeError):
                    raise ValueError(
                        f"Malformed response: chunk_size should be int, got '{chunk_size}'"
                    )

                part_urls = _get_sorted_parts_urls(header, file_size, chunk_size)

                # Get file path
                if isinstance(operation.path_or_fileobj, str):
                    file_path = operation.path_or_fileobj
                else:
                    raise ValueError(
                        "Multipart upload requires file path, not bytes/fileobj"
                    )

                # Upload using our pipelined uploader
                parts = await uploader.upload_multipart_pipelined(
                    part_urls=part_urls,
                    file_path=file_path,
                    chunk_size=chunk_size,
                    client=client,
                    progress_callback=progress.update,
                )

                # Send completion
                completion_payload = {
                    "oid": operation.upload_info.sha256.hex(),
                    "parts": [
                        {"partNumber": p.part_number, "etag": p.etag} for p in parts
                    ],
                }
                completion_res = get_session().post(
                    upload_url,
                    json=completion_payload,
                    headers=LFS_HEADERS,
                )
                hf_raise_for_status(completion_res)

            else:
                # Single part upload
                with operation.as_file(with_tqdm=False) as fileobj:
                    content = fileobj.read()

                response = await client.put(upload_url, content=content)
                response.raise_for_status()
                progress.update(len(content))

    finally:
        progress.close()

    # Verify upload
    if verify_action is not None:
        verify_url = fix_hf_endpoint_in_url(verify_action["href"], endpoint)
        verify_resp = get_session().post(
            verify_url,
            headers=build_hf_headers(headers=headers),
            json={
                "oid": operation.upload_info.sha256.hex(),
                "size": operation.upload_info.size,
            },
        )
        hf_raise_for_status(verify_resp)

    logger.debug(f"{operation.path_in_repo}: Upload successful")


def _create_patched_upload_lfs_files(uploader: Uploader):
    """Create patched _upload_lfs_files function."""

    def patched_upload_lfs_files(
        *,
        actions: list[dict[str, Any]],
        oid2addop: dict[str, "CommitOperationAdd"],
        headers: dict[str, str],
        endpoint: str | None = None,
        num_threads: int = 5,  # Ignored, we use our own concurrency
    ) -> None:
        """
        Patched _upload_lfs_files using S3impleClient's parallel uploader.

        Uploads multiple files concurrently with parallel multipart uploads.
        """
        from huggingface_hub.utils import logging

        logger = logging.get_logger(__name__)

        # Filter out files already present upstream
        filtered_actions = []
        for action in actions:
            if action.get("actions") is None:
                logger.debug(
                    f"Content of file {oid2addop[action['oid']].path_in_repo} "
                    "is already present upstream - skipping upload."
                )
            else:
                filtered_actions.append(action)

        if not filtered_actions:
            return

        logger.debug(
            f"Uploading {len(filtered_actions)} LFS files using S3impleClient "
            f"(max {uploader.config.max_file_concurrency} files, "
            f"{uploader.config.max_workers_per_file} workers/file)"
        )

        async def upload_all():
            semaphore = asyncio.Semaphore(uploader.config.max_file_concurrency)

            async def upload_one(batch_action: dict) -> None:
                async with semaphore:
                    operation = oid2addop[batch_action["oid"]]
                    try:
                        await _upload_single_file_async(
                            operation=operation,
                            lfs_batch_action=batch_action,
                            uploader=uploader,
                            headers=headers,
                            endpoint=endpoint,
                        )
                    except Exception as exc:
                        raise RuntimeError(
                            f"Error while uploading '{operation.path_in_repo}' to the Hub."
                        ) from exc

            tasks = [
                asyncio.create_task(upload_one(action)) for action in filtered_actions
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Raise first error if any
            for result in results:
                if isinstance(result, Exception):
                    raise result

        upload_run_async(upload_all())

    return patched_upload_lfs_files


def patch_huggingface_hub_upload(config: UploadConfig | None = None) -> bool:
    """
    Patch huggingface_hub to use S3impleClient for uploads.

    Args:
        config: Optional upload configuration

    Returns:
        True if patched successfully, False if already patched or module not found
    """
    global _original_upload_lfs_files, _is_upload_patched

    if _is_upload_patched:
        return False

    try:
        from huggingface_hub import _commit_api
    except ImportError:
        return False

    config = config or UploadConfig()
    uploader = Uploader(config)

    logger.info(
        f"Patching HF upload: max_workers_per_file={config.max_workers_per_file}, "
        f"max_file_concurrency={config.max_file_concurrency}, "
        f"prefetch_factor={config.prefetch_factor}"
    )

    _original_upload_lfs_files = _commit_api._upload_lfs_files
    _commit_api._upload_lfs_files = _create_patched_upload_lfs_files(uploader)
    _is_upload_patched = True

    return True


def unpatch_huggingface_hub_upload() -> bool:
    """
    Restore original _upload_lfs_files function.

    Returns:
        True if unpatched successfully, False if not patched
    """
    global _original_upload_lfs_files, _is_upload_patched

    if not _is_upload_patched or _original_upload_lfs_files is None:
        return False

    try:
        from huggingface_hub import _commit_api
    except ImportError:
        return False

    _commit_api._upload_lfs_files = _original_upload_lfs_files
    _original_upload_lfs_files = None
    _is_upload_patched = False

    return True


def is_upload_patched() -> bool:
    """Check if huggingface_hub upload is currently patched."""
    return _is_upload_patched


# =============================================================================
# Combined Patching
# =============================================================================


def patch_all(
    download_config: DownloadConfig | None = None,
    upload_config: UploadConfig | None = None,
) -> tuple[bool, bool]:
    """
    Patch both download and upload in huggingface_hub.

    Args:
        download_config: Optional download configuration
        upload_config: Optional upload configuration

    Returns:
        Tuple of (download_patched, upload_patched)
    """
    download_patched = patch_huggingface_hub(download_config)
    upload_patched = patch_huggingface_hub_upload(upload_config)
    return download_patched, upload_patched


def unpatch_all() -> tuple[bool, bool]:
    """
    Restore both download and upload in huggingface_hub.

    Returns:
        Tuple of (download_unpatched, upload_unpatched)
    """
    download_unpatched = unpatch_huggingface_hub()
    upload_unpatched = unpatch_huggingface_hub_upload()
    return download_unpatched, upload_unpatched


# =============================================================================
# Logging Configuration
# =============================================================================


def configure_logging(level: int = logging.WARNING) -> None:
    """
    Configure S3impleClient logging.

    Args:
        level: Logging level (default: WARNING, use INFO or DEBUG for more details)

    Example:
        >>> import s3impleclient as s3c
        >>> import logging
        >>> s3c.configure_logging(logging.INFO)  # See upload/download config
        >>> s3c.configure_logging(logging.DEBUG)  # See per-chunk progress
    """
    # Configure s3impleclient loggers
    for name in [
        "s3impleclient.upload.core",
        "s3impleclient.download.core",
        "s3impleclient.patcher",
    ]:
        log = logging.getLogger(name)
        log.setLevel(level)

        # Add handler if none exists
        if not log.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("[S3C] %(levelname)s - %(message)s"))
            log.addHandler(handler)


# Configure default logging (WARNING level, so users see important warnings)
configure_logging(logging.WARNING)
