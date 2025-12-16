"""Tests for git operations wrapper."""

from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from micropython_branch_manager.exceptions import (
    GitError,
    MergeConflictError,
    RebaseConflictError,
    RemoteDivergenceError,
    WorkingTreeDirtyError,
)
from micropython_branch_manager.git import GitRepo


def test_git_repo_run_success(tmp_path):
    """GitRepo.run executes command and returns stdout."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout="abc123\n", stderr="")
        repo = GitRepo(tmp_path)

        result = repo.run("rev-parse", "HEAD")

        assert result == "abc123"
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["git", "rev-parse", "HEAD"]
        assert mock_run.call_args[1]["cwd"] == tmp_path


def test_git_repo_run_failure(tmp_path):
    """GitRepo.run raises GitError on non-zero exit."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess(
            [], 1, stdout="", stderr="fatal: not a git repository"
        )
        repo = GitRepo(tmp_path)

        with pytest.raises(GitError) as exc_info:
            repo.run("status")

        assert "git status failed" in str(exc_info.value)
        assert "fatal: not a git repository" in str(exc_info.value)


def test_is_clean_true(tmp_path):
    """is_clean returns True when status is empty."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout="", stderr="")
        repo = GitRepo(tmp_path)

        assert repo.is_clean() is True


def test_is_clean_false(tmp_path):
    """is_clean returns False when status has changes."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout=" M file.py\n", stderr="")
        repo = GitRepo(tmp_path)

        assert repo.is_clean() is False


def test_require_clean_raises(tmp_path):
    """require_clean raises WorkingTreeDirtyError if dirty."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout=" M file.py\n", stderr="")
        repo = GitRepo(tmp_path)

        with pytest.raises(WorkingTreeDirtyError) as exc_info:
            repo.require_clean()

        assert "uncommitted changes" in str(exc_info.value)


def test_fetch_success(tmp_path):
    """fetch executes submodule sync and fetch."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout="", stderr="")
        repo = GitRepo(tmp_path)

        repo.fetch("origin")

        # Should call submodule sync and then fetch
        assert mock_run.call_count >= 2


def test_rebase_success(tmp_path):
    """rebase executes with correct args."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout="", stderr="")
        repo = GitRepo(tmp_path)

        repo.rebase("upstream/master")

        # Find the rebase call
        rebase_calls = [call for call in mock_run.call_args_list if "rebase" in str(call)]
        assert len(rebase_calls) > 0
        call_args = rebase_calls[0][0][0]
        assert "rebase" in call_args
        assert "--rebase-merges" in call_args
        assert "--update-refs" in call_args
        assert "upstream/master" in call_args


def test_rebase_conflict_detection(tmp_path):
    """rebase detects conflicts and raises RebaseConflictError."""
    with patch("subprocess.run") as mock_run:

        def side_effect(cmd, **kwargs):
            if "rebase" in cmd and "--rebase-merges" in cmd:
                return CompletedProcess(cmd, 1, stdout="", stderr="CONFLICT")
            elif "status" in cmd and "--porcelain" in cmd:
                return CompletedProcess(cmd, 0, stdout="UU file1.py\nAA file2.py\n", stderr="")
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        repo = GitRepo(tmp_path)

        with pytest.raises(RebaseConflictError) as exc_info:
            repo.rebase("upstream/master")

        assert exc_info.value.conflicting_files == ["file1.py", "file2.py"]
        assert "git rebase --continue" in str(exc_info.value)


def test_merge_success(tmp_path):
    """merge executes with no-ff and message."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = CompletedProcess([], 0, stdout="", stderr="")
        repo = GitRepo(tmp_path)

        repo.merge("feature-branch", "Merge feature")

        merge_calls = [call for call in mock_run.call_args_list if "merge" in str(call)]
        assert len(merge_calls) > 0
        call_args = merge_calls[0][0][0]
        assert "merge" in call_args
        assert "--no-ff" in call_args
        assert "feature-branch" in call_args
        assert "Merge feature" in call_args


