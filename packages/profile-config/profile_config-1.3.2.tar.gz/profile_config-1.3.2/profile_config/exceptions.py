"""
Exception classes for profile-config.
"""


class ProfileConfigError(Exception):
    """Base exception for all profile-config errors."""

    pass


class ConfigNotFoundError(ProfileConfigError):
    """Raised when no configuration files are found."""

    pass


class ProfileNotFoundError(ProfileConfigError):
    """Raised when a requested profile is not found."""

    pass


class CircularInheritanceError(ProfileConfigError):
    """Raised when circular inheritance is detected in profiles."""

    pass


class ConfigFormatError(ProfileConfigError):
    """Raised when configuration file format is invalid."""

    pass
