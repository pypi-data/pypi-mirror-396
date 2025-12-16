# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

"""Omnissa Horizon Cloud Service SDK.

This package provides tools for building and managing lifecycle management plugins
for Omnissa Horizon Cloud Service. It includes the runtime environment for
communicating with the cloud service and utilities for plugin development.
"""

__all__ = ["__version__"]


def _get_version():
    """Get package version using importlib.metadata or fallback to pyproject.toml"""
    # Try importlib.metadata first (works for installed packages)
    try:
        from importlib.metadata import version

        return version("ohcs")
    except Exception:
        pass

    # Fallback to reading pyproject.toml (for development)
    try:
        from pathlib import Path

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("version"):
                        # Extract version string from: version = "1.0.1"
                        return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass

    return "unknown"


__version__ = _get_version()
