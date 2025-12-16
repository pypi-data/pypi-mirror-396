"""
Tests for flexible overrides feature.
"""

import contextlib
import json
import os
import tempfile
from pathlib import Path

import pytest

from profile_config import ProfileConfigResolver
from profile_config.exceptions import ConfigFormatError


@contextlib.contextmanager
def chdir_context(path):
    """Context manager to temporarily change directory (Windows-safe)."""
    original_cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_cwd)


class TestFlexibleOverrides:
    """Test flexible overrides functionality."""

    def test_override_with_file_path_yaml(self):
        """Test override with YAML file path."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  port: 3000
  debug: false

profiles:
  dev:
    host: localhost
"""
            )

            # Create override file
            override_file = Path(tmpdir) / "overrides.yaml"
            override_file.write_text(
                """
port: 8080
debug: true
extra: from_file
"""
            )

            resolver = ProfileConfigResolver(
                "myapp", profile="dev", overrides=str(override_file), search_home=False
            )
            result = resolver.resolve()

            assert result["port"] == 8080
            assert result["debug"] is True
            assert result["extra"] == "from_file"
            assert result["host"] == "localhost"

    def test_override_with_file_path_json(self):
        """Test override with JSON file path."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
defaults:
  port: 3000

profiles:
  dev:
    host: localhost
"""
            )

            # Create JSON override file
            override_file = Path(tmpdir) / "overrides.json"
            with open(override_file, "w") as f:
                json.dump({"port": 9000, "format": "json"}, f)

            resolver = ProfileConfigResolver(
                "myapp", profile="dev", overrides=str(override_file), search_home=False
            )
            result = resolver.resolve()

            assert result["port"] == 9000
            assert result["format"] == "json"

    def test_override_with_pathlib_path(self):
        """Test override with pathlib.Path object."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
profiles:
  dev:
    port: 3000
"""
            )

            # Create override file
            override_file = Path(tmpdir) / "overrides.yaml"
            override_file.write_text("port: 8080")

            resolver = ProfileConfigResolver(
                "myapp",
                profile="dev",
                overrides=override_file,  # Pass Path object
                search_home=False,
            )
            result = resolver.resolve()

            assert result["port"] == 8080

    def test_override_with_list_of_dicts(self):
        """Test override with list of dictionaries."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
profiles:
  dev:
    port: 3000
    host: localhost
    debug: false
"""
            )

            overrides = [{"port": 8080}, {"debug": True}, {"port": 9000}]  # Should win

            resolver = ProfileConfigResolver(
                "myapp", profile="dev", overrides=overrides, search_home=False
            )
            result = resolver.resolve()

            assert result["port"] == 9000  # Last override wins
            assert result["debug"] is True
            assert result["host"] == "localhost"

    def test_override_with_mixed_list(self):
        """Test override with mixed list of dicts and file paths."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
profiles:
  dev:
    port: 3000
    host: localhost
"""
            )

            # Create override files
            override1 = Path(tmpdir) / "override1.yaml"
            override1.write_text("port: 8080\ndebug: true")

            override2 = Path(tmpdir) / "override2.json"
            with open(override2, "w") as f:
                json.dump({"port": 9000, "extra": "value"}, f)

            overrides = [
                str(override1),  # port: 8080, debug: true
                {"port": 8888},  # port: 8888
                str(override2),  # port: 9000, extra: value (should win)
            ]

            resolver = ProfileConfigResolver(
                "myapp", profile="dev", overrides=overrides, search_home=False
            )
            result = resolver.resolve()

            assert result["port"] == 9000  # Last file wins
            assert result["debug"] is True  # From first file
            assert result["extra"] == "value"  # From last file
            assert result["host"] == "localhost"  # From base config

    def test_override_precedence_order(self):
        """Test that overrides are applied in correct order."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
profiles:
  dev:
    value: base
    a: 1
    b: 2
    c: 3
"""
            )

            overrides = [
                {"value": "first", "a": 10},
                {"value": "second", "b": 20},
                {"value": "third", "c": 30},
            ]

            resolver = ProfileConfigResolver(
                "myapp", profile="dev", overrides=overrides, search_home=False
            )
            result = resolver.resolve()

            assert result["value"] == "third"  # Last override wins
            assert result["a"] == 10  # From first override
            assert result["b"] == 20  # From second override
            assert result["c"] == 30  # From third override

    def test_override_invalid_type(self):
        """Test that invalid override type raises error."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("profiles:\n  dev:\n    port: 3000")

            with pytest.raises(ConfigFormatError, match="Invalid override type"):
                resolver = ProfileConfigResolver(
                    "myapp",
                    profile="dev",
                    overrides=12345,  # Invalid type
                    search_home=False,
                )

    def test_override_invalid_type_in_list(self):
        """Test that invalid type in list raises error."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("profiles:\n  dev:\n    port: 3000")

            with pytest.raises(ConfigFormatError, match="Invalid override type"):
                resolver = ProfileConfigResolver(
                    "myapp",
                    profile="dev",
                    overrides=[{"valid": "dict"}, 12345],  # Second item invalid
                    search_home=False,
                )

    def test_override_missing_file(self):
        """Test that missing override file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("profiles:\n  dev:\n    port: 3000")

            with pytest.raises(ConfigFormatError, match="Override file not found"):
                resolver = ProfileConfigResolver(
                    "myapp",
                    profile="dev",
                    overrides="/nonexistent/file.yaml",
                    search_home=False,
                )

    def test_override_invalid_yaml_file(self):
        """Test that invalid YAML file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text("profiles:\n  dev:\n    port: 3000")

            # Create invalid YAML file
            invalid_file = Path(tmpdir) / "invalid.yaml"
            invalid_file.write_text("{ invalid yaml: [")

            with pytest.raises(ConfigFormatError, match="Failed to load override file"):
                resolver = ProfileConfigResolver(
                    "myapp",
                    profile="dev",
                    overrides=str(invalid_file),
                    search_home=False,
                )

    def test_override_empty_list(self):
        """Test that empty override list works."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
profiles:
  dev:
    port: 3000
"""
            )

            resolver = ProfileConfigResolver(
                "myapp", profile="dev", overrides=[], search_home=False  # Empty list
            )
            result = resolver.resolve()

            assert result["port"] == 3000  # No overrides applied

    def test_override_none(self):
        """Test that None override works (default behavior)."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
profiles:
  dev:
    port: 3000
"""
            )

            resolver = ProfileConfigResolver(
                "myapp",
                profile="dev",
                overrides=None,  # Explicit None
                search_home=False,
            )
            result = resolver.resolve()

            assert result["port"] == 3000

    def test_override_with_interpolation(self):
        """Test that overrides work with variable interpolation."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):

            # Create main config
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"
            config_file.write_text(
                """
profiles:
  dev:
    base_path: /app
    data_path: ${base_path}/data
"""
            )

            overrides = [{"base_path": "/override"}]

            resolver = ProfileConfigResolver(
                "myapp",
                profile="dev",
                overrides=overrides,
                search_home=False,
                enable_interpolation=True,
            )
            result = resolver.resolve()

            assert result["base_path"] == "/override"
            assert result["data_path"] == "/override/data"  # Interpolated with override