def test_merge_conflict_detection(tmp_path):
    """merge detects conflicts and raises MergeConflictError."""
    with patch("subprocess.run") as mock_run:

        def side_effect(cmd, **kwargs):
            if "merge" in cmd:
                return CompletedProcess(cmd, 1, stdout="", stderr="CONFLICT")
            elif "status" in cmd and "--porcelain" in cmd:
                return CompletedProcess(cmd, 0, stdout="UU src/main.py\n", stderr="")
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        repo = GitRepo(tmp_path)

        with pytest.raises(MergeConflictError) as exc_info:
            repo.merge("feature", "Merge message")

        assert exc_info.value.conflicting_files == ["src/main.py"]


def test_check_divergence_no_remote(tmp_path):
    """check_divergence succeeds if remote doesn't exist."""
    with patch("subprocess.run") as mock_run:

        def side_effect(cmd, **kwargs):
            if "rev-parse" in cmd and "--verify" in cmd:
                return CompletedProcess(cmd, 1, stdout="", stderr="fatal: bad revision")
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        repo = GitRepo(tmp_path)

        # Should not raise - remote doesn't exist
        repo.check_divergence("main", "origin/main")


def test_check_divergence_none(tmp_path):
    """check_divergence succeeds if no divergence."""
    with patch("subprocess.run") as mock_run:

        def side_effect(cmd, **kwargs):
            if "rev-parse" in cmd and "--verify" in cmd:
                return CompletedProcess(cmd, 0, stdout="abc123\n", stderr="")
            elif "rev-list" in cmd and "--count" in cmd:
                return CompletedProcess(cmd, 0, stdout="0\n", stderr="")
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        repo = GitRepo(tmp_path)

        # Should not raise - no divergence
        repo.check_divergence("main", "origin/main")


def test_check_divergence_detected(tmp_path):
    """check_divergence raises RemoteDivergenceError."""
    with patch("subprocess.run") as mock_run:

        def side_effect(cmd, **kwargs):
            if "rev-parse" in cmd and "--verify" in cmd:
                return CompletedProcess(cmd, 0, stdout="abc123\n", stderr="")
            elif "rev-list" in cmd and "--count" in cmd:
                # Remote has 5 commits not in local, local has 3 not in remote
                if "main..origin/main" in " ".join(cmd):
                    return CompletedProcess(cmd, 0, stdout="5\n", stderr="")
                else:
                    return CompletedProcess(cmd, 0, stdout="3\n", stderr="")
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        repo = GitRepo(tmp_path)

        with pytest.raises(RemoteDivergenceError) as exc_info:
            repo.check_divergence("main", "origin/main")

        error = exc_info.value
        assert error.branch == "main"
        assert error.remote_commits == 5
        assert error.local_commits == 3
        assert "5 commit(s) not in local" in str(error)


def test_ensure_remote_creates(tmp_path):
    """ensure_remote creates remote if missing."""
    with patch("subprocess.run") as mock_run:

        def side_effect(cmd, **kwargs):
            if "config" in cmd and "remote.origin.url" in cmd:
                return CompletedProcess(cmd, 1, stdout="", stderr="")
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        repo = GitRepo(tmp_path)

        repo.ensure_remote("origin", "https://github.com/user/repo.git")

        # Should call git remote add
        add_calls = [
            call for call in mock_run.call_args_list if "remote" in str(call) and "add" in str(call)
        ]
        assert len(add_calls) > 0


def test_ensure_remote_updates_url(tmp_path):
    """ensure_remote updates URL if changed."""
    with patch("subprocess.run") as mock_run:

        def side_effect(cmd, **kwargs):
            if "config" in cmd and "remote.origin.url" in cmd:
                return CompletedProcess(cmd, 0, stdout="https://old-url.git\n", stderr="")
            return CompletedProcess(cmd, 0, stdout="", stderr="")

        mock_run.side_effect = side_effect
        repo = GitRepo(tmp_path)

        repo.ensure_remote("origin", "https://new-url.git")

        # Should call git remote set-url
        seturl_calls = [call for call in mock_run.call_args_list if "set-url" in str(call)]
        assert len(seturl_calls) > 0
