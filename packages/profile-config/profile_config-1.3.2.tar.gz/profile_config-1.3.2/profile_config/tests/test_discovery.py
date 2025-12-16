"""Tests for configuration file discovery."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from profile_config.discovery import ConfigDiscovery
from profile_config.exceptions import ConfigNotFoundError


class TestConfigDiscovery:
    """Test configuration file discovery functionality."""

    def test_discover_single_config_file(self, tmp_path):
        """Test discovering a single configuration file."""
        # Create config structure
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("test: value")

        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            discovery = ConfigDiscovery("myapp", search_home=False)
            files = discovery.discover_config_files()

            assert len(files) == 1
            assert files[0].name == "config.yaml"
            assert files[0].parent.name == "myapp"
        finally:
            os.chdir(original_cwd)

    def test_discover_multiple_extensions(self, tmp_path):
        """Test discovering files with different extensions."""
        # Create config structure with multiple files
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()

        yaml_file = config_dir / "config.yaml"
        yaml_file.write_text("yaml: true")

        json_file = config_dir / "config.json"
        json_file.write_text('{"json": true}')

        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            discovery = ConfigDiscovery("myapp", search_home=False)
            files = discovery.discover_config_files()

            assert len(files) == 2
            file_names = {f.name for f in files}
            assert "config.yaml" in file_names
            assert "config.json" in file_names
        finally:
            os.chdir(original_cwd)

    def test_hierarchical_discovery(self, tmp_path):
        """Test hierarchical discovery up directory tree."""
        # Create nested directory structure
        root_config = tmp_path / "myapp"
        root_config.mkdir()
        (root_config / "config.yaml").write_text("level: root")

        sub_dir = tmp_path / "subdir"
        sub_dir.mkdir()
        sub_config = sub_dir / "myapp"
        sub_config.mkdir()
        (sub_config / "config.yaml").write_text("level: sub")

        # Change to subdirectory
        original_cwd = Path.cwd()
        try:
            os.chdir(sub_dir)

            discovery = ConfigDiscovery("myapp", search_home=False)
            files = discovery.discover_config_files()

            # Should find both files, with sub-level first (more specific)
            assert len(files) == 2
            assert "level: sub" in files[0].read_text()
            assert "level: root" in files[1].read_text()
        finally:
            os.chdir(original_cwd)

    def test_home_directory_search(self, tmp_path):
        """Test searching in home directory."""
        # Create config in mock home directory
        home_config = tmp_path / "myapp"
        home_config.mkdir()
        config_file = home_config / "config.yaml"
        config_file.write_text("location: home")

        # Mock home directory
        with patch("pathlib.Path.home", return_value=tmp_path):
            # Create separate work directory that's not under tmp_path
            with tempfile.TemporaryDirectory() as work_dir:
                original_cwd = Path.cwd()
                try:
                    os.chdir(work_dir)

                    discovery = ConfigDiscovery("myapp", search_home=True)
                    files = discovery.discover_config_files()

                    assert len(files) == 1
                    assert "location: home" in files[0].read_text()
                finally:
                    os.chdir(original_cwd)

    def test_no_home_directory_search(self, tmp_path):
        """Test disabling home directory search."""
        # Create config only in mock home directory
        home_config = tmp_path / "myapp"
        home_config.mkdir()
        (home_config / "config.yaml").write_text("location: home")

        # Mock home directory
        with patch("pathlib.Path.home", return_value=tmp_path):
            # Create separate work directory that's not under tmp_path
            with tempfile.TemporaryDirectory() as work_dir:
                original_cwd = Path.cwd()
                try:
                    os.chdir(work_dir)

                    discovery = ConfigDiscovery("myapp", search_home=False)

                    with pytest.raises(ConfigNotFoundError):
                        discovery.discover_config_files()
                finally:
                    os.chdir(original_cwd)

    def test_custom_extensions(self, tmp_path):
        """Test using custom file extensions."""
        # Create config with custom extension
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()
        config_file = config_dir / "config.ini"
        config_file.write_text("[section]\nkey=value")

        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            discovery = ConfigDiscovery("myapp", extensions=["ini"], search_home=False)
            files = discovery.discover_config_files()

            assert len(files) == 1
            assert files[0].name == "config.ini"
        finally:
            os.chdir(original_cwd)

    def test_no_config_found_error(self, tmp_path):
        """Test error when no configuration files are found."""
        # Change to empty directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            discovery = ConfigDiscovery("nonexistent", search_home=False)

            with pytest.raises(ConfigNotFoundError) as exc_info:
                discovery.discover_config_files()

            assert "nonexistent" in str(exc_info.value)
            assert "config.{yaml,yml,json,toml}" in str(exc_info.value)
        finally:
            os.chdir(original_cwd)

    def test_duplicate_removal(self, tmp_path):
        """Test removal of duplicate configuration files."""
        # Create config file
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text("test: value")

        # Create symlink to same file
        symlink_dir = tmp_path / "subdir"
        symlink_dir.mkdir()
        symlink_config_dir = symlink_dir / "myapp"
        symlink_config_dir.symlink_to(config_dir)

        # Change to subdirectory
        original_cwd = Path.cwd()
        try:
            os.chdir(symlink_dir)

            discovery = ConfigDiscovery("myapp", search_home=False)
            files = discovery.discover_config_files()

            # Should only find one file despite symlink
            assert len(files) == 1
        finally:
            os.chdir(original_cwd)

    def test_directory_not_file(self, tmp_path):
        """Test that directories named 'config.yaml' are ignored."""
        # Create directory with config name
        config_dir = tmp_path / "myapp"
        config_dir.mkdir()
        fake_config = config_dir / "config.yaml"
        fake_config.mkdir()  # Create as directory, not file

        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            discovery = ConfigDiscovery("myapp", search_home=False)

            with pytest.raises(ConfigNotFoundError):
                discovery.discover_config_files()
        finally:
            os.chdir(original_cwd)

    def test_search_locations_in_error(self, tmp_path):
        """Test that error message includes searched locations."""
        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            discovery = ConfigDiscovery("myapp", search_home=False)

            with pytest.raises(ConfigNotFoundError) as exc_info:
                discovery.discover_config_files()

            error_msg = str(exc_info.value)
            # On Windows, paths may be repr'd with escaped backslashes
            expected_path = str(tmp_path / "myapp")
            # Normalize both for comparison
            assert expected_path in error_msg.replace("\\\\", "\\")
        finally:
            os.chdir(original_cwd)
