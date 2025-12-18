"""
Async-based upload module with parallel multipart uploads.
"""

from .api import (
    configure,
    get_default_uploader,
    run_async,
    upload,
    upload_async,
    upload_files,
    upload_files_async,
)
from .config import UploadConfig
from .core import Uploader
from .result import MultiFileUploadResult, PartResult, UploadResult

__all__ = [
    "UploadConfig",
    "UploadResult",
    "PartResult",
    "MultiFileUploadResult",
    "Uploader",
    "upload",
    "upload_async",
    "upload_files",
    "upload_files_async",
    "configure",
    "get_default_uploader",
    "run_async",
]
