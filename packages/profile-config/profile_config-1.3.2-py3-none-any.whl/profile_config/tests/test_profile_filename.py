"""
Tests for custom profile filename feature.
"""

import os
from pathlib import Path

import pytest

from profile_config import ProfileConfigResolver
from profile_config.exceptions import ConfigNotFoundError


class TestProfileFilename:
    """Test custom profile filename functionality."""

    def test_default_profile_filename(self, tmp_path):
        """Test that default 'config' filename still works."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        config_file = config_dir / "config.yaml"
        config_file.write_text(
            """
defaults:
  value: 100
  name: default_test

profiles:
  dev:
    debug: true
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver("myapp", profile="dev")
        config = resolver.resolve()

        assert config["value"] == 100
        assert config["name"] == "default_test"
        assert config["debug"] is True

    def test_custom_profile_filename_yaml(self, tmp_path):
        """Test using custom profile filename with YAML."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create settings.yaml instead of config.yaml
        config_file = config_dir / "settings.yaml"
        config_file.write_text(
            """
defaults:
  value: 42
  source: settings

profiles:
  dev:
    debug: true
    log_level: DEBUG
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp", profile="dev", profile_filename="settings"
        )
        config = resolver.resolve()

        assert config["value"] == 42
        assert config["source"] == "settings"
        assert config["debug"] is True
        assert config["log_level"] == "DEBUG"

    def test_custom_profile_filename_json(self, tmp_path):
        """Test using custom profile filename with JSON."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create app.json
        config_file = config_dir / "app.json"
        config_file.write_text(
            """
{
  "defaults": {
    "type": "json",
    "port": 8080
  },
  "profiles": {
    "prod": {
      "port": 443,
      "ssl": true
    }
  }
}
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp", profile="prod", profile_filename="app"
        )
        config = resolver.resolve()

        assert config["type"] == "json"
        assert config["port"] == 443
        assert config["ssl"] is True

    def test_custom_profile_filename_toml(self, tmp_path):
        """Test using custom profile filename with TOML."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create database.toml
        config_file = config_dir / "database.toml"
        config_file.write_text(
            """
[defaults]
host = "localhost"
port = 5432

[profiles.production]
host = "prod-db.example.com"
pool_size = 20
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp", profile="production", profile_filename="database"
        )
        config = resolver.resolve()

        assert config["host"] == "prod-db.example.com"
        assert config["port"] == 5432
        assert config["pool_size"] == 20

    def test_custom_filename_multiple_extensions(self, tmp_path):
        """Test that custom filename searches all extensions."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create only .yml version (not .yaml)
        config_file = config_dir / "settings.yml"
        config_file.write_text(
            """
defaults:
  found: true
  extension: yml
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver("myapp", profile_filename="settings")
        config = resolver.resolve()

        assert config["found"] is True
        assert config["extension"] == "yml"

    def test_custom_filename_precedence(self, tmp_path):
        """Test that extension precedence works with custom filename."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create both .yaml and .json with different values
        yaml_file = config_dir / "settings.yaml"
        yaml_file.write_text(
            """
defaults:
  source: yaml
  value: 100
