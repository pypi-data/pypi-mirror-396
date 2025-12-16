# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import atexit
import json
import logging
from multiprocessing import shared_memory
from threading import Lock
from typing import Any, Optional

log = logging.getLogger(__name__)

# Configuration
_SHARED_MEMORY_NAME = "ohcs_global_stats"
_SHARED_MEMORY_SIZE = 65536  # 64KB for stats

# Module state
_stats: dict[str, Any] = {}
_stats_lock = Lock()
_shm: Optional[shared_memory.SharedMemory] = None


# def _signal_handler(signum, frame):
#     """Handle termination signals to cleanup shared memory"""
#     log.info(f"Received signal {signum}, shutting down gracefully...")
#     sys.exit(0)  # This will trigger atexit handlers


def _init_shared_memory() -> bool:
    """
    Initialize shared memory for stats storage (SERVE mode only).
    Registers cleanup handlers to ensure proper shutdown.
    """
    global _shm

    if _shm is not None:
        return True

    atexit.register(cleanup)
    # signal.signal(signal.SIGTERM, _signal_handler)
    # signal.signal(signal.SIGINT, _signal_handler)

    try:
        _shm = shared_memory.SharedMemory(name=_SHARED_MEMORY_NAME, create=True, size=_SHARED_MEMORY_SIZE)

        # Register cleanup handlers - only for the creator process
        log.debug(f"Shared memory initialized: {_SHARED_MEMORY_NAME}")
        return True

    except FileExistsError:
        # Shared memory already exists - clean it up and recreate
        log.warning(f"Shared memory {_SHARED_MEMORY_NAME} already exists, attempting cleanup...")
        try:
            old_shm = shared_memory.SharedMemory(name=_SHARED_MEMORY_NAME, create=False)
            log.debug("Destroying old shared memory...")
            old_shm.close()
            old_shm.unlink()
            log.debug("Old shared memory cleaned up")

            # Now create fresh
            _shm = shared_memory.SharedMemory(name=_SHARED_MEMORY_NAME, create=True, size=_SHARED_MEMORY_SIZE)
            log.debug(f"Shared memory re-created: {_SHARED_MEMORY_NAME}")
            return True
        except Exception as e:
            log.error(f"Failed to cleanup and recreate shared memory: {e}")
            return False

    except Exception as e:
        log.error(f"Failed to initialize shared memory: {e}")
        return False


def _write_to_shared_memory(stats_dict: dict[str, Any]) -> None:
    """Write stats dictionary to shared memory as JSON."""
    if _shm is None:
        if not _init_shared_memory():
            return

    try:
        stats_json = json.dumps(stats_dict).encode("utf-8")

        if len(stats_json) > _SHARED_MEMORY_SIZE:
            log.error(f"Stats too large for shared memory: {len(stats_json)} bytes")
            return

        # Zero out buffer and write JSON
        _shm.buf[:_SHARED_MEMORY_SIZE] = b"\0" * _SHARED_MEMORY_SIZE
        _shm.buf[: len(stats_json)] = stats_json

    except Exception as e:
        log.error(f"Error writing to shared memory: {e}")


def set(key: str, value: Any) -> None:
    """Set a statistic key to a value."""
    with _stats_lock:
        _stats[key] = value
        _write_to_shared_memory(_stats)


def get(key: str, default: Optional[Any] = None) -> Any:
    """Get a statistic value by key, returning default if not found."""
    with _stats_lock:
        return _stats.get(key, default)


def get_int(key: str, default: int = 0) -> int:
    """Get a statistic value as an integer."""
    with _stats_lock:
        return int(_stats.get(key, default))


def increase(key: str, amount: int = 1) -> None:
    """Increase a statistic value by a specified amount."""
    with _stats_lock:
        current_value = _stats.get(key, 0)
        if not isinstance(current_value, int):
            raise ValueError(f"Statistic '{key}' is not an integer and cannot be increased.")
        _stats[key] = current_value + amount
        _write_to_shared_memory(_stats)


def all() -> dict[str, Any]:
    """Get a copy of all statistics from the current process."""
    with _stats_lock:
        return dict(_stats)


def read_shared() -> Optional[dict[str, Any]]:
    """
    Read statistics from shared memory (INFO mode).
    Safely reads without taking ownership or interfering with the creator process.

    Returns:
        Dictionary of all statistics, or None if not available.
    """
    try:
        # Open existing shared memory (read-only access)
        shm = shared_memory.SharedMemory(name=_SHARED_MEMORY_NAME, create=False)

        # Python 3.9 bug workaround: Unregister from resource tracker IMMEDIATELY
        # BEFORE doing anything else. In Python 3.9-3.11, the resource tracker
        # incorrectly tries to unlink shared memory even when we only call close().
        # We must unregister before close() to prevent the tracker from interfering.
        try:
            from multiprocessing import resource_tracker

            resource_tracker.unregister(shm._name, "shared_memory")  # type: ignore[attr-defined]
        except Exception:
            # Ignore errors - this is best effort for Python 3.9 compatibility
            pass

        try:
            # Read the data
            data = bytes(shm.buf[:_SHARED_MEMORY_SIZE])
            null_pos = data.find(b"\0")
            if null_pos > 0:
                stats_json = data[:null_pos].decode("utf-8")
                return json.loads(stats_json)
            return None
        finally:
            # Just close - never unlink (creator owns it)
            try:
                shm.close()
            except Exception:
                pass

    except FileNotFoundError:
        return None
    except Exception as e:
        log.warning(f"Error reading from shared memory: {e}")
        return None


def cleanup() -> None:
    """
    Cleanup shared memory resources (SERVE mode only).
    Called automatically on process shutdown via atexit.
    """
    global _shm

    if _shm is not None:
        try:
            log.debug("Destroy shared memory")
            _shm.close()
            _shm.unlink()
            log.debug(f"Shared memory cleaned up: {_SHARED_MEMORY_NAME}")
        except Exception as e:
            log.warning(f"Error cleaning up shared memory: {e}")
        finally:
            _shm = None
