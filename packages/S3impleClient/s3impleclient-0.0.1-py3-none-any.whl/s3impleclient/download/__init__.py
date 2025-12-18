"""
Async-based download module with parallel range requests.
"""

from .config import DownloadConfig
from .core import Downloader
from .result import DownloadResult, ShardInfo
from .api import download, download_async, configure, get_default_downloader, run_async

__all__ = [
    "DownloadConfig",
    "DownloadResult",
    "ShardInfo",
    "Downloader",
    "download",
    "download_async",
    "configure",
    "get_default_downloader",
    "run_async",
]