"""
        )

        json_file = config_dir / "settings.json"
        json_file.write_text(
            """
{
  "defaults": {
    "source": "json",
    "value": 200
  }
}
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver("myapp", profile_filename="settings")
        config = resolver.resolve()

        # YAML should take precedence (first in default extensions list)
        assert config["source"] == "yaml"
        assert config["value"] == 100

    def test_custom_filename_hierarchical_discovery(self, tmp_path):
        """Test hierarchical discovery with custom filename."""
        # Create nested directory structure
        parent_config = tmp_path / "myapp"
        parent_config.mkdir()
        (parent_config / "app.yaml").write_text(
            """
defaults:
  level: parent
  timeout: 30
"""
        )

        child_dir = tmp_path / "subdir"
        child_dir.mkdir()
        child_config = child_dir / "myapp"
        child_config.mkdir()
        (child_config / "app.yaml").write_text(
            """
defaults:
  level: child
  retries: 3
"""
        )

        os.chdir(child_dir)
        resolver = ProfileConfigResolver("myapp", profile_filename="app")
        config = resolver.resolve()

        # Child should override parent
        assert config["level"] == "child"
        assert config["retries"] == 3
        assert config["timeout"] == 30  # From parent

    def test_custom_filename_not_found(self, tmp_path):
        """Test error when custom filename not found."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create config.yaml but search for settings
        config_file = config_dir / "config.yaml"
        config_file.write_text("defaults: {}")

        os.chdir(tmp_path)

        with pytest.raises(ConfigNotFoundError) as exc_info:
            resolver = ProfileConfigResolver("myapp", profile_filename="settings")
            resolver.resolve()

        error_msg = str(exc_info.value)
        assert "settings" in error_msg
        assert "myapp" in error_msg

    def test_custom_filename_with_overrides(self, tmp_path):
        """Test custom filename works with overrides."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        config_file = config_dir / "settings.yaml"
        config_file.write_text(
            """
defaults:
  value: 100
  debug: false
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp",
            profile_filename="settings",
            overrides={"value": 200, "debug": True},
        )
        config = resolver.resolve()

        assert config["value"] == 200  # Overridden
        assert config["debug"] is True  # Overridden

    def test_custom_filename_with_inheritance(self, tmp_path):
        """Test custom filename works with profile inheritance."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        config_file = config_dir / "app.yaml"
        config_file.write_text(
            """
profiles:
  base:
    timeout: 30
    retries: 3

  dev:
    inherits: base
    debug: true
    timeout: 60

  staging:
    inherits: dev
    debug: false
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp", profile="staging", profile_filename="app"
        )
        config = resolver.resolve()

        assert config["timeout"] == 60  # From dev (overrides base)
        assert config["retries"] == 3  # From base
        assert config["debug"] is False  # From staging (overrides dev)

    def test_custom_filename_with_interpolation(self, tmp_path):
        """Test custom filename works with variable interpolation."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        config_file = config_dir / "settings.yaml"
        config_file.write_text(
            """
defaults:
  app_name: myapp
  base_path: /opt/${app_name}
  data_path: ${base_path}/data

profiles:
  dev:
    base_path: /tmp/${app_name}
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp", profile="dev", profile_filename="settings"
        )
        config = resolver.resolve()

        assert config["app_name"] == "myapp"
        assert config["base_path"] == "/tmp/myapp"
        assert config["data_path"] == "/tmp/myapp/data"

    def test_custom_filename_list_profiles(self, tmp_path):
        """Test list_profiles works with custom filename."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        config_file = config_dir / "app.yaml"
        config_file.write_text(
            """
profiles:
  development:
    debug: true
  staging:
    debug: false
  production:
    debug: false
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver("myapp", profile_filename="app")
        profiles = resolver.list_profiles()

        assert set(profiles) == {"development", "staging", "production"}

    def test_custom_filename_get_config_files(self, tmp_path):
        """Test get_config_files returns correct paths with custom filename."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        config_file = config_dir / "settings.yaml"
        config_file.write_text("defaults: {}")

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver("myapp", profile_filename="settings")
        files = resolver.get_config_files()

        assert len(files) == 1
        assert files[0].name == "settings.yaml"
        assert files[0].parent.name == "myapp"

    def test_custom_filename_search_home_disabled(self, tmp_path):
        """Test custom filename with home directory search disabled."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        config_file = config_dir / "app.yaml"
        config_file.write_text(
            """
defaults:
  value: 42
"""
        )

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp", profile_filename="app", search_home=False
        )
        config = resolver.resolve()

        assert config["value"] == 42

    def test_custom_filename_with_custom_extensions(self, tmp_path):
        """Test custom filename with custom extensions list."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create only JSON file
        config_file = config_dir / "settings.json"
        config_file.write_text('{"defaults": {"format": "json"}}')

        os.chdir(tmp_path)
        resolver = ProfileConfigResolver(
            "myapp",
            profile_filename="settings",
            extensions=["json"],  # Only search for JSON
        )
        config = resolver.resolve()

        assert config["format"] == "json"

    def test_empty_profile_filename_error(self, tmp_path):
        """Test that empty profile filename is handled."""
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        # Create .yaml file (empty filename)
        config_file = config_dir / ".yaml"
        config_file.write_text("defaults: {}")

        os.chdir(tmp_path)

        with pytest.raises(ConfigNotFoundError):
            resolver = ProfileConfigResolver("myapp", profile_filename="")
            resolver.resolve()
