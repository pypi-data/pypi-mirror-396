"""
Progress tracking utilities for download/upload operations.
"""

from abc import ABC, abstractmethod
from typing import Callable

from tqdm.auto import tqdm


class ProgressTracker(ABC):
    """Abstract base class for progress tracking."""

    @abstractmethod
    def set_total(self, total: int) -> None:
        """Set the total size in bytes."""
        ...

    @abstractmethod
    def update(self, n: int) -> None:
        """Update progress by n bytes."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the progress tracker."""
        ...


class NoopProgressTracker(ProgressTracker):
    """No-op progress tracker that does nothing."""

    def set_total(self, total: int) -> None:
        pass

    def update(self, n: int) -> None:
        pass

    def close(self) -> None:
        pass


class TqdmProgressTracker(ProgressTracker):
    """Progress tracker using tqdm."""

    PREFIX = "[S3C]"  # Prefix to identify S3impleClient downloads

    def __init__(
        self,
        desc: str | None = None,
        unit: str = "B",
        unit_scale: bool = True,
        unit_divisor: int = 1024,
        miniters: int = 1,
        initial: int = 0,
        total: int | None = None,
        tqdm_class: type[tqdm] | None = None,
        show_prefix: bool = True,
        **kwargs,
    ):
        self._tqdm_class = tqdm_class or tqdm
        # Add prefix to description
        if show_prefix and desc:
            desc = f"{self.PREFIX} {desc}"
        elif show_prefix:
            desc = self.PREFIX
        self._kwargs = {
            "desc": desc,
            "unit": unit,
            "unit_scale": unit_scale,
            "unit_divisor": unit_divisor,
            "miniters": miniters,
            "initial": initial,
            "total": total,
            **kwargs,
        }
        self._bar: tqdm | None = None
        self._create_bar()

    def _create_bar(self) -> None:
        self._bar = self._tqdm_class(**self._kwargs)

    def set_total(self, total: int) -> None:
        if self._bar is not None:
            self._bar.total = total
            self._bar.refresh()

    def update(self, n: int) -> None:
        if self._bar is not None:
            self._bar.update(n)

    def close(self) -> None:
        if self._bar is not None:
            self._bar.close()
            self._bar = None


class CallbackProgressTracker(ProgressTracker):
    """Progress tracker that calls a callback function."""

    def __init__(
        self,
        callback: Callable[[int, int], None],
        total: int = 0,
    ):
        """
        Args:
            callback: Function called with (current_bytes, total_bytes)
            total: Initial total size
        """
        self._callback = callback
        self._total = total
        self._current = 0

    def set_total(self, total: int) -> None:
        self._total = total
        self._callback(self._current, self._total)

    def update(self, n: int) -> None:
        self._current += n
        self._callback(self._current, self._total)

    def close(self) -> None:
        pass


class CompositeProgressTracker(ProgressTracker):
    """Progress tracker that combines multiple trackers."""

    def __init__(self, *trackers: ProgressTracker):
        self._trackers = list(trackers)

    def add(self, tracker: ProgressTracker) -> None:
        self._trackers.append(tracker)

    def set_total(self, total: int) -> None:
        for tracker in self._trackers:
            tracker.set_total(total)

    def update(self, n: int) -> None:
        for tracker in self._trackers:
            tracker.update(n)

    def close(self) -> None:
        for tracker in self._trackers:
            tracker.close()
