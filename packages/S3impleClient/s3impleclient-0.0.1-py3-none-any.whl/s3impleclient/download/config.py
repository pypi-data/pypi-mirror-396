"""
Download configuration.
"""

from dataclasses import dataclass, field


# Default configuration values
DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024  # 4MB per HTTP request (small chunk)
DEFAULT_WRITE_CHUNK_SIZE = 128 * 1024 * 1024  # 128MB per disk write (large chunk)
DEFAULT_MAX_WORKERS = 8  # Number of concurrent download workers
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_BUFFER_SIZE = 64 * 1024  # 64KB read buffer


@dataclass
class DownloadConfig:
    """Configuration for download operations."""

    chunk_size: int = DEFAULT_CHUNK_SIZE  # Small chunk for HTTP requests
    write_chunk_size: int = DEFAULT_WRITE_CHUNK_SIZE  # Large chunk for disk writes
    max_workers: int = DEFAULT_MAX_WORKERS
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    buffer_size: int = DEFAULT_BUFFER_SIZE
    follow_redirects: bool = True
    headers: dict[str, str] = field(default_factory=dict)
