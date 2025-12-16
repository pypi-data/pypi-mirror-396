# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import logging
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

import yumako

log = logging.getLogger(__name__)


class DaemonTask(ABC):
    """
    Base class for periodic daemon tasks.
    Handles thread management, start/stop lifecycle, and interval-based execution.
    """

    def __init__(self, name: str, interval: str, run_immediately: bool = False):
        """
        Initialize the daemon task.

        Args:
            name: Name of the daemon task (used for thread naming and logging)
            interval: Execution interval as a string, e.g. "2m", "24h", "1d4h"
            run_immediately: If True, execute immediately on start; if False, wait for interval first
        """
        self.name = name
        self.interval = interval
        self._interval_seconds = yumako.time.duration(interval)
        self.run_immediately = run_immediately
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_execution_time: Optional[float] = None

    def start(self) -> None:
        """Start the daemon task."""
        if self._running:
            log.warning(f"Daemon task '{self.name}' is already running")
            return

        self._running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name=self.name, daemon=True)
        self._thread.start()
        log.info(f"Daemon '{self.name}' started (interval: {self.interval})")

    def stop(self) -> None:
        """Stop the daemon task."""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None
        log.info(f"Daemon '{self.name}' stopped")

    def _run_loop(self) -> None:
        """Main loop for periodic task execution."""

        log.info(f"Daemon '{self.name}' loop start (interval: {self.interval})")

        # Execute immediately if configured to do so
        if self.run_immediately:
            try:
                self.execute()
                self._last_execution_time = time.time()
            except Exception as e:
                log.error(f"Error in daemon task '{self.name}': {e}")

        while self._running:
            # Wait for the interval
            self._stop_event.wait(timeout=self._interval_seconds)

            if not self._running:
                break

            try:
                self.execute()
                self._last_execution_time = time.time()
            except Exception as e:
                log.error(f"Error in daemon task '{self.name}': {e}")
                # Continue running even if there's an error
                self._stop_event.wait(timeout=60)  # Wait a minute before retry

        log.info(f"Daemon '{self.name}' loop exiting")

    @abstractmethod
    def execute(self) -> None:
        """
        Execute the task logic.
        This method must be implemented by subclasses.
        """
        pass

    def force_execute(self) -> None:
        """Force an immediate execution of the task (useful for testing or debugging)."""
        if not self._running:
            log.warning(f"Daemon task '{self.name}' is not running, cannot force execution")
            return
        try:
            self.execute()
            self._last_execution_time = time.time()
        except Exception as e:
            log.error(f"Error during forced execution of '{self.name}': {e}")

    @property
    def is_running(self) -> bool:
        """Check if the daemon task is currently running."""
        return self._running

    @property
    def next_execution_time(self) -> Optional[datetime]:
        """Get the estimated time of the next scheduled execution."""
        if not self._running or self._last_execution_time is None:
            return None
        next_time = self._last_execution_time + self._interval_seconds
        return datetime.fromtimestamp(next_time)

    @property
    def last_execution_time(self) -> Optional[datetime]:
        """Get the time of the last execution."""
        if self._last_execution_time is None:
            return None
        return datetime.fromtimestamp(self._last_execution_time)
