"""
Upload configuration.
"""

from dataclasses import dataclass, field


# Default configuration values
DEFAULT_MAX_WORKERS_PER_FILE = 8  # Parallel parts per file
DEFAULT_MAX_FILE_CONCURRENCY = 4  # Parallel files
DEFAULT_PREFETCH_FACTOR = 4  # Read prefetch_factor * max_workers parts at once
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 5
DEFAULT_BUFFER_SIZE = 64 * 1024  # 64KB read buffer


@dataclass
class UploadConfig:
    """Configuration for upload operations."""

    max_workers_per_file: int = DEFAULT_MAX_WORKERS_PER_FILE
    max_file_concurrency: int = DEFAULT_MAX_FILE_CONCURRENCY
    prefetch_factor: int = DEFAULT_PREFETCH_FACTOR
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    buffer_size: int = DEFAULT_BUFFER_SIZE
    headers: dict[str, str] = field(default_factory=dict)
