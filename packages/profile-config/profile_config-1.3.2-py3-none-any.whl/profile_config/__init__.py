"""
Profile Config - Hierarchical profile-based configuration management.

This package provides configuration resolution with:
- Hierarchical directory discovery
- Profile inheritance
- Configurable search patterns
- Multiple file format support
- Environment variable expansion
- Command execution in configuration values
"""

import logging

from .discovery import ConfigDiscovery
from .exceptions import (
    CircularInheritanceError,
    ConfigNotFoundError,
    ProfileConfigError,
    ProfileNotFoundError,
)
from .merger import ConfigMerger
from .profiles import ProfileResolver
from .resolver import ProfileConfigResolver

# Add NullHandler to prevent "No handler found" warnings
# Applications using this library should configure their own handlers
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "1.3.2"
__all__ = [
    "ProfileConfigResolver",
    "ConfigDiscovery",
    "ProfileResolver",
    "ConfigMerger",
    "ProfileConfigError",
    "ConfigNotFoundError",
    "ProfileNotFoundError",
    "CircularInheritanceError",
]
