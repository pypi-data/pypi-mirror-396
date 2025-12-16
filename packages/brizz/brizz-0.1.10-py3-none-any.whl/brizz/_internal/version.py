"""Version utilities for Brizz SDK."""

from importlib.metadata import PackageNotFoundError, version


def get_version() -> str:
    """Get the Brizz SDK version.

    Returns:
        The version string (e.g., "0.1.2")
    """
    try:
        return version("brizz")
    except PackageNotFoundError:
        # Fallback for unknown version
        return "unknown"
