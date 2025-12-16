"""
Profile resolution with inheritance support.
"""

import logging
from typing import Any, Dict, List, Set

from .exceptions import CircularInheritanceError, ProfileNotFoundError
from .merger import ConfigMerger

logger = logging.getLogger(__name__)


class ProfileResolver:
    """
    Resolves profile configurations with inheritance support.

    Supports profile inheritance via 'inherits' key with circular dependency detection.
    Profiles can inherit from other profiles, creating a chain of configuration merging.
    """

    def __init__(self, inherit_key: str = "inherits"):
        """
        Initialize profile resolver.

        Args:
            inherit_key: Key name used for inheritance (default: "inherits")
        """
        self.inherit_key = inherit_key
        self.merger = ConfigMerger()

    def resolve_profile(
        self,
        config_data: Dict[str, Any],
        profile_name: str,
        default_profile: str = "default",
    ) -> Dict[str, Any]:
        """
        Resolve profile configuration with inheritance.

        Args:
            config_data: Full configuration data containing profiles
            profile_name: Name of profile to resolve
            default_profile: Name of default profile to use as base

        Returns:
            Resolved configuration dictionary

        Notes:
            If profile "default" is requested but doesn't exist, an empty profile
            is automatically created, returning only the defaults section.

        Raises:
            ProfileNotFoundError: If requested profile is not found
            CircularInheritanceError: If circular inheritance is detected
        """
        profiles = config_data.get("profiles", {})
        defaults = config_data.get("defaults", {})

        # If no profiles section, return defaults with any top-level config
        if not profiles:
            result = defaults.copy()
            # Add any non-reserved keys from root level
            for key, value in config_data.items():
                if key not in ["profiles", "defaults", "default_profile"]:
                    result[key] = value
            return result

        # Check if requested profile exists
        if profile_name not in profiles:
            # Special case: if "default" profile is requested but doesn't exist,
            # create an empty profile (returns only defaults)
            if profile_name == "default":
                logger.debug(
                    "Profile 'default' not found, using empty profile (defaults only)"
                )
                return defaults.copy()

            # Try default profile if different from requested
            if profile_name != default_profile and default_profile in profiles:
                logger.warning(
                    f"Profile '{profile_name}' not found, using '{default_profile}'"
                )
                profile_name = default_profile
            else:
                raise ProfileNotFoundError(
                    f"Profile '{profile_name}' not found. "
                    f"Available profiles: {list(profiles.keys())}"
                )

        # Resolve inheritance chain
        resolved_config = self._resolve_inheritance_chain(profiles, profile_name, set())

        # Merge with defaults using deep merge (defaults have lowest precedence)
        # FIX: Use merger.merge_configs() for deep merge instead of shallow .update()
        final_config = self.merger.merge_configs(
            defaults,
            resolved_config,
            enable_interpolation=False,  # Interpolation happens later in resolver
        )

        logger.debug(f"Resolved profile '{profile_name}' with {len(final_config)} keys")
        return final_config

    def _resolve_inheritance_chain(
        self, profiles: Dict[str, Any], profile_name: str, visited: Set[str]
    ) -> Dict[str, Any]:
        """
        Recursively resolve inheritance chain for a profile.

        Args:
            profiles: Dictionary of all profiles
            profile_name: Current profile to resolve
            visited: Set of already visited profiles (for cycle detection)

        Returns:
            Resolved configuration for the profile

        Raises:
            CircularInheritanceError: If circular inheritance is detected
        """
        if profile_name in visited:
            cycle_path = " -> ".join(visited) + f" -> {profile_name}"
            raise CircularInheritanceError(
                f"Circular inheritance detected: {cycle_path}"
            )

        if profile_name not in profiles:
            raise ProfileNotFoundError(
                f"Profile '{profile_name}' not found in inheritance chain"
            )

        visited.add(profile_name)
        profile_config = profiles[profile_name].copy()

        # Check for inheritance
        parent_profile = profile_config.pop(self.inherit_key, None)

        if parent_profile:
            # Recursively resolve parent configuration
            parent_config = self._resolve_inheritance_chain(
                profiles, parent_profile, visited.copy()
            )

            # Merge parent config with current profile using deep merge
            # FIX: Use merger.merge_configs() for deep merge
            merged_config = self.merger.merge_configs(
                parent_config,
                profile_config,
                enable_interpolation=False,  # Interpolation happens later
            )
            profile_config = merged_config

        visited.remove(profile_name)
        return profile_config

    def list_profiles(self, config_data: Dict[str, Any]) -> List[str]:
        """
        List available profiles in configuration.

        Args:
            config_data: Configuration data

        Returns:
            List of available profile names
        """
        profiles = config_data.get("profiles", {})
        return list(profiles.keys())

    def get_default_profile(self, config_data: Dict[str, Any]) -> str:
        """
        Get the default profile name from configuration.

        Args:
            config_data: Configuration data

        Returns:
            Default profile name
        """
        return config_data.get("default_profile", "default")
