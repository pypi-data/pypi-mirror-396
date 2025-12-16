# ----------------------------------------------------------------------------
# Copyright (c) Omnissa, LLC. All rights reserved.
# This product is protected by copyright and intellectual property laws in the
# United States and other countries as well as by international treaties.
# ----------------------------------------------------------------------------

import ohcs


def test_version_exists():
    """Test that the package has a version attribute."""
    assert hasattr(ohcs, "__version__")


def test_version_format():
    """Test that the version is a string and not 'unknown'."""
    assert isinstance(ohcs.__version__, str)
    assert ohcs.__version__ != "unknown"
    assert len(ohcs.__version__) > 0


def test_version_is_valid_semver():
    """Test that the version follows semantic versioning format."""
    version = ohcs.__version__
    parts = version.split(".")

    # Should have at least major.minor.patch
    assert len(parts) >= 3, f"Version {version} should have at least 3 parts"

    # First three parts should be integers
    for i, part in enumerate(parts[:3]):
        assert part.isdigit(), f"Version part {i} ({part}) should be a number"
