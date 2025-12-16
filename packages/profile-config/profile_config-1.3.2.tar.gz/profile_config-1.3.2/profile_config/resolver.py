"""
Main profile configuration resolver.
"""

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .discovery import ConfigDiscovery
from .exceptions import ConfigFormatError, ConfigNotFoundError
from .loader import ConfigLoader
from .merger import ConfigMerger
from .profiles import ProfileResolver

logger = logging.getLogger(__name__)

# Type aliases for overrides
OverrideSource = Union[Dict[str, Any], str, Path, os.PathLike]
OverridesType = Optional[Union[OverrideSource, List[OverrideSource]]]


class ProfileConfigResolver:
    """
    Main interface for profile-based configuration resolution.

    Provides a unified interface for discovering configuration files,
    resolving profiles with inheritance, and merging configurations
    with proper precedence handling.
    """

    def __init__(
        self,
        config_name: str,
        profile: str = "default",
        profile_filename: str = "config",
        overrides: OverridesType = None,
        extensions: Optional[List[str]] = None,
        search_home: bool = True,
        inherit_key: str = "inherits",
        enable_interpolation: bool = True,
        apply_environment: bool = True,
        environment_key: str = "env_vars",
        override_environment: bool = False,
        command_timeout: float = 2.0,
    ):
        """
        Initialize profile configuration resolver.

        Args:
            config_name: Name of configuration directory (e.g., "myapp")
            profile: Profile name to resolve (default: "default")
            profile_filename: Name of profile file without extension (default: "config")
            overrides: Override values (highest precedence). Can be:
                - Dict[str, Any]: Single override dictionary
                - PathLike: Path to override file (yaml/json/toml)
                - List[Union[Dict, PathLike]]: Multiple overrides applied in order
            extensions: File extensions to search for (default: yaml, yml, json, toml)
            search_home: Whether to search home directory
            inherit_key: Key name used for profile inheritance (default: "inherits")
            enable_interpolation: Whether to enable variable interpolation
            apply_environment: Whether to apply environment variables from config (default: True)
            environment_key: Key name for environment variables section (default: "env_vars")
            override_environment: Whether to override existing environment variables (default: False)
            command_timeout: Timeout in seconds for command execution (default: 2.0)
        """
        self.config_name = config_name
        self.profile = profile
        self.profile_filename = profile_filename
        self.enable_interpolation = enable_interpolation
        self.apply_environment = apply_environment
        self.environment_key = environment_key
        self.override_environment = override_environment
        self.command_timeout = command_timeout

        # Track environment variable application
        self._env_applied: Dict[str, str] = {}
        self._env_skipped: Dict[str, str] = {}

        # Initialize components
        self.discovery = ConfigDiscovery(
            config_name=config_name,
            profile_filename=profile_filename,
            extensions=extensions,
            search_home=search_home,
        )
        self.loader = ConfigLoader()
        self.profile_resolver = ProfileResolver(inherit_key=inherit_key)
        self.merger = ConfigMerger()

        # Process overrides into list of dictionaries
        self.override_list = self._process_overrides(overrides)

    def _process_overrides(self, overrides: OverridesType) -> List[Dict[str, Any]]:
        """
        Process overrides into a list of dictionaries.

        Args:
            overrides: Single dict, file path, or list of dicts/paths

        Returns:
            List of override dictionaries in application order

        Raises:
            ConfigFormatError: If file cannot be loaded or invalid type provided
        """
        if overrides is None:
            return []

        # Normalize to list
        if not isinstance(overrides, list):
            override_list = [overrides]
        else:
            override_list = overrides

        # Process each override source
        processed: List[Dict[str, Any]] = []
        for override_source in override_list:
            if isinstance(override_source, dict):
                # Direct dictionary
                processed.append(override_source)
                logger.debug("Added dictionary override")
            elif isinstance(override_source, (str, Path, os.PathLike)):
                # File path - load it
                file_path = Path(override_source)
                try:
                    override_dict = self.loader.load_config_file(file_path)
                    processed.append(override_dict)
                    logger.debug(f"Loaded override from {file_path}")
                except FileNotFoundError:
                    raise ConfigFormatError(f"Override file not found: {file_path}")
                except Exception as e:
                    raise ConfigFormatError(
                        f"Failed to load override file {file_path}: {e}"
                    )
            else:
                raise ConfigFormatError(
                    f"Invalid override type: {type(override_source).__name__}. "
                    f"Expected dict, file path, or list of dicts/paths"
                )

        logger.debug(f"Processed {len(processed)} override sources")
        return processed

    def _expand_value(self, value: Any, context: str = "") -> Any:
        """
        Expand command substitutions in a single value.

        Processes $(...) syntax by executing commands with shell expansion.
        Failed commands or empty output return None.

        Args:
            value: Value to expand (only processes strings)
            context: Context for logging (e.g., key name)

        Returns:
            Expanded value or None if command failed
        """
        if not isinstance(value, str):
            return value

        # Pattern to match $(command) syntax
        cmd_pattern = re.compile(r"\$\(([^)]+)\)")

        # Find all command substitutions in the value
        matches = cmd_pattern.findall(value)
        if not matches:
            return value

        # Process each command substitution
        expanded_value = value
        for cmd in matches:
            try:
                logger.debug(
                    f"Executing command{' for ' + context if context else ''}: {cmd}"
                )

                # Execute command with shell expansion and current environment
                proc_result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.command_timeout,
                    env=os.environ.copy(),
                )

                if proc_result.returncode != 0:
                    stderr = proc_result.stderr.strip()
                    logger.error(
                        f"Command failed{' for ' + context if context else ''}: {cmd} "
                        f"(exit {proc_result.returncode}): {stderr}"
                    )
                    # Failed command = return None
                    return None

                output = proc_result.stdout.strip()
                if not output:
                    logger.warning(
                        f"Command produced no output{' for ' + context if context else ''}: {cmd}"
                    )
                    # Empty output = return None
                    return None

                # Replace this command substitution with its output
                expanded_value = expanded_value.replace(f"$({cmd})", output)
                logger.debug(
                    f"Command output{' for ' + context if context else ''}: {output}"
                )

            except subprocess.TimeoutExpired:
                logger.error(
                    f"Command timeout ({self.command_timeout}s){' for ' + context if context else ''}: {cmd}"
                )
                return None
            except Exception as e:
                logger.error(
                    f"Command execution error{' for ' + context if context else ''}: {cmd} - {e}"
                )
                return None

        return expanded_value

    def _expand_commands_recursive(self, data: Any, path: str = "") -> Any:
        """
        Recursively expand command substitutions in configuration data.

        Args:
            data: Configuration data (dict, list, or primitive)
            path: Current path in config (for logging)

        Returns:
            Configuration data with commands expanded
        """
        if isinstance(data, dict):
            result: Dict[str, Any] = {}
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                expanded = self._expand_commands_recursive(value, current_path)
                # Skip None values (failed commands)
                if expanded is not None:
                    result[key] = expanded
                else:
                    logger.debug(f"Skipping key '{current_path}' due to failed command")
            return result
        elif isinstance(data, list):
            result_list: List[Any] = []
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                expanded = self._expand_commands_recursive(item, current_path)
                # Keep None in lists (user might want it)
                result_list.append(expanded)
            return result_list
        elif isinstance(data, str):
            return self._expand_value(data, path)
        else:
            # Other types (int, float, bool, None) pass through
            return data

    def _apply_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and apply environment variables from config.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration dictionary with env_vars section removed
        """
        # Reset tracking
        self._env_applied = {}
        self._env_skipped = {}

        # Always remove the environment key from config
        config_copy = dict(config)
        env_vars = config_copy.pop(self.environment_key, None)

        if not self.apply_environment:
            return config_copy

        if not env_vars:
            # Empty or missing - nothing to apply
            return config_copy

        if not isinstance(env_vars, dict):
            logger.warning(
                f"'{self.environment_key}' section must be a dictionary, found {type(env_vars).__name__}"
            )
            return config_copy

        # Apply environment variables (already expanded by _expand_commands_recursive)
        for key, value in env_vars.items():
            if not isinstance(key, str):
                logger.warning(
                    f"Environment variable key must be string, skipping: {key}"
                )
                continue

            # None value means "not set" (from failed command or missing env var)
            if value is None:
                logger.debug(f"Skipping environment variable '{key}' (value is None)")
                continue

            # Convert value to string
            str_value = str(value) if value is not None else ""

            # Check if variable already exists
            if key in os.environ and not self.override_environment:
                self._env_skipped[key] = str_value
                logger.debug(
                    f"Environment variable '{key}' already exists, skipping "
                    f"(override_environment=False)"
                )
            else:
                os.environ[key] = str_value
                self._env_applied[key] = str_value
                logger.debug(f"Set environment variable '{key}' from config")

        applied_count = len(self._env_applied)
        skipped_count = len(self._env_skipped)
        total_count = applied_count + skipped_count

        if applied_count > 0 or skipped_count > 0:
            logger.info(
                f"Processed {total_count} environment variables: "
                f"{applied_count} applied, {skipped_count} skipped"
            )

        return config_copy

    def get_environment_info(self) -> Dict[str, Dict[str, str]]:
        """
        Get information about environment variables applied from config.

        Returns:
            Dictionary with 'applied' and 'skipped' environment variables
        """
        return {
            "applied": dict(self._env_applied),
            "skipped": dict(self._env_skipped),
        }

    def resolve(self) -> Dict[str, Any]:
        """
        Resolve configuration with full precedence handling.

        Resolution order:
        1. Discover configuration files (hierarchical search)
        2. Load and merge configuration files (most specific first)
        3. Expand command substitutions in entire config
        4. Resolve profile with inheritance
        5. Apply overrides in order (highest precedence)
        6. Apply variable interpolation (OmegaConf)
        7. Apply environment variables from config (if enabled)

        Returns:
            Resolved configuration dictionary (without env_vars section)

        Raises:
            ConfigNotFoundError: If no configuration files are found
            ProfileNotFoundError: If requested profile is not found
            CircularInheritanceError: If circular inheritance is detected
            ConfigFormatError: If override files cannot be loaded
        """
        # Step 1: Discover configuration files
        config_files = self.discovery.discover_config_files()
        logger.info(f"Found {len(config_files)} configuration files")

        # Step 2: Load configuration files
        config_data_list: List[Dict[str, Any]] = []
        for config_file in reversed(config_files):  # Reverse for precedence order
            try:
                config_data = self.loader.load_config_file(config_file)
                config_data_list.append(config_data)
                logger.debug(f"Loaded config from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_file}: {e}")
                continue

        if not config_data_list:
            raise ConfigNotFoundError("No valid configuration files could be loaded")

        # Step 3: Merge configuration files
        merged_config = self.merger.merge_config_files(
            config_data_list,
            enable_interpolation=False,  # Defer interpolation until after profile resolution
        )

        # Step 4: Expand command substitutions BEFORE profile resolution
        # This allows $(command) to work in any configuration value
        logger.debug("Expanding command substitutions in configuration")
        merged_config = self._expand_commands_recursive(merged_config)

        # Step 5: Resolve profile
        profile_config = self.profile_resolver.resolve_profile(
            merged_config,
            self.profile,
            self.profile_resolver.get_default_profile(merged_config),
        )

        # Step 6: Apply overrides in order and final interpolation
        if self.override_list:
            # Expand commands in overrides too
            expanded_overrides = [
                self._expand_commands_recursive(override)
                for override in self.override_list
            ]
            # Apply each override in order (later overrides take precedence)
            final_config = self.merger.merge_configs(
                profile_config,
                *expanded_overrides,  # Unpack list to apply in order
                enable_interpolation=self.enable_interpolation,
            )
            logger.debug(f"Applied {len(self.override_list)} override sources")
        else:
            final_config = self.merger.merge_configs(
                profile_config, enable_interpolation=self.enable_interpolation
            )

        # Step 7: Apply environment variables and remove from config
        final_config = self._apply_environment_variables(final_config)

        logger.info(
            f"Resolved configuration for profile '{self.profile}' with {len(final_config)} keys"
        )
        return final_config

    def list_profiles(self) -> List[str]:
        """
        List available profiles from discovered configuration.

        Returns:
            List of available profile names
        """
        try:
            config_files = self.discovery.discover_config_files()
        except ConfigNotFoundError:
            return []

        # Load and merge all config files to get complete profile list
        config_data_list: List[Dict[str, Any]] = []
        for config_file in config_files:
            try:
                config_data = self.loader.load_config_file(config_file)
                config_data_list.append(config_data)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_file}: {e}")
                continue

        if not config_data_list:
            return []

        merged_config = self.merger.merge_config_files(
            config_data_list, enable_interpolation=False
        )
        return self.profile_resolver.list_profiles(merged_config)

    def get_config_files(self) -> List[Path]:
        """
        Get list of discovered configuration files.

        Returns:
            List of configuration file paths in precedence order
        """
        try:
            return self.discovery.discover_config_files()
        except ConfigNotFoundError:
            return []
