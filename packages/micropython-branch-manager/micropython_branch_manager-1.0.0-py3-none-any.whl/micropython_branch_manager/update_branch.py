"""Update branch management for micropython-branch-manager."""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

if TYPE_CHECKING:
    from .config import MicroPythonConfig

from .git import GitRepo


def get_update_branch_name(integration_branch: str) -> str:
    """Get update branch name from integration branch name."""
    return f"{integration_branch}_update"


def create_update_branch(git: GitRepo, integration_branch: str) -> str:
    """Create update branch from integration branch.

    Returns the update branch name.
    """
    update_branch = get_update_branch_name(integration_branch)
    git.checkout(update_branch, create=True, force=True)
    return update_branch


def find_gitlab_remote(git: GitRepo, pattern: str = "gitlab") -> str | None:
    """Find remote pointing to GitLab.

    Searches for remote URL containing 'gitlab'.
    """
    remotes = git.list_remotes()
    for name, url in remotes.items():
        if pattern in url.lower():
            return name
    return None


def git_url_to_https(url: str) -> str:
    """Convert git remote URL to HTTPS base URL.

    Handles SSH format (git@host:path) and HTTPS format.
    Strips .git suffix.
    """
    if url.startswith("git@"):
        # SSH format: git@host:path -> https://host/path
        # Remove git@ prefix, then replace first : with /
        without_prefix = url[4:]  # Remove "git@"
        base = "https://" + without_prefix.replace(":", "/", 1)
    elif url.startswith("https://"):
        base = url
    else:
        base = url
    return base.removesuffix(".git")


def get_gitlab_mr_url(
    base_url: str,
    source_branch: str,
    target_branch: str,
    title: str | None = None,
    description: str | None = None,
) -> str:
    """Generate GitLab merge request creation URL."""
    # Strip trailing slash from base_url if present
    base_url = base_url.rstrip("/")
    url = (
        f"{base_url}/-/merge_requests/new"
        f"?merge_request%5Bsource_branch%5D={quote(source_branch, safe='')}"
        f"&merge_request%5Btarget_branch%5D={quote(target_branch, safe='')}"
    )
    if title:
        url += f"&merge_request%5Btitle%5D={quote(title, safe='')}"
    if description:
        url += f"&merge_request%5Bdescription%5D={quote(description, safe='')}"
    return url


def format_mr_description(
    config: MicroPythonConfig,
    remotes: dict[str, str],
) -> str:
    """Format MR description with branches and used remotes.

    Args:
        config: The MicroPython configuration.
        remotes: Dict of remote name to URL.

    Returns:
        Formatted description string.
    """
    lines = ["## Branches\n"]

    for b in config.branches:
        title = b.title or "(no title)"
        lines.append(f"- **{b.remote}/{b.name}**: {title}")
        if b.pr_url:
            lines.append(f"  - {b.pr_url}")

    # Only include remotes referenced by branches
    used_remotes = {b.remote for b in config.branches}
    used_remotes.add("upstream")
    remotes_to_show = {k: v for k, v in remotes.items() if k in used_remotes}

    if remotes_to_show:
        lines.append("\n## Remotes\n")
        for name, url in remotes_to_show.items():
            lines.append(f"- **{name}**: {url}")

    # Add next steps section
    integration = config.integration_branch
    update_branch = f"{integration}_update"
    lines.append("\n## Next Steps\n")
    lines.append(
        f'Once this MR has been reviewed, "{integration}" will need to be '
        f'force-pushed to "{update_branch}":'
    )
    lines.append(f"\n```bash\ngit push origin +{update_branch}:{integration}\n```")

    return "\n".join(lines)
