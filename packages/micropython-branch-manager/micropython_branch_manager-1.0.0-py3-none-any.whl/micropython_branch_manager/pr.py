"""PR addition workflow for micropython-branch-manager."""

import re
from pathlib import Path

from .config import CONFIG_FILENAME, BranchConfig, MicroPythonConfig
from .exceptions import ConfigError, GitError, MergeConflictError
from .git import GitRepo
from .github import GitHubClient, PRInfo
from .update_branch import (
    create_update_branch,
    find_gitlab_remote,
    format_mr_description,
    get_gitlab_mr_url,
    git_url_to_https,
)

PR_URL_PATTERN = re.compile(r"https?://github\.com/micropython/micropython/pull/(\d+)")


class PRManager:
    """Manages adding PRs to integration branch."""

    def __init__(self, submodule_path: Path, parent_repo_path: Path | None = None):
        self.submodule_path = submodule_path
        self.parent_repo_path = parent_repo_path
        self.git = GitRepo(submodule_path)
        self.parent_git = GitRepo(parent_repo_path) if parent_repo_path else None
        self.github = GitHubClient()

    def parse_identifier(self, value: str) -> str | int:
        """Parse PR identifier to number or branch name."""
        # URL
        match = PR_URL_PATTERN.match(value)
        if match:
            return int(match.group(1))
        # Number
        if value.isdigit():
            return int(value)
        # Branch name
        return value

    def add_pr(self, identifier: str) -> None:
        """Add PR to integration branch."""
        config = MicroPythonConfig.load(self.submodule_path, require_exists=True)
        integration = config.integration_branch

        # Setup remotes
        for name, url in config.remotes.items():
            self.git.ensure_remote(name, url)

        # Parse identifier and get PR info
        print(f"Fetching PR info for: {identifier}")
        parsed = self.parse_identifier(identifier)
        pr_info = self.github.get_pr(parsed)
        print(f"Found PR #{pr_info.number}: {pr_info.title}")
        print(f"Branch: {pr_info.branch}")
        print(f"State: {pr_info.state}")

        # Check not already in config
        if config.has_branch(pr_info.branch):
            raise ConfigError(f"Branch {pr_info.branch} already in config")

        # Check working tree, but allow config-only modifications
        status = self.git.run("status", "--porcelain")
        if status:
            lines = [line for line in status.split("\n") if line]
            non_config_lines = [line for line in lines if not line.endswith(CONFIG_FILENAME)]
            if non_config_lines:
                # Has changes other than config
                self.git.require_clean()

        # Create update branch
        print(f"\nCreating update branch from {integration}...")
        update_branch = create_update_branch(self.git, integration)

        # Fetch PR from upstream
        print(f"Fetching PR #{pr_info.number} from upstream...")
        self._fetch_pr(pr_info)

        # Ensure remote exists for PR author's fork
        remote = self._ensure_author_remote(pr_info.author, config)

        # Update config before merge
        print("\nUpdating config...")
        config.branches.append(
            BranchConfig(
                name=pr_info.branch,
                remote=remote,
                pr_url=pr_info.url,
                pr_number=pr_info.number,
                title=pr_info.title,
            )
        )
        config.save(self.submodule_path)

        # Merge into update branch (may raise MergeConflictError)
        merge_msg = f"Merge branch '{pr_info.branch}'\n\n{pr_info.title}"
        print(f"Merging {pr_info.branch} into {update_branch}...")
        try:
            self.git.merge(pr_info.branch, merge_msg)
            print("Merge completed successfully")
        except MergeConflictError:
            # Re-raise with context - user must resolve manually
            raise

        # Stage config and amend merge commit to include it
        self.git.run("add", CONFIG_FILENAME)
        self.git.run("commit", "--amend", "--no-edit")

        # Push update branch to GitLab
        gitlab_remote = find_gitlab_remote(self.git)
        if gitlab_remote:
            print(f"\nPushing {update_branch} to {gitlab_remote}...")
            try:
                self.git.push(gitlab_remote, update_branch, force=True)
            except GitError as e:
                print(f"WARNING: Failed to push {update_branch} to {gitlab_remote}: {e}")

        # Commit to parent repo if available
        if self.parent_git:
            self._commit_parent(pr_info)

        # Print summary
        self._print_summary(config, update_branch, pr_info)

    def _fetch_pr(self, pr_info: PRInfo) -> None:
        """Fetch PR branch from upstream, always getting fresh content."""
        # Always fetch fresh from upstream, using + to force update if branch exists
        self.git.run("fetch", "upstream", f"+pull/{pr_info.number}/head:{pr_info.branch}")

    def _ensure_author_remote(self, author: str, config: MicroPythonConfig) -> str:
        """Ensure a remote exists for the PR author's fork.

        Checks existing remotes first (both git and config). If no matching remote
        found, creates one with the author's GitHub username and HTTPS URL.

        Returns the remote name to use for this author.
        """
        # Check if we already have a remote for this author
        git_remotes = self.git.list_remotes()
        for name, url in git_remotes.items():
            if f"/{author}/" in url or f":{author}/" in url:
                # Found existing remote for this author
                if name not in config.remotes:
                    config.remotes[name] = url
                return name

        # No existing remote, create one using author's GitHub username
        remote_url = f"https://github.com/{author}/micropython.git"
        print(f"Adding remote '{author}' -> {remote_url}")
        self.git.run("remote", "add", author, remote_url)
        config.remotes[author] = remote_url
        return author

    def _commit_parent(self, pr_info: PRInfo) -> None:
        """Commit submodule and config changes to parent repo."""
        if not self.parent_git or not self.parent_repo_path:
            return
        print("\nCommitting to parent repository...")
        # Stage submodule
        rel_path = str(self.submodule_path.relative_to(self.parent_repo_path))
        self.parent_git.run("add", rel_path)
        # Commit
        msg = f'Add "{pr_info.branch}" to micropython.\n\nFrom {pr_info.url}'
        self.parent_git.run("commit", "-m", msg)
        print("Parent repository updated")

    def _print_summary(
        self, config: MicroPythonConfig, update_branch: str, pr_info: PRInfo
    ) -> None:
        """Print summary with MR URL."""
        print("\n=== PR ADDED SUCCESSFULLY ===")
        print(f"PR #{pr_info.number}: {pr_info.title}")
        print(f"Branch: {pr_info.branch}")

        gitlab_remote = find_gitlab_remote(self.git)
        if gitlab_remote:
            remotes = self.git.list_remotes()
            url = remotes[gitlab_remote]
            base = git_url_to_https(url)
            mr_title = f"{config.integration_branch}: Add micropython PR #{pr_info.number}"
            mr_description = format_mr_description(config, remotes)
            mr_url = get_gitlab_mr_url(
                base,
                update_branch,
                config.integration_branch,
                title=mr_title,
                description=mr_description,
            )
            print(f"\nCreate MR: {mr_url}")
