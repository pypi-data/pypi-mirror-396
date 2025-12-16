# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import asyncio
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

import yumako

from ohcs.common.utils import error_details
from ohcs.common import stats as global_stats

log = logging.getLogger(__name__)

_capacity = 50

_executor = ThreadPoolExecutor(max_workers=_capacity, thread_name_prefix="exec")


class Task:
    def __init__(self, id: str, name: str, timeout: float, method: Callable[[Any], Any]):
        self.id: str = id
        self.name: str = name
        self.timeout: float = timeout
        self.method: Callable[[Any], Any] = method
        self.future: Optional[Future[Any]] = None
        self.time_added: float = time.time()
        self.time_started: Optional[float] = None
        self.error: Optional[BaseException] = None
        self.result: Optional[Any] = None

    def time_in_queue(self) -> float:
        return self.time_started - self.time_added if self.time_started else time.time() - self.time_added

    def time_in_execution(self) -> float:
        return time.time() - self.time_started if self.time_started else 0

    def start(self) -> None:
        self.time_started = time.time()

    def __str__(self) -> str:
        queued = yumako.time.display(self.time_in_queue())
        execution = yumako.time.display(self.time_in_execution())
        if self.future:
            if self.future.done():
                if self.error:
                    ret = f"error={error_details(self.error)})"
                else:
                    ret = f"result={self.result})"
            elif self.future.running():
                ret = "<running>"
            else:
                ret = "<queued>"
        else:
            ret = "<submitted>"
        return f"Task[{self.id}/{self.name}] (timeout={self.timeout}, queued={queued}, execution={execution}, {ret})"

    def on_complete(self, callback: Callable[["Task"], Any]) -> None:
        def cb(future: Future[Any]) -> None:
            self.error = future.exception()
            if not self.error:
                self.result = future.result()
            callback(self)

        self.future.add_done_callback(cb)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation"""
        status = "submitted"
        if self.future:
            if self.future.done():
                status = "error" if self.error else "completed"
            elif self.future.running():
                status = "running"
            else:
                status = "queued"

        return {
            "id": self.id,
            "name": self.name,
            "timeout": self.timeout,
            "status": status,
            "time_added": self.time_added,
            "time_started": self.time_started,
            "time_in_queue": self.time_in_queue(),
            "time_in_execution": self.time_in_execution(),
            "error": error_details(self.error) if self.error else None,
        }


class TaskTracker:
    def __init__(self) -> None:
        self._task_details: Dict[str, Task] = {}
        self._lock = threading.RLock()

    def add(self, id: str, name: str, timeout: float, method: Callable[[Any], Any]) -> Task:
        with self._lock:
            if id in self._task_details:
                raise ValueError(f"Task {id} already exists")
            task = Task(id, name, timeout, method)
            self._task_details[id] = task
            return task

    def remove(self, id: str) -> None:
        with self._lock:
            del self._task_details[id]

    def all(self) -> Dict[str, Task]:
        """Get details for all tracked tasks"""
        with self._lock:
            return self._task_details.copy()

    def clear(self) -> None:
        """Clear all tracked tasks"""
        with self._lock:
            self._task_details.clear()

    def count(self) -> int:
        """Get the number of currently tracked tasks"""
        with self._lock:
            return len(self._task_details.values())

    def dump(self) -> str:
        copy = self.all()
        slow_tasks = []
        delayed_tasks = []
        for task in copy.values():
            if task.time_in_execution() > task.timeout:
                slow_tasks.append(task)
        for task in slow_tasks:
            copy.pop(task.id)
        for task in copy.values():
            if task.time_in_queue() > 6:
                delayed_tasks.append(task)
        for task in delayed_tasks:
            copy.pop(task.id)

        ret = ["---- TASK DUMP START ----"]
        if slow_tasks:
            for task in slow_tasks:
                ret.append(f"SLOW:    {task}")
        if delayed_tasks:
            for task in delayed_tasks:
                ret.append(f"DELAYED: {task}")
        if copy:
            for task in copy.values():
                ret.append(f"NORMAL:  {task}")
        ret.append("---- TASK DUMP END ----")
        return "\n".join(ret)


_task_tracker = TaskTracker()
_last_full_log_reported_at = 0


def _log_if_full():
    if _task_tracker.count() < _capacity:
        return
    now = time.time()
    global _last_full_log_reported_at
    if now - _last_full_log_reported_at < 10:
        return
    _last_full_log_reported_at = now
    log.warning(f"Executor is full ({_task_tracker.count()}/{_capacity} tasks).\n" + _task_tracker.dump())


def safe_invoke(
    task_id: str,
    name: str,
    timeout: float,
    method: Callable[[Any], Any],
    *args,
    **kwargs,
):
    task = _task_tracker.add(task_id, name, timeout, method)
    _log_if_full()
    task.future = _executor.submit(_run_with_context, task, *args, **kwargs)
    return task


def _run_with_context(task: Task, *args, **kwargs) -> Any:
    task.start()

    current_thread = threading.current_thread()
    setattr(current_thread, "_task_context", task)

    try:
        global_stats.increase("executor.tasks_executed")
        ret = task.method(*args, **kwargs)

        if not asyncio.iscoroutinefunction(task.method):
            # Increment task execution counter
            return ret

        global_stats.increase("executor.tasks_executed_async")

        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            ret = loop.run_until_complete(asyncio.wait_for(ret, timeout=task.timeout))
        finally:
            loop.close()
            asyncio.set_event_loop(None)
        return ret
    except Exception as e:
        global_stats.increase("executor.tasks_exception")
        raise e
    finally:
        # Mark task as completed and remove from tracking
        _task_tracker.remove(task.id)
        delattr(current_thread, "_task_context")


def shutdown():
    _task_tracker.clear()
    _executor.shutdown(wait=True, cancel_futures=True)


def task_context() -> Optional[Task]:
    return getattr(threading.current_thread(), "_task_context", None)


def stats() -> Dict[str, Any]:
    """
    Get comprehensive executor statistics and current task details.

    Returns:
        Dict containing:
        - capacity: Maximum number of worker threads
        - active_tasks: Number of currently tracked tasks
        - utilization: Percentage of capacity being used
        - tasks: Dict of all tasks categorized by status
    """
    all_tasks = _task_tracker.all()

    # Categorize tasks
    queued_tasks = []
    running_tasks = []
    slow_tasks = []
    delayed_tasks = []

    for task in all_tasks.values():
        task_dict = task.to_dict()

        # Check if task is slow (execution time exceeds timeout)
        if task.time_in_execution() > task.timeout:
            slow_tasks.append(task_dict)
        # Check if task is delayed in queue
        elif task.time_in_queue() > 6 and task_dict["status"] == "queued":
            delayed_tasks.append(task_dict)
        # Categorize by status
        elif task_dict["status"] == "running":
            running_tasks.append(task_dict)
        elif task_dict["status"] == "queued":
            queued_tasks.append(task_dict)

    active_count = _task_tracker.count()

    return {
        "capacity": _capacity,
        "active_tasks": active_count,
        "utilization": round(active_count / _capacity * 100, 2) if _capacity > 0 else 0,
        "tasks": {
            "queued": queued_tasks,
            "running": running_tasks,
            "slow": slow_tasks,
            "delayed": delayed_tasks,
        },
        "counts": {
            "queued": len(queued_tasks),
            "running": len(running_tasks),
            "slow": len(slow_tasks),
            "delayed": len(delayed_tasks),
        },
    }
