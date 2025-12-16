"""
Configuration merging with precedence handling.
"""

import logging
import os
from typing import Any, Dict, List

from omegaconf import DictConfig, OmegaConf

logger = logging.getLogger(__name__)


class ConfigMerger:
    """
    Merges configuration from multiple sources with precedence rules.

    Uses OmegaConf for robust merging and variable interpolation.
    Supports deep merging of nested dictionaries and variable substitution.
    """

    def __init__(self):
        """Initialize the config merger and register custom resolvers."""
        self._register_resolvers()

    def _register_resolvers(self):
        """Register custom OmegaConf resolvers for environment variable access."""
        # Register 'env' resolver for ${env:VAR_NAME} syntax
        # Returns None if variable doesn't exist (will be converted to empty string)
        if not OmegaConf.has_resolver("env"):
            OmegaConf.register_new_resolver("env", lambda name: os.environ.get(name))
            logger.debug("Registered 'env' resolver for ${env:VAR_NAME} syntax")

    def merge_configs(
        self, *config_sources: Dict[str, Any], enable_interpolation: bool = True
    ) -> Dict[str, Any]:
        """
        Merge multiple configuration sources with precedence.

        Later sources in the argument list take precedence over earlier ones.

        Args:
            *config_sources: Configuration dictionaries to merge
            enable_interpolation: Whether to enable variable interpolation

        Returns:
            Merged configuration dictionary
        """
        if not config_sources:
            return {}

        # Filter out empty configs
        valid_configs = [config for config in config_sources if config]

        if not valid_configs:
            return {}

        if len(valid_configs) == 1:
            config = OmegaConf.create(valid_configs[0])
            return self._to_dict(config, enable_interpolation)

        # Convert all configs to OmegaConf objects
        omega_configs = [OmegaConf.create(config) for config in valid_configs]

        # Merge all configurations
        merged = OmegaConf.merge(*omega_configs)  # type: ignore[arg-type]

        logger.debug(f"Merged {len(valid_configs)} configuration sources")
        return self._to_dict(merged, enable_interpolation)  # type: ignore[arg-type]

    def merge_config_files(
        self, config_data_list: List[Dict[str, Any]], enable_interpolation: bool = True
    ) -> Dict[str, Any]:
        """
        Merge configuration data from multiple files.

        Args:
            config_data_list: List of configuration dictionaries from files
            enable_interpolation: Whether to enable variable interpolation

        Returns:
            Merged configuration dictionary
        """
        return self.merge_configs(
            *config_data_list, enable_interpolation=enable_interpolation
        )

    def _to_dict(
        self, omega_config: DictConfig, enable_interpolation: bool
    ) -> Dict[str, Any]:
        """
        Convert OmegaConf object to regular dictionary.

        Args:
            omega_config: OmegaConf configuration object
            enable_interpolation: Whether to resolve interpolations

        Returns:
            Regular Python dictionary
        """
        if enable_interpolation:
            # Resolve interpolations and convert to dict
            try:
                return OmegaConf.to_container(omega_config, resolve=True)  # type: ignore[return-value]
            except Exception as e:
                logger.warning(f"Variable interpolation failed: {e}")
                # Fall back to unresolved config
                return OmegaConf.to_container(omega_config, resolve=False)  # type: ignore[return-value]
        else:
            # Return without resolving interpolations
            return OmegaConf.to_container(omega_config, resolve=False)  # type: ignore[return-value]
