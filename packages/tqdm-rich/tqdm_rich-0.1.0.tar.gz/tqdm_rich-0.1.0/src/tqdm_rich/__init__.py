"""
tqdm_rich: A thread-safe tqdm-compatible progress bar library using Rich.

This module provides a tqdm-compatible interface built on top of the Rich library,
offering beautiful terminal progress bars with full support for multi-threading.

Key Features:
    - tqdm-compatible API for easy drop-in replacement
    - Rich-based beautiful progress rendering
    - Thread-safe progress tracking
    - Automatic color indication (white=running, green=success, red=error)
    - Support for both known and unknown total lengths
    - Transient mode for cleaner output

Example:
    >>> from tqdm_rich import tqdm, track
    >>> 
    >>> # Basic tqdm usage
    >>> for item in tqdm(range(100), desc="Processing"):
    ...     time.sleep(0.01)
    >>> 
    >>> # Generator-based tracking
    >>> for item in track(range(100), description="Working"):
    ...     time.sleep(0.01)
"""

import threading
import time
from collections.abc import Generator, Iterable
from typing import Any, Optional, TypeVar, Union

from rich.console import RenderableType
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    Task,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.progress_bar import ProgressBar

__version__ = "0.1.0"
__author__ = "DawnMagnet"
__all__ = ["tqdm", "track", "TqdmRich"]

T = TypeVar("T")

# Color constants for different progress states
_COLOR_RUNNING = "white"
_COLOR_SUCCESS = "green"
_COLOR_ERROR = "red"


class DynamicBarColumn(BarColumn):
    """
    Custom progress bar column that supports dynamic color changes.
    
    This column reads the 'bar_style' field from the task to determine
    the current color of the progress bar, allowing for dynamic recoloring
    based on the task state (running, success, error).
    
    Attributes:
        bar_width: Width of the progress bar (None for auto)
    """

    def render(self, task: Task) -> RenderableType:
        """
        Render the progress bar with dynamically selected color.
        
        Args:
            task: The progress task to render
            
        Returns:
            A ProgressBar renderable with the appropriate styling
        """
        # Get the current task's color status, default to white
        style = task.fields.get("bar_style", _COLOR_RUNNING)

        # Create the progress bar with appropriate styling
        return ProgressBar(
            total=max(0, task.total) if task.total is not None else None,
            completed=max(0, task.completed),
            width=None,
            pulse=task.total is None,
            animation_time=task.get_time(),
            style="bar.back",  # Background color (usually dark gray)
            complete_style=style,  # Color for completed portion
            finished_style=_COLOR_SUCCESS,  # Color at 100% (Rich default behavior)
            pulse_style=style,  # Color of pulse cursor
        )


class _ProgressManager:
    """
    Thread-safe singleton manager for Rich Progress instances.
    
    This manager ensures that only one Progress instance is active at a time,
    coordinating multiple concurrent progress tasks. It uses reference counting
    to determine when to start and stop the underlying Progress instance.
    
    Thread Safety:
        All operations are protected by an RLock to ensure thread safety.
    """

    def __init__(self) -> None:
        """Initialize the progress manager with locking and state tracking."""
        self._lock = threading.RLock()
        self._active_count = 0
        self._progress: Optional[Progress] = None

    def get_progress(self) -> Progress:
        """
        Get or create the global Progress instance.
        
        Thread-safe operation that either returns an existing Progress instance
        or creates a new one with standard columns.
        
        Returns:
            The shared Progress instance
        """
        with self._lock:
            if self._progress is None:
                self._progress = Progress(
                    SpinnerColumn(style=_COLOR_RUNNING),
                    TextColumn("{task.description}", justify="right"),
                    DynamicBarColumn(bar_width=None),
                    TaskProgressColumn(),
                    "•",
                    TimeElapsedColumn(),
                    "•",
                    TimeRemainingColumn(),
                    transient=False,
                )
            return self._progress

    def start_task(self) -> Progress:
        """
        Start a new task, initializing the Progress instance if needed.
        
        Uses reference counting to track active tasks. The Progress instance
        is only started when the first task begins.
        
        Returns:
            The Progress instance
        """
        with self._lock:
            p = self.get_progress()
            if self._active_count == 0:
                p.start()
            self._active_count += 1
            return p

    def stop_task(self) -> None:
        """
        Stop a task and clean up if no more tasks are active.
        
        When the last task stops, the Progress instance is stopped and
        reset for future use.
        """
        with self._lock:
            self._active_count -= 1
            if self._active_count <= 0 and self._progress:
                self._progress.stop()
                self._progress = None
                self._active_count = 0


# Global progress manager instance
_manager = _ProgressManager()


