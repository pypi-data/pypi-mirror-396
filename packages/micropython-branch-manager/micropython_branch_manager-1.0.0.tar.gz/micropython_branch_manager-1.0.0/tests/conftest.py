"""Shared pytest fixtures for micropython-branch-manager tests."""

import json
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from micropython_branch_manager.git import GitRepo

# Sample test data constants
SAMPLE_CONFIG_DICT = {
    "integration_branch": "main",
    "remotes": {
        "upstream": "https://github.com/micropython/micropython.git",
        "origin": "git@github.com:testuser/micropython.git",
    },
    "branches": [
        {
            "name": "feature-1",
            "remote": "origin",
            "pr_url": "https://github.com/micropython/micropython/pull/12345",
            "pr_number": 12345,
            "title": "Add feature 1",
        },
        {
            "name": "feature-2",
            "remote": "origin",
            "pr_url": "https://github.com/micropython/micropython/pull/12346",
            "pr_number": 12346,
            "title": "Add feature 2",
        },
    ],
}

SAMPLE_CONFIG_JSON = json.dumps(
    {
        "_generated_by": "micropython-branch-manager (mbm) - do not edit manually",
        **SAMPLE_CONFIG_DICT,
    },
    indent=2,
)

SAMPLE_GIT_LOG = """Merge branch 'feature-1'

Add feature 1

Merge branch 'feature-2'

Add feature 2

Initial commit"""

SAMPLE_GH_PR_JSON = json.dumps(
    {
        "number": 12345,
        "headRefName": "feature-branch",
        "title": "Add feature",
        "url": "https://github.com/micropython/micropython/pull/12345",
        "state": "OPEN",
        "headRepositoryOwner": {"login": "testuser"},
    }
)


@pytest.fixture
def sample_config_dict():
    """Sample config as dict."""
    return SAMPLE_CONFIG_DICT.copy()


@pytest.fixture
def sample_config_json():
    """Sample config as JSON string."""
    return SAMPLE_CONFIG_JSON


@pytest.fixture
def temp_repo_path(tmp_path):
    """Temporary directory simulating a repo."""
    return tmp_path


@pytest.fixture
def mock_subprocess_run():
    """
    Mock subprocess.run with configurable responses.

    Returns a mock that can be configured per-test with side_effect.
    """
    with patch("subprocess.run") as mock:
        # Default: return successful completion
        mock.return_value = CompletedProcess([], 0, stdout="", stderr="")
        yield mock


@pytest.fixture
def mock_git_repo(tmp_path, mock_subprocess_run):
    """
    GitRepo instance with mocked subprocess.

    Returns tuple of (repo, mock) for call verification.
    """
    with patch("micropython_branch_manager.git.subprocess.run", mock_subprocess_run):
        repo = GitRepo(tmp_path)
        yield repo, mock_subprocess_run


@pytest.fixture
def mock_gh_output():
    """Sample gh CLI JSON responses."""
    return {
        "pr": SAMPLE_GH_PR_JSON,
        "prs_list": json.dumps(
            [
                {
                    "number": 12345,
                    "headRefName": "feature-1",
                    "title": "Add feature 1",
                    "url": "https://github.com/micropython/micropython/pull/12345",
                    "state": "OPEN",
                    "headRepositoryOwner": {"login": "testuser"},
                },
                {
                    "number": 12346,
                    "headRefName": "feature-2",
                    "title": "Add feature 2",
                    "url": "https://github.com/micropython/micropython/pull/12346",
                    "state": "OPEN",
                    "headRepositoryOwner": {"login": "testuser"},
                },
            ]
        ),
    }


@pytest.fixture
def mock_config_file(tmp_path, sample_config_json):
    """Mock config file on disk."""
    config_path = tmp_path / ".micropython-branches.json"
    config_path.write_text(sample_config_json)
    return config_path
