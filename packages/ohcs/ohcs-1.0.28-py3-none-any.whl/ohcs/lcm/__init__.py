# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

"""Lifecycle Management (LCM) module for OHCS.

This module provides the core lifecycle management functionality including
plugin loading, validation, and server operations for managing virtual machine
lifecycles through custom providers.

"""

from .serve import serve

__all__ = ["serve"]