def track(
    sequence: Iterable[T],
    description: str = "Processing",
    total: Optional[int] = None,
    log: Optional[Union[int, float]] = None,
    transient: bool = False,
) -> Generator[T, None, None]:
    """
    A generator-based progress bar that wraps an iterable sequence.
    
    Automatically changes color based on the progress state:
    - White: Running
    - Green: Successfully completed
    - Red: Error or interrupted
    
    Args:
        sequence: An iterable to track
        description: Description text to display (default: "Processing")
        total: Expected number of items (auto-detected if not provided)
        log: Enable logarithmic progress mode. If provided, it sets the
             logarithmic scale factor. When enabled, progress grows
             logarithmically to show activity in long-running operations.
        transient: If True, remove the progress bar after completion
                   (default: False)
    
    Yields:
        Items from the sequence one at a time
        
    Raises:
        Any exception raised during iteration is re-raised after updating
        the progress bar to show error state.
        
    Example:
        >>> for item in track(range(100), description="Processing items"):
        ...     # Do something with item
        ...     pass
    """
    # Determine the total count and mode
    is_log_mode = False
    if total is None:
        if hasattr(sequence, "__len__"):
            total = len(sequence)
        else:
            is_log_mode = True

    # Use logarithmic mode if log parameter is provided
    if log is not None:
        is_log_mode = True
        log_step_factor = float(log)
    elif is_log_mode:
        log_step_factor = 20.0

    # Calculate the total value for the progress bar
    rich_total = 1.0 if is_log_mode else total

    # Start task and get the progress instance
    progress = _manager.start_task()

    # Add the task to the progress bar with initial white styling
    task_id = progress.add_task(
        f"[{_COLOR_RUNNING}]{description}",
        total=rich_total if rich_total else None,
        start=True,
        bar_style=_COLOR_RUNNING,
    )

    success = False
    try:
        current_step = 0
        for item in sequence:
            yield item

            # Update progress bar
            if is_log_mode:
                # Logarithmic progress: approaches 1.0 asymptotically
                current_step += 1
                percentage = 1.0 - (0.2 ** (current_step / log_step_factor))
                progress.update(task_id, completed=min(percentage, 0.99))
            else:
                # Linear progress: increment by 1
                progress.update(task_id, advance=1)

        # Mark successful completion
        success = True

    except Exception as e:
        # Update to error state before re-raising
        progress.update(
            task_id,
            bar_style=_COLOR_ERROR,
            description=f"[{_COLOR_ERROR}]{description}",
        )
        raise

    finally:
        # Final state handling
        if success:
            # Success: turn green and fill the bar
            progress.update(
                task_id,
                bar_style=_COLOR_SUCCESS,
                description=f"[{_COLOR_SUCCESS}]{description}",
                completed=rich_total or 1.0,
            )
        else:
            # Error or interrupted: turn red
            progress.update(
                task_id,
                bar_style=_COLOR_ERROR,
                description=f"[{_COLOR_ERROR}]{description}",
            )

        # Remove the task if transient mode is enabled
        if transient:
            progress.remove_task(task_id)

        _manager.stop_task()


