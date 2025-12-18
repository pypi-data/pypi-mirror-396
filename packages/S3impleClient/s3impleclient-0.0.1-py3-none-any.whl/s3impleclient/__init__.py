"""
S3impleClient - A simple, fast, and robust async S3/HTTP downloader/uploader.
"""

from .download import (
    DownloadConfig,
    DownloadResult,
    Downloader,
    configure as configure_download,
    download,
    download_async,
)
from .patcher import (
    configure_logging,
    is_patched,
    is_upload_patched,
    patch_all,
    patch_huggingface_hub,
    patch_huggingface_hub_upload,
    unpatch_all,
    unpatch_huggingface_hub,
    unpatch_huggingface_hub_upload,
)
from .progress import (
    CallbackProgressTracker,
    NoopProgressTracker,
    ProgressTracker,
    TqdmProgressTracker,
)
from .upload import (
    MultiFileUploadResult,
    UploadConfig,
    UploadResult,
    Uploader,
    configure as configure_upload,
    upload,
    upload_async,
    upload_files,
    upload_files_async,
)

__version__ = "0.1.0"

__all__ = [
    # Download API
    "download",
    "download_async",
    "configure_download",
    "Downloader",
    "DownloadConfig",
    "DownloadResult",
    # Upload API
    "upload",
    "upload_async",
    "upload_files",
    "upload_files_async",
    "configure_upload",
    "Uploader",
    "UploadConfig",
    "UploadResult",
    "MultiFileUploadResult",
    # Patcher - Download
    "patch_huggingface_hub",
    "unpatch_huggingface_hub",
    "is_patched",
    # Patcher - Upload
    "patch_huggingface_hub_upload",
    "unpatch_huggingface_hub_upload",
    "is_upload_patched",
    # Patcher - Combined
    "patch_all",
    "unpatch_all",
    # Logging
    "configure_logging",
    # Progress
    "ProgressTracker",
    "TqdmProgressTracker",
    "NoopProgressTracker",
    "CallbackProgressTracker",
]
