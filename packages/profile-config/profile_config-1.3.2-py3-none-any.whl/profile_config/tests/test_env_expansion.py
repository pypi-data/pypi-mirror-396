"""
Tests for environment variable expansion and command execution features.
"""

import contextlib
import os
import platform
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


class TestEnvironmentVariableExpansion:
    """Test ${env:VAR} syntax for reading existing environment variables."""

    def test_env_expansion_existing_var(self):
        """Test expanding existing environment variable."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            # Set up test environment variable
            os.environ["TEST_EXISTING_VAR"] = "existing_value"

            config_file.write_text(
                """
defaults:
  env_vars:
    READ_FROM_ENV: "${env:TEST_EXISTING_VAR}"
"""
            )

            os.environ.pop("READ_FROM_ENV", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Should read from existing environment
                assert os.environ.get("READ_FROM_ENV") == "existing_value"

            finally:
                os.environ.pop("TEST_EXISTING_VAR", None)
                os.environ.pop("READ_FROM_ENV", None)

    def test_env_expansion_missing_var(self):
        """Test expanding missing environment variable (should result in empty/None)."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            # Ensure variable doesn't exist
            os.environ.pop("NONEXISTENT_VAR", None)

            config_file.write_text(
                """
defaults:
  env_vars:
    FROM_MISSING: "${env:NONEXISTENT_VAR}"
"""
            )

            os.environ.pop("FROM_MISSING", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Missing env var should result in empty string or not be set
                result = os.environ.get("FROM_MISSING")
                # OmegaConf converts None to empty string
                assert result == "" or result is None

            finally:
                os.environ.pop("FROM_MISSING", None)

    def test_env_expansion_in_interpolation(self):
        """Test environment variable expansion combined with regular interpolation."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            os.environ["USER_HOME"] = "/home/testuser"

            config_file.write_text(
                """
defaults:
  app_name: myapp
  env_vars:
    APP_PATH: "${env:USER_HOME}/${app_name}"
"""
            )

            os.environ.pop("APP_PATH", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Should combine env expansion and config interpolation
                assert os.environ.get("APP_PATH") == "/home/testuser/myapp"

            finally:
                os.environ.pop("USER_HOME", None)
                os.environ.pop("APP_PATH", None)

    def test_env_expansion_multiple_vars(self):
        """Test expanding multiple environment variables."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            os.environ["VAR1"] = "value1"
            os.environ["VAR2"] = "value2"
            os.environ["VAR3"] = "value3"

            config_file.write_text(
                """
defaults:
  env_vars:
    COPY1: "${env:VAR1}"
    COPY2: "${env:VAR2}"
    COPY3: "${env:VAR3}"
"""
            )

            os.environ.pop("COPY1", None)
            os.environ.pop("COPY2", None)
            os.environ.pop("COPY3", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                assert os.environ.get("COPY1") == "value1"
                assert os.environ.get("COPY2") == "value2"
                assert os.environ.get("COPY3") == "value3"

            finally:
                for var in ["VAR1", "VAR2", "VAR3", "COPY1", "COPY2", "COPY3"]:
                    os.environ.pop(var, None)


class TestCommandExecution:
    """Test $(command) syntax for executing shell commands."""

    def test_command_execution_basic(self):
        """Test basic command execution."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  env_vars:
    CMD_OUTPUT: "$(echo test_value)"
"""
            )

            os.environ.pop("CMD_OUTPUT", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Command should be executed
                assert os.environ.get("CMD_OUTPUT") == "test_value"

            finally:
                os.environ.pop("CMD_OUTPUT", None)

    def test_command_execution_with_env_expansion(self):
        """Test command execution with environment variable expansion in command."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            os.environ["TEST_VAR"] = "from_env"

            # Platform-specific echo command
            if platform.system() == "Windows":
                cmd = "$(echo %TEST_VAR%)"
            else:
                cmd = "$(echo $TEST_VAR)"

            config_file.write_text(
                f"""
defaults:
  env_vars:
    EXPANDED_CMD: "{cmd}"
"""
            )

            os.environ.pop("EXPANDED_CMD", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Command should execute with env var expansion
                assert os.environ.get("EXPANDED_CMD") == "from_env"

            finally:
                os.environ.pop("TEST_VAR", None)
                os.environ.pop("EXPANDED_CMD", None)

    def test_command_execution_failed_command(self):
        """Test that failed commands result in variable not being set."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  other_var: "should_be_set"
  env_vars:
    FAILED_CMD: "$(nonexistent_command_xyz)"
    GOOD_VAR: "normal_value"
"""
            )

            os.environ.pop("FAILED_CMD", None)
            os.environ.pop("GOOD_VAR", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Failed command should not set variable
                assert "FAILED_CMD" not in os.environ

                # Other variables should still be set
                assert os.environ.get("GOOD_VAR") == "normal_value"
                assert config["other_var"] == "should_be_set"

            finally:
                os.environ.pop("FAILED_CMD", None)
                os.environ.pop("GOOD_VAR", None)

    def test_command_execution_empty_output(self):
        """Test that commands with empty output result in variable not being set."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            # Command that produces no output
            if platform.system() == "Windows":
                empty_cmd = "$(echo.)"  # Windows empty echo
            else:
                empty_cmd = "$(true)"  # Unix command with no output

            config_file.write_text(
                f"""
defaults:
  env_vars:
    EMPTY_CMD: "{empty_cmd}"
    GOOD_VAR: "normal_value"
"""
            )

            os.environ.pop("EMPTY_CMD", None)
            os.environ.pop("GOOD_VAR", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Empty output should not set variable
                assert "EMPTY_CMD" not in os.environ

                # Other variables should still be set
                assert os.environ.get("GOOD_VAR") == "normal_value"

            finally:
                os.environ.pop("EMPTY_CMD", None)
                os.environ.pop("GOOD_VAR", None)

    @pytest.mark.skipif(
        platform.system() == "Windows", reason="Unix-specific test with sleep"
    )
    def test_command_execution_timeout(self):
        """Test that commands exceeding timeout are terminated."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  env_vars:
    TIMEOUT_CMD: "$(sleep 10 && echo done)"
    GOOD_VAR: "normal_value"
"""
            )

            os.environ.pop("TIMEOUT_CMD", None)
            os.environ.pop("GOOD_VAR", None)

            try:
                resolver = ProfileConfigResolver(
                    "myapp",
                    search_home=False,
                    command_timeout=0.5,  # 0.5 second timeout
                )
                config = resolver.resolve()

                # Timeout command should not set variable
                assert "TIMEOUT_CMD" not in os.environ

                # Other variables should still be set
                assert os.environ.get("GOOD_VAR") == "normal_value"

            finally:
                os.environ.pop("TIMEOUT_CMD", None)
                os.environ.pop("GOOD_VAR", None)

    def test_command_execution_multiple_commands(self):
        """Test multiple command substitutions."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  env_vars:
    CMD1: "$(echo value1)"
    CMD2: "$(echo value2)"
    CMD3: "$(echo value3)"
"""
            )

            for var in ["CMD1", "CMD2", "CMD3"]:
                os.environ.pop(var, None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                assert os.environ.get("CMD1") == "value1"
                assert os.environ.get("CMD2") == "value2"
                assert os.environ.get("CMD3") == "value3"

            finally:
                for var in ["CMD1", "CMD2", "CMD3"]:
                    os.environ.pop(var, None)

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix-specific test")
    def test_command_execution_with_pipes(self):
        """Test command execution with pipes and complex commands."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  env_vars:
    PIPED_CMD: "$(echo 'hello world' | tr ' ' '_')"
"""
            )

            os.environ.pop("PIPED_CMD", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                assert os.environ.get("PIPED_CMD") == "hello_world"

            finally:
                os.environ.pop("PIPED_CMD", None)


class TestCombinedFeatures:
    """Test combined usage of env expansion and command execution."""

    def test_combined_env_and_command(self):
        """Test using both ${env:VAR} and $(command) in same config."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            os.environ["EXISTING_VAR"] = "existing_value"

            config_file.write_text(
                """
defaults:
  env_vars:
    FROM_ENV: "${env:EXISTING_VAR}"
    FROM_CMD: "$(echo command_value)"
    COMBINED: "${env:EXISTING_VAR}_$(echo suffix)"
"""
            )

            for var in ["FROM_ENV", "FROM_CMD", "COMBINED"]:
                os.environ.pop(var, None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                assert os.environ.get("FROM_ENV") == "existing_value"
                assert os.environ.get("FROM_CMD") == "command_value"
                assert os.environ.get("COMBINED") == "existing_value_suffix"

            finally:
                os.environ.pop("EXISTING_VAR", None)
                for var in ["FROM_ENV", "FROM_CMD", "COMBINED"]:
                    os.environ.pop(var, None)

    def test_command_using_env_resolver(self):
        """Test command that uses environment variable via shell expansion."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            os.environ["BASE_VALUE"] = "base"

            # Platform-specific echo - use curly braces to properly delimit variable
            if platform.system() == "Windows":
                cmd = "$(echo %BASE_VALUE%_extended)"
            else:
                cmd = "$(echo ${BASE_VALUE}_extended)"

            config_file.write_text(
                f"""
defaults:
  env_vars:
    RESULT: "{cmd}"
"""
            )

            os.environ.pop("RESULT", None)

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Command should access existing env var
                assert os.environ.get("RESULT") == "base_extended"

            finally:
                os.environ.pop("BASE_VALUE", None)
                os.environ.pop("RESULT", None)

    def test_profile_with_mixed_features(self):
        """Test profile override with both env expansion and commands."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            os.environ["PROFILE_VAR"] = "production"

            config_file.write_text(
                """
defaults:
  env_vars:
    ENV_TYPE: "${env:PROFILE_VAR}"

profiles:
  production:
    env_vars:
      ENV_TYPE: "${env:PROFILE_VAR}_override"
      BUILD_ID: "$(echo build_123)"
"""
            )

            for var in ["ENV_TYPE", "BUILD_ID"]:
                os.environ.pop(var, None)

            try:
                resolver = ProfileConfigResolver(
                    "myapp",
                    profile="production",
                    search_home=False,
                )
                config = resolver.resolve()

                assert os.environ.get("ENV_TYPE") == "production_override"
                assert os.environ.get("BUILD_ID") == "build_123"

            finally:
                os.environ.pop("PROFILE_VAR", None)
                for var in ["ENV_TYPE", "BUILD_ID"]:
                    os.environ.pop(var, None)


class TestGlobalCommandExpansion:
    """Test that $(command) and ${env:VAR} work in ANY configuration value."""

    def test_commands_in_regular_config_values(self):
        """Test command execution in regular configuration values (not just env_vars)."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            os.environ["TEST_USER"] = "testuser"

            config_file.write_text(
                """
defaults:
  project_name: "$(echo myproject)"
  user: "${env:TEST_USER}"
  database:
    host: "db.example.com"
    name: "$(echo myproject)_db"
  servers:
    - "server1.$(hostname)"
    - "server2.$(hostname)"
"""
            )

            try:
                resolver = ProfileConfigResolver("myapp", search_home=False)
                config = resolver.resolve()

                # Commands should work in regular config
                assert config["project_name"] == "myproject"
                assert config["user"] == "testuser"
                assert config["database"]["name"] == "myproject_db"
                assert len(config["servers"]) == 2
                assert config["servers"][0].startswith("server1.")
                assert config["servers"][1].startswith("server2.")

            finally:
                os.environ.pop("TEST_USER", None)

    @pytest.mark.skipif(platform.system() == "Windows", reason="Unix-specific test")
    def test_basename_pwd_pattern(self):
        """Test the specific pattern: $(basename ${PWD})"""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            # Get the expected basename
            expected_basename = Path(tmpdir).name

            config_file.write_text(
                """
defaults:
  current_dir: "$(basename ${PWD})"
  username: "${env:USER}"
"""
            )

            resolver = ProfileConfigResolver("myapp", search_home=False)
            config = resolver.resolve()

            # Should get basename of current directory
            assert config["current_dir"] == expected_basename
            # Should get current user
            assert config["username"] == os.environ.get("USER")

    def test_commands_in_profiles(self):
        """Test that commands work in profile-specific values."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  environment: "$(echo base)"

profiles:
  development:
    environment: "$(echo dev)"
    debug: true

  production:
    environment: "$(echo prod)"
    debug: false
"""
            )

            # Test development profile
            resolver = ProfileConfigResolver(
                "myapp", profile="development", search_home=False
            )
            config = resolver.resolve()
            assert config["environment"] == "dev"
            assert config["debug"] is True

            # Test production profile
            resolver = ProfileConfigResolver(
                "myapp", profile="production", search_home=False
            )
            config = resolver.resolve()
            assert config["environment"] == "prod"
            assert config["debug"] is False

    def test_commands_with_interpolation(self):
        """Test commands combined with OmegaConf interpolation."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  app_name: myapp
  environment: "$(echo production)"
  full_name: "${app_name}_${environment}"
  database_url: "postgresql://localhost/${app_name}_$(echo db)"
"""
            )

            resolver = ProfileConfigResolver("myapp", search_home=False)
            config = resolver.resolve()

            # Commands expand first, then OmegaConf interpolation
            assert config["environment"] == "production"
            assert config["full_name"] == "myapp_production"
            assert config["database_url"] == "postgresql://localhost/myapp_db"

    def test_failed_command_in_regular_config(self):
        """Test that failed commands in regular config result in key being omitted."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  good_value: "static"
  bad_value: "$(nonexistent_command_xyz)"
  another_good: "also_static"
"""
            )

            resolver = ProfileConfigResolver("myapp", search_home=False)
            config = resolver.resolve()

            # Failed command should not be in config
            assert "good_value" in config
            assert "bad_value" not in config
            assert "another_good" in config
            assert config["good_value"] == "static"
            assert config["another_good"] == "also_static"

    def test_commands_in_nested_structures(self):
        """Test commands work deeply nested in configuration."""
        with tempfile.TemporaryDirectory() as tmpdir, chdir_context(tmpdir):
            config_dir = Path(tmpdir) / "myapp"
            config_dir.mkdir()
            config_file = config_dir / "config.yaml"

            config_file.write_text(
                """
defaults:
  level1:
    level2:
      level3:
        value: "$(echo deeply_nested)"
      another: "$(echo level2_value)"
    simple: "$(echo level1_value)"
"""
            )

            resolver = ProfileConfigResolver("myapp", search_home=False)
            config = resolver.resolve()

            assert config["level1"]["level2"]["level3"]["value"] == "deeply_nested"
            assert config["level1"]["level2"]["another"] == "level2_value"
            assert config["level1"]["simple"] == "level1_value"
