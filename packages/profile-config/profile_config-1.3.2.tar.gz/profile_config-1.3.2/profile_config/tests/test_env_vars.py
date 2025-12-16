"""
Tests for environment variable injection feature.
"""

import contextlib
import os
import tempfile
from pathlib import Path

import pytest

from profile_config import ProfileConfigResolver


@contextlib.contextmanager
def chdir_context(path):
    """Context manager to temporarily change directory."""
    original_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_cwd)


class TestEnvironmentVariables:
    """Test environment variable injection from configuration."""

    def test_apply_env_vars_basic(self):
        """Test basic environment variable application."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            # Create config with env_vars
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  database: testdb
  env_vars:
    TEST_VAR_1: "value1"
    TEST_VAR_2: "value2"
"""
            )

            # Clear any existing test variables
            os.environ.pop("TEST_VAR_1", None)
            os.environ.pop("TEST_VAR_2", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Verify environment variables were set
                assert os.environ.get("TEST_VAR_1") == "value1"
                assert os.environ.get("TEST_VAR_2") == "value2"

                # Verify env_vars not in returned config
                assert "env_vars" not in config
                assert config["database"] == "testdb"

                # Check tracking
                env_info = resolver.get_environment_info()
                assert env_info["applied"]["TEST_VAR_1"] == "value1"
                assert env_info["applied"]["TEST_VAR_2"] == "value2"
                assert len(env_info["skipped"]) == 0

            finally:
                # Cleanup
                os.environ.pop("TEST_VAR_1", None)
                os.environ.pop("TEST_VAR_2", None)

    def test_apply_env_vars_with_interpolation(self):
        """Test environment variables with interpolation."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  app_name: myapp
  base_path: /opt/apps
  env_vars:
    APP_NAME: "${app_name}"
    APP_PATH: "${base_path}/${app_name}"
"""
            )

            os.environ.pop("APP_NAME", None)
            os.environ.pop("APP_PATH", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Verify interpolation worked
                assert os.environ.get("APP_NAME") == "myapp"
                assert os.environ.get("APP_PATH") == "/opt/apps/myapp"

            finally:
                os.environ.pop("APP_NAME", None)
                os.environ.pop("APP_PATH", None)

    def test_apply_env_vars_profile_override(self):
        """Test environment variables with profile overrides."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  env_vars:
    LOG_LEVEL: "INFO"
    APP_ENV: "default"

profiles:
  production:
    env_vars:
      LOG_LEVEL: "WARNING"
      APP_ENV: "production"
"""
            )

            os.environ.pop("LOG_LEVEL", None)
            os.environ.pop("APP_ENV", None)

            try:
                resolver = ProfileConfigResolver(
                    "myapp", profile="production", search_home=False
                )
                config = resolver.resolve()

                # Verify profile values were used
                assert os.environ.get("LOG_LEVEL") == "WARNING"
                assert os.environ.get("APP_ENV") == "production"

            finally:
                os.environ.pop("LOG_LEVEL", None)
                os.environ.pop("APP_ENV", None)

    def test_override_environment_false(self):
        """Test that existing env vars are not overridden by default."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  env_vars:
    EXISTING_VAR: "from_config"
    NEW_VAR: "from_config"
"""
            )

            # Set existing variable
            os.environ["EXISTING_VAR"] = "from_environment"
            os.environ.pop("NEW_VAR", None)

            try:
                resolver = ProfileConfigResolver(
                    "myapp",
                    search_home=False,
                    override_environment=False,  # default
                )
                config = resolver.resolve()

                # Existing var should NOT be overridden
                assert os.environ.get("EXISTING_VAR") == "from_environment"
                # New var should be set
                assert os.environ.get("NEW_VAR") == "from_config"

                # Check tracking
                env_info = resolver.get_environment_info()
                assert "NEW_VAR" in env_info["applied"]
                assert "EXISTING_VAR" in env_info["skipped"]
                assert env_info["skipped"]["EXISTING_VAR"] == "from_config"

            finally:
                os.environ.pop("EXISTING_VAR", None)
                os.environ.pop("NEW_VAR", None)

    def test_override_environment_true(self):
        """Test that existing env vars are overridden when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  env_vars:
    EXISTING_VAR: "from_config"
"""
            )

            # Set existing variable
            os.environ["EXISTING_VAR"] = "from_environment"

            try:
                resolver = ProfileConfigResolver(
                    "myapp", search_home=False, override_environment=True
                )
                config = resolver.resolve()

                # Existing var SHOULD be overridden
                assert os.environ.get("EXISTING_VAR") == "from_config"

                # Check tracking
                env_info = resolver.get_environment_info()
                assert "EXISTING_VAR" in env_info["applied"]
                assert len(env_info["skipped"]) == 0

            finally:
                os.environ.pop("EXISTING_VAR", None)

    def test_apply_environment_disabled(self):
        """Test disabling environment variable application."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  env_vars:
    SHOULD_NOT_BE_SET: "value"
"""
            )

            os.environ.pop("SHOULD_NOT_BE_SET", None)

            try:
                resolver = ProfileConfigResolver(
                    "myapp", search_home=False, apply_environment=False
                )
                config = resolver.resolve()

                # Variable should NOT be set
                assert "SHOULD_NOT_BE_SET" not in os.environ

                # env_vars should still be REMOVED from config (processed but not applied)
                assert "env_vars" not in config

            finally:
                os.environ.pop("SHOULD_NOT_BE_SET", None)

    def test_custom_environment_key(self):
        """Test using a custom key name for environment variables."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  exports:
    CUSTOM_VAR: "custom_value"
"""
            )

            os.environ.pop("CUSTOM_VAR", None)

            try:
                resolver = ProfileConfigResolver(
                    "myapp", search_home=False, environment_key="exports"
                )
                config = resolver.resolve()

                # Variable should be set
                assert os.environ.get("CUSTOM_VAR") == "custom_value"
                # Custom key should be removed from config
                assert "exports" not in config

            finally:
                os.environ.pop("CUSTOM_VAR", None)

    def test_env_vars_with_overrides(self):
        """Test environment variables with runtime overrides."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  base_url: "http://localhost"
  env_vars:
    BASE_URL: "${base_url}"
"""
            )

            os.environ.pop("BASE_URL", None)

            try:
                resolver = ProfileConfigResolver(
                    "myapp",
                    search_home=False,
                    overrides={"base_url": "http://production.example.com"},
                )
                config = resolver.resolve()

                # Override should affect env var through interpolation
                assert os.environ.get("BASE_URL") == "http://production.example.com"

            finally:
                os.environ.pop("BASE_URL", None)

    def test_env_vars_type_conversion(self):
        """Test that non-string values are converted to strings."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  env_vars:
    PORT: 8080
    DEBUG: true
    RATIO: 3.14
"""
            )

            os.environ.pop("PORT", None)
            os.environ.pop("DEBUG", None)
            os.environ.pop("RATIO", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # All values should be strings
                assert os.environ.get("PORT") == "8080"
                assert os.environ.get("DEBUG") == "True"
                assert os.environ.get("RATIO") == "3.14"

            finally:
                os.environ.pop("PORT", None)
                os.environ.pop("DEBUG", None)
                os.environ.pop("RATIO", None)

    def test_env_vars_empty_section(self):
        """Test handling of empty env_vars section."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  database: testdb
  env_vars: {}
"""
            )

            resolver = ProfileConfigResolver("myapp", search_home=False)
            config = resolver.resolve()

            # Should work fine with empty section
            assert "env_vars" not in config
            assert config["database"] == "testdb"

    def test_env_vars_missing_section(self):
        """Test handling when env_vars section is missing."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  database: testdb
"""
            )

            resolver = ProfileConfigResolver("myapp", search_home=False)
            config = resolver.resolve()

            # Should work fine without env_vars section
            assert config["database"] == "testdb"
            env_info = resolver.get_environment_info()
            assert len(env_info["applied"]) == 0
            assert len(env_info["skipped"]) == 0

    def test_env_vars_invalid_type(self):
        """Test handling of invalid env_vars type (should log warning)."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  database: testdb
  env_vars: "not_a_dict"
"""
            )

            resolver = ProfileConfigResolver("myapp", search_home=False)

            # Should not raise, just log warning
            config = resolver.resolve()

            # env_vars should be removed even if invalid type
            assert "env_vars" not in config
            assert config["database"] == "testdb"
