"""
misato.utils - Utility functions and helpers

Contains thread-safe counters, path operations, progress display,
integer splitting, text parsing helpers, and graceful exit handling.

All original behavior is preserved with improved type safety and readability.
"""

from __future__ import annotations

import shutil
import sys
import threading
from pathlib import Path
from typing import List, Tuple, Optional

from misato.config import MAGIC_NUMBER
from misato.logger import logger
from misato.chrome import browser  # Only used for cleanup in exit


class ThreadSafeCounter:
    """
    Thread-safe integer counter for tracking progress across multiple threads.
    """

    def __init__(self) -> None:
        self._count: int = 0
        self._lock = threading.Lock()

    def increment_and_get(self) -> int:
        """Atomically increment and return the new value."""
        with self._lock:
            self._count += 1
            return self._count

    def get(self) -> int:
        """Return current value without incrementing."""
        with self._lock:
            return self._count

    def reset(self) -> None:
        """Reset counter to zero."""
        with self._lock:
            self._count = 0


def split_integer_into_intervals(total: int, parts: int) -> List[Tuple[int, int]]:
    """
    Split an integer into roughly equal intervals for parallel processing.

    Args:
        total: Total number to split (e.g., number of segments)
        parts: Number of intervals (e.g., number of threads)

    Returns:
        List of (start, end) tuples, where end is exclusive
    """
    if parts <= 0:
        raise ValueError("parts must be positive")
    if total == 0:
        return [(0, 0)] * parts

    quotient = total // parts
    remainder = total % parts

    intervals: List[Tuple[int, int]] = []
    start = 0
    for i in range(parts):
        extra = 1 if i < remainder else 0
        end = start + quotient + extra
        intervals.append((start, end))
        start = end

    return intervals


def find_last_non_empty_line(text: str) -> str:
    """
    Find the last non-empty line in a string (used for m3u8 parsing).

    Args:
        text: Input text (typically m3u8 playlist content)

    Returns:
        Last non-empty line

    Raises:
        ValueError: If no non-empty lines found
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("No non-empty lines found in text")
    return lines[-1]


def find_closest(numbers: List[int], target: int) -> int:
    """
    Find the number in list closest to target.

    Args:
        numbers: List of integers
        target: Target value

    Returns:
        Closest number in the list
    """
    if not numbers:
        raise ValueError("numbers list cannot be empty")
    return min(numbers, key=lambda x: abs(x - target))


def delete_all_subfolders(folder_path: Path | str) -> None:
    """
    Delete all subdirectories (but not files) in the given folder.

    Args:
        folder_path: Path to the parent directory
    """
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        return

    for item in path.iterdir():
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
            logger.debug(f"Deleted subfolder: {item}")


def display_progress_bar(max_value: int, file_counter: ThreadSafeCounter) -> None:
    bar_length = 50
    current_value = file_counter.increment_and_get()
    progress = current_value / max_value
    block = int(round(bar_length * progress))
    text = f"\rProgress: [{'#' * block + '-' * (bar_length - block)}] {current_value}/{max_value}"
    sys.stdout.write(text)
    sys.stdout.flush()


def exit_with_cleanup(code: int = MAGIC_NUMBER) -> None:
    """
    Gracefully exit the application with browser cleanup.

    Attempts to close the Playwright browser before exiting.
    Preserves original exit code behavior.
    """
    try:
        if browser and hasattr(browser, "close"):
            browser.close()
            logger.info("Playwright browser closed during exit")
    except Exception as e:
        logger.warning(f"Error closing browser during exit: {e}")
    finally:
        sys.exit(code)

# Backward compatibility
display_progress_bar = display_progress_bar
exit_all = exit_with_cleanup