class TqdmRich:
    """
    A tqdm-compatible progress bar class using Rich as the backend.
    
    This class provides an API similar to tqdm.tqdm but uses Rich for rendering,
    offering a more beautiful and feature-rich progress bar experience.
    
    Attributes:
        iterable: The sequence being iterated
        desc: Description of the progress bar
        total: Total number of items (auto-detected if not provided)
        position: Position in the multi-bar display
        leave: Whether to leave the progress bar after completion
        file: Output file (ignored, for tqdm compatibility)
        colour: Color to use (stored but overridden by state-based coloring)
    
    Example:
        >>> bar = TqdmRich(range(100), desc="Processing")
        >>> for item in bar:
        ...     # Do something with item
        ...     time.sleep(0.01)
    """

    def __init__(
        self,
        iterable: Optional[Iterable[T]] = None,
        desc: Optional[str] = None,
        total: Optional[int] = None,
        leave: bool = True,
        file: Any = None,
        ncols: Optional[int] = None,
        mininterval: float = 0.1,
        maxinterval: float = 10.0,
        miniters: Optional[int] = None,
        ascii: bool = False,
        disable: bool = False,
        unit: str = "it",
        unit_scale: bool = False,
        colour: Optional[str] = None,
        position: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a TqdmRich progress bar.
        
        Args:
            iterable: An iterable to wrap (optional)
            desc: Short description of the progress bar
            total: Expected number of items (auto-detected if not provided)
            leave: If True, keep the progress bar after completion
            file: Output file (ignored, for compatibility)
            ncols: Width of the progress bar (ignored, auto-detected)
            mininterval: Minimum update interval (ignored, for compatibility)
            maxinterval: Maximum update interval (ignored, for compatibility)
            miniters: Minimum iterations between updates (ignored)
            ascii: ASCII mode (ignored, for compatibility)
            disable: If True, disable the progress bar
            unit: Unit name (default: "it" for iterations)
            unit_scale: If True, scale large numbers (ignored)
            colour: Color name (overridden by state-based coloring)
            position: Position in multi-bar display (ignored)
            **kwargs: Additional arguments (ignored for compatibility)
        """
        self.iterable = iterable
        self.desc = desc or "Processing"
        self.total = total
        self.leave = leave
        self.disable = disable
        self.unit = unit
        self.colour = colour
        self.position = position or 0
        
        # For compatibility with tqdm
        self.file = file
        self.ncols = ncols
        self.mininterval = mininterval
        self.maxinterval = maxinterval
        self.miniters = miniters
        self.ascii = ascii
        self.unit_scale = unit_scale
        
        # Initialize internal state
        self._iterator: Optional[Generator[T, None, None]] = None
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None
        self._completed = 0

    def __iter__(self) -> "TqdmRich":
        """Start iteration over the wrapped iterable."""
        if self.disable:
            # If disabled, just iterate without progress
            if self.iterable is not None:
                yield from self.iterable
            return self
        
        # Create the iterator
        if self.iterable is None:
            return self
        
        # Determine total
        total = self.total
        if total is None and hasattr(self.iterable, "__len__"):
            total = len(self.iterable)
        
        # Start progress tracking
        self._progress = _manager.start_task()
        self._task_id = self._progress.add_task(
            f"[{_COLOR_RUNNING}]{self.desc}",
            total=total,
            start=True,
            bar_style=_COLOR_RUNNING,
        )
        
        success = False
        try:
            for item in self.iterable:
                self._completed += 1
                yield item
                
                # Update progress
                if self._task_id is not None:
                    self._progress.update(
                        self._task_id,
                        advance=1,
                    )
            
            success = True
        
        except Exception:
            # Update to error state
            if self._task_id is not None:
                self._progress.update(
                    self._task_id,
                    bar_style=_COLOR_ERROR,
                    description=f"[{_COLOR_ERROR}]{self.desc}",
                )
            raise
        
        finally:
            # Final state
            if self._task_id is not None:
                if success:
                    self._progress.update(
                        self._task_id,
                        bar_style=_COLOR_SUCCESS,
                        description=f"[{_COLOR_SUCCESS}]{self.desc}",
                        completed=total or self._completed,
                    )
                else:
                    self._progress.update(
                        self._task_id,
                        bar_style=_COLOR_ERROR,
                        description=f"[{_COLOR_ERROR}]{self.desc}",
                    )
                
                # Remove if not leaving
                if not self.leave:
                    self._progress.remove_task(self._task_id)
            
            _manager.stop_task()

    def __next__(self) -> T:
        """Get the next item from the iterator."""
        if self._iterator is None:
            self._iterator = iter(self)
        return next(self._iterator)

    def update(self, n: int = 1) -> None:
        """
        Update the progress bar.
        
        Args:
            n: Number of items to advance the progress bar by
        """
        if self._task_id is not None and self._progress is not None:
            self._progress.update(self._task_id, advance=n)
            self._completed += n

    def close(self) -> None:
        """Close the progress bar."""
        if self._task_id is not None and self._progress is not None:
            if self.leave:
                self._progress.update(
                    self._task_id,
                    bar_style=_COLOR_SUCCESS,
                    description=f"[{_COLOR_SUCCESS}]{self.desc}",
                )
            else:
                self._progress.remove_task(self._task_id)
            self._task_id = None

    def __enter__(self) -> "TqdmRich":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()


# Create a module-level function alias for tqdm compatibility
def tqdm(
    iterable: Optional[Iterable[T]] = None,
    desc: Optional[str] = None,
    total: Optional[int] = None,
    leave: bool = True,
    **kwargs: Any,
) -> TqdmRich:
    """
    Create a tqdm-compatible progress bar using Rich backend.
    
    This is a convenience function that creates and returns a TqdmRich instance.
    It provides a familiar tqdm API for users migrating from tqdm.
    
    Args:
        iterable: An iterable to wrap
        desc: Short description of the progress bar
        total: Expected number of items (auto-detected if not provided)
        leave: If True, keep the progress bar after completion
        **kwargs: Additional arguments passed to TqdmRich
    
    Returns:
        A TqdmRich instance
        
    Example:
        >>> from tqdm_rich import tqdm
        >>> for item in tqdm(range(100)):
        ...     time.sleep(0.01)
    """
    return TqdmRich(
        iterable=iterable,
        desc=desc,
        total=total,
        leave=leave,
        **kwargs,
    )
