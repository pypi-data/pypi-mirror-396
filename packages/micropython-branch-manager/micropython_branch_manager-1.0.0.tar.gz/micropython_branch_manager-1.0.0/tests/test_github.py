"""Tests for GitHub API wrapper."""

from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from micropython_branch_manager.exceptions import GitHubCLINotFound, GitHubError
from micropython_branch_manager.github import GitHubClient


def test_github_client_gh_not_found():
    """GitHubClient raises GitHubCLINotFound if gh missing."""
    with patch("shutil.which", return_value=None):
        with pytest.raises(GitHubCLINotFound) as exc_info:
            GitHubClient()

        assert "GitHub CLI (gh) not found" in str(exc_info.value)
        assert "gh auth login" in str(exc_info.value)


def test_get_pr_by_number(mock_gh_output):
    """get_pr fetches PR by number."""
    with patch("shutil.which", return_value="/usr/bin/gh"), patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout=mock_gh_output["pr"], stderr="")
        client = GitHubClient()

        pr = client.get_pr(12345)

        assert pr.number == 12345
        assert pr.branch == "feature-branch"
        assert pr.title == "Add feature"
        assert pr.url == "https://github.com/micropython/micropython/pull/12345"
        assert pr.state == "OPEN"
        assert pr.author == "testuser"


def test_get_pr_by_branch(mock_gh_output):
    """get_pr fetches PR by branch name."""
    with patch("shutil.which", return_value="/usr/bin/gh"), patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout=mock_gh_output["pr"], stderr="")
        client = GitHubClient()

        pr = client.get_pr("feature-branch")

        assert pr.branch == "feature-branch"
        # Verify gh was called with the branch name
        call_args = mock_run.call_args[0][0]
        assert "feature-branch" in call_args


def test_get_pr_error():
    """get_pr raises GitHubError on failure."""
    with patch("shutil.which", return_value="/usr/bin/gh"), patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 1, stdout="", stderr="PR not found")
        client = GitHubClient()

        with pytest.raises(GitHubError) as exc_info:
            client.get_pr(99999)

        assert "gh command failed" in str(exc_info.value)
        assert "PR not found" in str(exc_info.value)


def test_list_prs_by_author(mock_gh_output):
    """list_prs_by_author returns list of PRInfo."""
    with patch("shutil.which", return_value="/usr/bin/gh"), patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess(
            [], 0, stdout=mock_gh_output["prs_list"], stderr=""
        )
        client = GitHubClient()

        prs = client.list_prs_by_author("testuser")

        assert len(prs) == 2
        assert prs[0].number == 12345
        assert prs[0].branch == "feature-1"
        assert prs[1].number == 12346
        assert prs[1].branch == "feature-2"
        # Verify gh was called with author filter
        call_args = mock_run.call_args[0][0]
        assert "--author" in call_args
        assert "testuser" in call_args


def test_get_pr_info_by_branches(mock_gh_output):
    """get_pr_info_by_branches returns dict keyed by branch."""
    with patch("shutil.which", return_value="/usr/bin/gh"), patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess(
            [], 0, stdout=mock_gh_output["prs_list"], stderr=""
        )
        client = GitHubClient()

        pr_dict = client.get_pr_info_by_branches("testuser")

        assert "feature-1" in pr_dict
        assert "feature-2" in pr_dict
        assert pr_dict["feature-1"].number == 12345
        assert pr_dict["feature-2"].number == 12346
