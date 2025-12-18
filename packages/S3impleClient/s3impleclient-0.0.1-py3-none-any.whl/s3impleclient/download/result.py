"""
Download result and shard data structures.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ShardInfo:
    """Information about a download shard."""

    index: int
    start: int
    end: int  # inclusive

    @property
    def size(self) -> int:
        return self.end - self.start + 1


@dataclass
class DownloadResult:
    """Result of a download operation."""

    success: bool
    path: Path | None
    total_bytes: int
    error: Exception | None = None
