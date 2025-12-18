"""
Upload result data structures.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PartResult:
    """Result of uploading a single part."""

    part_number: int
    etag: str
    size: int


@dataclass
class UploadResult:
    """Result of an upload operation."""

    success: bool
    path: Path | str | None
    total_bytes: int
    parts: list[PartResult] = field(default_factory=list)
    error: Exception | None = None


@dataclass
class MultiFileUploadResult:
    """Result of uploading multiple files."""

    success: bool
    results: list[UploadResult] = field(default_factory=list)
    failed: list[tuple[Path | str, Exception]] = field(default_factory=list)

    @property
    def total_bytes(self) -> int:
        return sum(r.total_bytes for r in self.results)
