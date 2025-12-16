# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import logging
from datetime import datetime
from typing import Optional

from ohcs.common import executor, stats
from ohcs.common.daemon import DaemonTask

log = logging.getLogger(__name__)


class StatsLogger(DaemonTask):
    """
    Daily statistics logger for executor metrics.
    Logs executor statistics at a configured interval (default: daily).
    """

    def __init__(self, interval: str):
        """
        Initialize the daily statistics logger.

        Args:
            interval: Logging interval as a string, e.g. "24h", "12m"
        """
        super().__init__(name="stats-logger", interval=interval)

    def execute(self) -> None:
        """Log current executor statistics."""
        try:
            executor_stats = executor.stats()
            global_stats = stats.all()
            now = datetime.now()

            # Format the statistics for logging
            log_lines = [
                "",
                "=" * 80,
                f"EXECUTOR STATISTICS - {now.strftime('%Y-%m-%d %H:%M:%S')}",
                "=" * 80,
                f"Capacity: {executor_stats['capacity']} workers",
                f"Active Tasks: {executor_stats['active_tasks']}",
                f"Utilization: {executor_stats['utilization']}%",
                "",
                "Task Counts:",
                f"  - Queued: {executor_stats['counts']['queued']}",
                f"  - Running: {executor_stats['counts']['running']}",
                f"  - Slow (exceeding timeout): {executor_stats['counts']['slow']}",
                f"  - Delayed (>6s in queue): {executor_stats['counts']['delayed']}",
            ]

            # Add global statistics
            if global_stats:
                log_lines.append("")
                log_lines.append("GLOBAL STATISTICS:")
                for key, value in sorted(global_stats.items()):
                    log_lines.append(f"  - {key}: {value}")

            # Add details about problematic tasks if any exist
            if executor_stats["tasks"]["slow"]:
                log_lines.append("")
                log_lines.append("SLOW TASKS (exceeding timeout):")
                for task in executor_stats["tasks"]["slow"]:
                    log_lines.append(
                        f"  - [{task['id']}] {task['name']}: "
                        f"timeout={task['timeout']}s, "
                        f"execution={task['time_in_execution']:.2f}s"
                    )

            if executor_stats["tasks"]["delayed"]:
                log_lines.append("")
                log_lines.append("DELAYED TASKS (waiting >6s):")
                for task in executor_stats["tasks"]["delayed"]:
                    log_lines.append(f"  - [{task['id']}] {task['name']}: queued={task['time_in_queue']:.2f}s")

            # Add summary of currently running tasks
            if executor_stats["tasks"]["running"]:
                log_lines.append("")
                log_lines.append(f"RUNNING TASKS ({len(executor_stats['tasks']['running'])}):")
                for task in executor_stats["tasks"]["running"][:10]:  # Limit to first 10
                    log_lines.append(f"  - [{task['id']}] {task['name']}: execution={task['time_in_execution']:.2f}s")
                if len(executor_stats["tasks"]["running"]) > 10:
                    log_lines.append(f"  ... and {len(executor_stats['tasks']['running']) - 10} more")

            log_lines.append("=" * 80)

            # Log as a single message
            log.info("\n".join(log_lines))

        except Exception as e:
            log.error(f"Failed to log executor statistics: {e}")


# Global instance for easy access
_stats_logger: Optional[StatsLogger] = None


def start_stats_logging():
    """
    Start statistics logging.

    Returns:
        The StatsLogger instance
    """
    global _stats_logger

    if _stats_logger is not None and _stats_logger.is_running:
        log.warning("Daily stats logger is already running")
        return _stats_logger

    _stats_logger = StatsLogger(interval="24h")
    _stats_logger.start()


def stop_stats_logging() -> None:
    """Stop statistics logging."""
    global _stats_logger

    if _stats_logger is not None:
        _stats_logger.stop()
        _stats_logger = None
