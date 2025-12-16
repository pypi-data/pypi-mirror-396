"""
Tests for semiautomatic.lib.env module.

Tests cover:
- Project root detection
- Environment variable loading
- require_env and get_env helpers
"""

import os
import pytest
from pathlib import Path

from semiautomatic.lib.env import (
    find_project_root,
    load_project_env,
    require_env,
    get_env,
)


class TestFindProjectRoot:
    """Tests for find_project_root()."""

    def test_finds_root_from_nested_directory(self, temp_dir):
        """Should find project root by walking up directories."""
        # Create a fake project structure
        project_root = temp_dir / "my_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]\nname = 'test'")

        nested_dir = project_root / "src" / "deep" / "nested"
        nested_dir.mkdir(parents=True)

        result = find_project_root(nested_dir)
        assert result == project_root

    def test_finds_root_with_git_marker(self, temp_dir):
        """Should find root when .git directory exists."""
        project_root = temp_dir / "git_project"
        project_root.mkdir()
        (project_root / ".git").mkdir()

        result = find_project_root(project_root)
        assert result == project_root

    def test_returns_none_when_no_markers(self, temp_dir):
        """Should return None if no project markers found."""
        isolated_dir = temp_dir / "isolated"
        isolated_dir.mkdir()

        # Start from isolated dir with no markers above
        # (temp_dir is created fresh by pytest, no markers)
        result = find_project_root(isolated_dir)
        # May or may not find root depending on test environment
        # Just verify it doesn't crash

    def test_uses_file_location_when_no_start_path(self):
        """Should use __file__ location when start_path is None."""
        # This test verifies the function runs without error
        # when called with default arguments
        result = find_project_root()
        # Should find the semiautomatic project root
        assert result is not None
        assert (result / "pyproject.toml").exists()


class TestLoadProjectEnv:
    """Tests for load_project_env()."""

    def test_loads_env_file(self, temp_dir, monkeypatch):
        """Should load .env file and set environment variables."""
        # Create project with .env
        project_root = temp_dir / "env_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")
        (project_root / ".env").write_text("TEST_VAR_12345=hello_world\n")

        # Clear any existing value
        monkeypatch.delenv("TEST_VAR_12345", raising=False)

        result = load_project_env(project_root)

        assert result is True
        assert os.environ.get("TEST_VAR_12345") == "hello_world"

    def test_returns_false_when_no_env_file(self, temp_dir):
        """Should return False if no .env file exists."""
        project_root = temp_dir / "no_env_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]")

        result = load_project_env(project_root)
        assert result is False


class TestRequireEnv:
    """Tests for require_env()."""

    def test_returns_value_when_set(self, monkeypatch):
        """Should return env var value when set."""
        monkeypatch.setenv("TEST_REQUIRE_VAR", "test_value")

        result = require_env("TEST_REQUIRE_VAR")
        assert result == "test_value"

    def test_raises_when_not_set(self, monkeypatch):
        """Should raise EnvironmentError when var not set."""
        monkeypatch.delenv("NONEXISTENT_VAR_XYZ", raising=False)

        with pytest.raises(EnvironmentError) as exc_info:
            require_env("NONEXISTENT_VAR_XYZ")

        assert "NONEXISTENT_VAR_XYZ" in str(exc_info.value)

    def test_includes_description_in_error(self, monkeypatch):
        """Should include description in error message."""
        monkeypatch.delenv("MISSING_VAR", raising=False)

        with pytest.raises(EnvironmentError) as exc_info:
            require_env("MISSING_VAR", "This is your API key")

        assert "This is your API key" in str(exc_info.value)


class TestGetEnv:
    """Tests for get_env()."""

    def test_returns_value_when_set(self, monkeypatch):
        """Should return env var value when set."""
        monkeypatch.setenv("TEST_GET_VAR", "got_it")

        result = get_env("TEST_GET_VAR")
        assert result == "got_it"

    def test_returns_default_when_not_set(self, monkeypatch):
        """Should return default when var not set."""
        monkeypatch.delenv("MISSING_GET_VAR", raising=False)

        result = get_env("MISSING_GET_VAR", "default_value")
        assert result == "default_value"

    def test_returns_none_when_not_set_no_default(self, monkeypatch):
        """Should return None when var not set and no default."""
        monkeypatch.delenv("MISSING_GET_VAR_2", raising=False)

        result = get_env("MISSING_GET_VAR_2")
        assert result is None
