"""CLI interface for micropython-branch-manager."""

import sys
from pathlib import Path
from typing import Annotated

import cyclopts

from .branch_sync import extract_branches_from_merges, sync_config_with_branches
from .config import CONFIG_FILENAME, MicroPythonConfig
from .exceptions import GitHubCLINotFound, MBMError
from .git import GitRepo
from .github import GitHubClient
from .pr import PRManager
from .rebase import RebaseManager

app = cyclopts.App(
    name="mbm",
    help="Manage MicroPython fork integration branches.",
)

# Common parameter types
SubmodulePath = Annotated[
    Path | None,
    cyclopts.Parameter(
        name="--submodule",
        help="Path to MicroPython submodule (default: auto-detect)",
    ),
]


def resolve_submodule(path: Path | None) -> Path:
    """Resolve submodule path, auto-detecting if not specified."""
    if path:
        return path.resolve()
    # Try common locations
    for candidate in [Path("src/micropython"), Path("micropython"), Path(".")]:
        config_path = candidate / CONFIG_FILENAME
        if config_path.exists() or (candidate / ".git").exists():
            return candidate.resolve()
    raise ValueError("Could not auto-detect submodule path. Use --submodule.")


@app.command
def init(
    submodule: SubmodulePath = None,
    integration_branch: Annotated[
        str | None,
        cyclopts.Parameter(name=["--integration-branch", "-b"]),
    ] = None,
) -> None:
    """Initialize configuration in submodule."""
    path = resolve_submodule(submodule)
    git = GitRepo(path)

    # If integration branch not specified, detect current branch
    if integration_branch is None:
        integration_branch = git.run("branch", "--show-current")
        if not integration_branch:
            # Detached HEAD or other issue, fall back to main
            integration_branch = "main"
        print(f"Using current branch as integration branch: {integration_branch}")

    # Detect existing git remotes
    remotes = git.list_remotes()
    if remotes:
        print(f"\nDetected {len(remotes)} remote(s):")
        for name, url in remotes.items():
            print(f"  - {name}: {url}")
    else:
        print("\nNo remotes detected. You'll need to add them manually to the config.")

    config = MicroPythonConfig(integration_branch=integration_branch, remotes=remotes)
    config.save(path)
    print(f"\nCreated {path / CONFIG_FILENAME}")


@app.command
def rebase(
    target: str = "upstream/master",
    submodule: SubmodulePath = None,
    local: Annotated[bool, cyclopts.Parameter(name="--local")] = False,
    dry_run: Annotated[bool, cyclopts.Parameter(name="--dry-run")] = False,
    force_push: Annotated[bool, cyclopts.Parameter(name="--force-push")] = False,
    resume: Annotated[bool, cyclopts.Parameter(name="--resume")] = False,
) -> None:
    """Rebase integration branch by rebuilding from fresh PRs."""
    path = resolve_submodule(submodule)
    manager = RebaseManager(path)
    manager.execute(
        target=target,
        local_only=local,
        dry_run=dry_run,
        force_push=force_push,
        resume=resume,
    )


@app.command
def add_pr(
    pr_identifier: str,
    submodule: SubmodulePath = None,
) -> None:
    """Add PR to integration branch."""
    path = resolve_submodule(submodule)
    # Detect parent repo
    parent_path = path.parent
    parent: Path | None = parent_path if (parent_path / ".git").exists() else None

    manager = PRManager(path, parent)
    manager.add_pr(pr_identifier)


@app.command
def sync(
    gh_author: Annotated[
        str,
        cyclopts.Parameter(
            help="GitHub username to look up PR metadata for branches",
        ),
    ],
    submodule: SubmodulePath = None,
) -> None:
    """Sync JSON config with current branch state.

    Detects branches from merge commits and updates config with PR metadata.
    """
    path = resolve_submodule(submodule)
    config = MicroPythonConfig.load(path, require_exists=True)
    git = GitRepo(path)

    # Setup remotes
    for name, url in config.remotes.items():
        git.ensure_remote(name, url)

    # Detect branches
    detected = extract_branches_from_merges(git, "upstream/master", config.integration_branch)

    # Get PR cache from GitHub
    pr_cache = {}
    try:
        github = GitHubClient()
        pr_cache = github.get_pr_info_by_branches(gh_author)
    except GitHubCLINotFound:
        pass  # Continue without PR info

    # Sync
    if sync_config_with_branches(config, detected, pr_cache):
        config.save(path)
        print(f"Updated {path / CONFIG_FILENAME}")
    else:
        print("Config already in sync")


@app.command
def config(
    submodule: SubmodulePath = None,
) -> None:
    """Show current configuration."""
    path = resolve_submodule(submodule)
    cfg = MicroPythonConfig.load(path, require_exists=True)

    print(f"Integration branch: {cfg.integration_branch}")

    # Show branches first
    print(f"\nBranches ({len(cfg.branches)}):")
    for b in cfg.branches:
        title = b.title or "(no title)"
        print(f"  {b.remote}/{b.name}: {title}")
        if b.pr_url:
            print(f"    - {b.pr_url}")
        print()  # Blank line between entries

    # Only show remotes that are referenced by branches
    used_remotes = {b.remote for b in cfg.branches}
    used_remotes.add("upstream")  # Always show upstream
    remotes_to_show = {k: v for k, v in cfg.remotes.items() if k in used_remotes}
    print(f"Remotes ({len(remotes_to_show)}):")
    for name, url in remotes_to_show.items():
        print(f"  {name}: {url}")


def main() -> None:
    """Entry point."""
    try:
        app()
    except MBMError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
