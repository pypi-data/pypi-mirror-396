"""
Configuration file discovery with hierarchical search.

This module provides functionality to discover configuration files by searching
up the directory tree from the current working directory and optionally in the
user's home directory.
"""

import os
from pathlib import Path
from typing import List, Set

from .exceptions import ConfigNotFoundError


class ConfigDiscovery:
    """
    Discovers configuration files using hierarchical directory search.

    Searches for configuration files in the following order:
    1. Current working directory and parent directories (up to root)
    2. User's home directory (if enabled)

    For each directory, looks for: {config_name}/{profile_filename}.{extension}
    """

    def __init__(
        self,
        config_name: str,
        profile_filename: str = "config",
        extensions: List[str] = None,
        search_home: bool = True,
    ):
        """
        Initialize configuration discovery.

        Args:
            config_name: Name of the configuration directory to search for
            profile_filename: Name of the profile file without extension (default: "config")
            extensions: List of file extensions to search for (default: yaml, yml, json, toml)
            search_home: Whether to search in the user's home directory
        """
        self.config_name = config_name
        self.profile_filename = profile_filename
        self.extensions = extensions or ["yaml", "yml", "json", "toml"]
        self.search_home = search_home

    def discover_config_files(self) -> List[Path]:
        """
        Discover configuration files in hierarchical order.

        Returns:
            List of configuration file paths in order of precedence (most specific first)

        Raises:
            ConfigNotFoundError: If no configuration files are found
        """
        config_files = []

        # Search up directory tree for exact matches only
        config_files.extend(self._search_directory_tree())

        # Search home directory for exact match only
        if self.search_home:
            config_files.extend(self._search_home_directory())

        # Remove duplicates while preserving order
        config_files = self._remove_duplicates(config_files)

        if not config_files:
            search_locations = self._get_search_locations()
            raise ConfigNotFoundError(
                f"No configuration files found for '{self.config_name}'. "
                f"Searched for {self.profile_filename}.{{{','.join(self.extensions)}}} in: {search_locations}"
            )

        return config_files

    def _search_directory_tree(self) -> List[Path]:
        """Search up directory tree for {config_name}/{profile_filename}.{ext}"""
        config_files = []
        current = Path.cwd()

        while current != current.parent:
            config_dir = current / self.config_name
            if config_dir.is_dir():
                config_files.extend(self._search_directory(config_dir))
            current = current.parent

        return config_files

    def _search_home_directory(self) -> List[Path]:
        """Search home directory for {config_name}/{profile_filename}.{ext}"""
        home = Path.home()
        config_dir = home / self.config_name

        if config_dir.is_dir():
            return self._search_directory(config_dir)

        return []

    def _search_directory(self, directory: Path) -> List[Path]:
        """Search for config files in a specific directory."""
        config_files = []

        for ext in self.extensions:
            config_file = directory / f"{self.profile_filename}.{ext}"
            if config_file.is_file():
                config_files.append(config_file)

        return config_files

    def _remove_duplicates(self, config_files: List[Path]) -> List[Path]:
        """Remove duplicate paths while preserving order."""
        seen: Set[Path] = set()
        unique_files = []

        for config_file in config_files:
            resolved = config_file.resolve()
            if resolved not in seen:
                seen.add(resolved)
                unique_files.append(config_file)

        return unique_files

    def _get_search_locations(self) -> List[str]:
        """Get list of locations that were searched for error messages."""
        locations = []

        # Add directory tree locations
        current = Path.cwd()
        while current != current.parent:
            locations.append(str(current / self.config_name))
            current = current.parent

        # Add home directory location
        if self.search_home:
            locations.append(str(Path.home() / self.config_name))

        return locations
