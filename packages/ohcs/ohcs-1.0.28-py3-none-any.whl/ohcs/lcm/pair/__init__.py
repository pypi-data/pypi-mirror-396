# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

"""Provider pairing utilities for OHCS.

This module handles pairing of local LCM extensions with Omnissa Horizon Cloud
Service providers and edges, including configuration management and cleanup.

Example:
    >>> from ohcs.lcm import pair
    >>> pair.pair_existing_or_new(org_id)
"""

from .main import pair_existing, pair_existing_or_new, reset, reset_all, create_stub_plugin_and_tutorial

__all__ = ["pair_existing", "pair_existing_or_new", "reset", "reset_all", "create_stub_plugin_and_tutorial"]
