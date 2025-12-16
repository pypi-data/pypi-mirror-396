"""
Configuration file loading with multiple format support.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import tomllib  # Python 3.11+

    HAS_TOML = True
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]

        HAS_TOML = True
    except ImportError:
        HAS_TOML = False

from .exceptions import ConfigFormatError

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads configuration files in multiple formats.

    Supports YAML, JSON, and TOML formats with automatic format detection
    based on file extension.
    """

    def load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            file_path: Path to configuration file

        Returns:
            Dictionary containing configuration data

        Raises:
            ConfigFormatError: If file format is unsupported or invalid
            FileNotFoundError: If file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        extension = file_path.suffix.lower()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if extension in [".yaml", ".yml"]:
                    return self._load_yaml(f.read(), file_path)
                elif extension == ".json":
                    return self._load_json(f.read(), file_path)
                elif extension == ".toml":
                    return self._load_toml(f.read(), file_path)
                else:
                    raise ConfigFormatError(
                        f"Unsupported file format: {extension}. "
                        f"Supported formats: .yaml, .yml, .json, .toml"
                    )
        except (OSError, IOError) as e:
            raise ConfigFormatError(f"Error reading file {file_path}: {e}")

    def _load_yaml(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Load YAML content."""
        if not HAS_YAML:
            raise ConfigFormatError(
                "YAML support not available. Install PyYAML: pip install pyyaml"
            )

        try:
            data = yaml.safe_load(content)
            if data is None:
                return {}
            if not isinstance(data, dict):
                raise ConfigFormatError(
                    f"YAML file must contain a dictionary, got {type(data).__name__}: {file_path}"
                )
            return data
        except yaml.YAMLError as e:
            raise ConfigFormatError(f"Invalid YAML in {file_path}: {e}")

    def _load_json(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Load JSON content."""
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ConfigFormatError(
                    f"JSON file must contain an object, got {type(data).__name__}: {file_path}"
                )
            return data
        except json.JSONDecodeError as e:
            raise ConfigFormatError(f"Invalid JSON in {file_path}: {e}")

    def _load_toml(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Load TOML content."""
        if not HAS_TOML:
            raise ConfigFormatError(
                "TOML support not available. Install tomli: pip install tomli"
            )

        try:
            return tomllib.loads(content)
        except Exception as e:  # tomllib raises various exceptions
            raise ConfigFormatError(f"Invalid TOML in {file_path}: {e}")
