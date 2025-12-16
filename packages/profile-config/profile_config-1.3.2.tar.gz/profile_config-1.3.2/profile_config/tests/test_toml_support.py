"""Tests for TOML format support."""

import os
import tempfile
from pathlib import Path

import pytest

from profile_config import ProfileConfigResolver
from profile_config.exceptions import ConfigFormatError
from profile_config.loader import HAS_TOML, ConfigLoader


class TestTOMLSupport:
    """Test TOML configuration file support."""

    def test_toml_available(self):
        """Test that TOML support is available."""
        assert HAS_TOML, "TOML support should be available"

    def test_load_simple_toml(self, tmp_path):
        """Test loading a simple TOML configuration file."""
        # Create TOML config file
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[defaults]
database_host = "localhost"
database_port = 5432
debug = false

[profiles.development]
debug = true
database_name = "myapp_dev"
"""
        )

        loader = ConfigLoader()
        config = loader.load_config_file(config_file)

        expected = {
            "defaults": {
                "database_host": "localhost",
                "database_port": 5432,
                "debug": False,
            },
            "profiles": {"development": {"debug": True, "database_name": "myapp_dev"}},
        }
        assert config == expected

    def test_toml_complex_data_types(self, tmp_path):
        """Test TOML with complex data types."""
        # Create TOML config with arrays, nested tables, etc.
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[defaults]
name = "myapp"
version = "1.0.0"
tags = ["web", "api", "python"]

[defaults.database]
host = "localhost"
port = 5432
credentials = { username = "admin", password = "secret" }

[defaults.features]
feature_a = true
feature_b = false

[[defaults.servers]]
name = "web1"
ip = "192.168.1.1"

[[defaults.servers]]
name = "web2"
ip = "192.168.1.2"

[profiles.development]
[profiles.development.database]
host = "dev-db"
port = 5433
"""
        )

        loader = ConfigLoader()
        config = loader.load_config_file(config_file)

        # Verify complex structures are loaded correctly
        assert config["defaults"]["name"] == "myapp"
        assert config["defaults"]["tags"] == ["web", "api", "python"]
        assert config["defaults"]["database"]["credentials"]["username"] == "admin"
        assert len(config["defaults"]["servers"]) == 2
        assert config["defaults"]["servers"][0]["name"] == "web1"
        assert config["profiles"]["development"]["database"]["host"] == "dev-db"

    def test_toml_error_handling(self, tmp_path):
        """Test TOML error handling for invalid files."""
        # Create invalid TOML file
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[defaults
invalid_toml = "missing closing bracket"
"""
        )

        loader = ConfigLoader()

        with pytest.raises(ConfigFormatError) as exc_info:
            loader.load_config_file(config_file)

        assert "Invalid TOML" in str(exc_info.value)
        assert str(config_file) in str(exc_info.value)

    def test_toml_extension_in_discovery(self):
        """Test that TOML extension is included in default discovery."""
        from profile_config.discovery import ConfigDiscovery

        discovery = ConfigDiscovery("myapp")
        assert "toml" in discovery.extensions

    @pytest.mark.skipif(not HAS_TOML, reason="TOML support not available")
    def test_toml_without_toml_library(self, tmp_path, monkeypatch):
        """Test error handling when TOML library is not available."""
        # Mock HAS_TOML to False
        import profile_config.loader

        monkeypatch.setattr(profile_config.loader, "HAS_TOML", False)

        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[defaults]
test = "value"
"""
        )

        loader = ConfigLoader()

        with pytest.raises(ConfigFormatError) as exc_info:
            loader.load_config_file(config_file)

        assert "TOML support not available" in str(exc_info.value)
        assert "pip install tomli" in str(exc_info.value)
