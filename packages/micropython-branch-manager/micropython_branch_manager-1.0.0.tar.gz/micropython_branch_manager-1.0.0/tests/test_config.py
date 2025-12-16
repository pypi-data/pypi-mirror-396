"""Tests for configuration models."""

import json

import pytest

from micropython_branch_manager.config import (
    CONFIG_FILENAME,
    CONFIG_HEADER,
    CONFIG_HEADER_VALUE,
    BranchConfig,
    MicroPythonConfig,
)
from micropython_branch_manager.exceptions import ConfigError


def test_branch_config_defaults():
    """BranchConfig has correct defaults."""
    branch = BranchConfig(name="test-branch")

    assert branch.name == "test-branch"
    assert branch.remote == "origin"
    assert branch.pr_url is None
    assert branch.pr_number is None
    assert branch.title is None


def test_micropython_config_defaults():
    """MicroPythonConfig has correct defaults."""
    config = MicroPythonConfig()

    assert config.integration_branch == "main"
    assert config.remotes == {}
    assert config.branches == []


def test_config_load_existing(tmp_path, sample_config_json):
    """Load config from existing file."""
    config_path = tmp_path / CONFIG_FILENAME
    config_path.write_text(sample_config_json)

    config = MicroPythonConfig.load(tmp_path)

    assert config.integration_branch == "main"
    assert "upstream" in config.remotes
    assert "origin" in config.remotes
    assert len(config.branches) == 2
    assert config.branches[0].name == "feature-1"
    assert config.branches[0].pr_number == 12345


def test_config_load_missing_not_required(tmp_path):
    """Load returns default config if file missing and not required."""
    config = MicroPythonConfig.load(tmp_path, require_exists=False)

    assert config.integration_branch == "main"
    assert config.remotes == {}
    assert config.branches == []


def test_config_load_missing_required(tmp_path):
    """Load raises ConfigError if file missing and required."""
    with pytest.raises(ConfigError) as exc_info:
        MicroPythonConfig.load(tmp_path, require_exists=True)

    assert "No config file found" in str(exc_info.value)
    assert "mbm init" in str(exc_info.value)


def test_config_save(tmp_path):
    """Save config to file with header."""
    config = MicroPythonConfig(
        integration_branch="develop",
        remotes={"upstream": "https://github.com/micropython/micropython.git"},
        branches=[BranchConfig(name="test", remote="upstream", pr_number=123)],
    )

    config.save(tmp_path)

    config_path = tmp_path / CONFIG_FILENAME
    assert config_path.exists()

    saved_data = json.loads(config_path.read_text())
    assert CONFIG_HEADER in saved_data
    assert saved_data[CONFIG_HEADER] == CONFIG_HEADER_VALUE
    assert saved_data["integration_branch"] == "develop"
    assert saved_data["remotes"]["upstream"] == "https://github.com/micropython/micropython.git"
    assert len(saved_data["branches"]) == 1


def test_config_get_branch(sample_config_dict):
    """get_branch returns matching branch or None."""
    config = MicroPythonConfig(**sample_config_dict)

    branch = config.get_branch("feature-1")
    assert branch is not None
    assert branch.name == "feature-1"
    assert branch.pr_number == 12345

    not_found = config.get_branch("non-existent")
    assert not_found is None


def test_config_has_branch(sample_config_dict):
    """has_branch returns True/False correctly."""
    config = MicroPythonConfig(**sample_config_dict)

    assert config.has_branch("feature-1") is True
    assert config.has_branch("feature-2") is True
    assert config.has_branch("non-existent") is False
