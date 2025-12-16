"""GitHub API wrapper using gh CLI for micropython-branch-manager."""

import json
import shutil
import subprocess
from dataclasses import dataclass

from .exceptions import GitHubCLINotFound, GitHubError

MICROPYTHON_REPO = "micropython/micropython"


@dataclass
class PRInfo:
    """GitHub Pull Request metadata."""

    number: int
    branch: str  # headRefName
    title: str
    url: str
    state: str  # OPEN, CLOSED, MERGED
    author: str  # headRepositoryOwner.login - the fork owner


class GitHubClient:
    """Wrapper for gh CLI operations."""

    def __init__(self, repo: str = MICROPYTHON_REPO):
        self.repo = repo
        self._check_gh_available()

    def _check_gh_available(self) -> None:
        """Verify gh CLI is installed and accessible."""
        if shutil.which("gh") is None:
            raise GitHubCLINotFound(
                "GitHub CLI (gh) not found.\n\n"
                "Install from: https://cli.github.com/\n"
                "  - macOS: brew install gh\n"
                "  - Ubuntu: sudo apt install gh\n"
                "  - Windows: winget install GitHub.cli\n\n"
                "After installation, authenticate with: gh auth login"
            )

    def _run(self, *args: str) -> str:
        """Run gh command, return stdout."""
        cmd = ["gh", *args]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise GitHubError(f"gh command failed: {result.stderr}")
        return result.stdout.strip()

    def get_pr(self, identifier: str | int) -> PRInfo:
        """Get PR metadata by number or branch name."""
        output = self._run(
            "pr",
            "view",
            str(identifier),
            "--repo",
            self.repo,
            "--json",
            "headRefName,headRepositoryOwner,number,title,url,state",
        )
        data = json.loads(output)
        return PRInfo(
            number=data["number"],
            branch=data["headRefName"],
            title=data["title"],
            url=data["url"],
            state=data["state"],
            author=data["headRepositoryOwner"]["login"],
        )

    def list_prs_by_author(self, author: str, limit: int = 100) -> list[PRInfo]:
        """List all PRs by author."""
        output = self._run(
            "pr",
            "list",
            "--repo",
            self.repo,
            "--author",
            author,
            "--state",
            "all",
            "--limit",
            str(limit),
            "--json",
            "headRefName,headRepositoryOwner,number,title,url,state",
        )
        data = json.loads(output)
        return [
            PRInfo(
                number=pr["number"],
                branch=pr["headRefName"],
                title=pr["title"],
                url=pr["url"],
                state=pr["state"],
                author=pr["headRepositoryOwner"]["login"],
            )
            for pr in data
        ]

    def get_pr_info_by_branches(self, author: str) -> dict[str, PRInfo]:
        """Get mapping of branch name to PR info for author."""
        prs = self.list_prs_by_author(author)
        return {pr.branch: pr for pr in prs}
