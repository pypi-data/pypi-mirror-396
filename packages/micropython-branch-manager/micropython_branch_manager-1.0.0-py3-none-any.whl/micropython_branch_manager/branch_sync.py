"""Branch synchronization logic for micropython-branch-manager."""

import re

from .config import BranchConfig, MicroPythonConfig
from .git import GitRepo
from .github import PRInfo

MERGE_PATTERN = re.compile(r"Merge branch '([^']+)'")


def extract_branches_from_merges(git: GitRepo, target: str, integration: str) -> list[str]:
    """Extract branch names from merge commits between target and integration.

    Returns branches in merge order (oldest first).
    """
    subjects = git.get_log_subjects(f"{target}..{integration}")
    branches = []
    for subject in subjects:
        match = MERGE_PATTERN.search(subject)
        if match:
            branch = match.group(1)
            if branch not in branches:
                branches.append(branch)
    branches.reverse()  # Oldest first
    return branches


def sync_config_with_branches(
    config: MicroPythonConfig,
    detected_branches: list[str],
    pr_cache: dict[str, PRInfo],
) -> bool:
    """Update config with detected branches.

    Returns True if config was modified.
    """
    existing = {b.name: b for b in config.branches}
    modified = False

    for branch in detected_branches:
        if branch not in existing:
            entry = BranchConfig(name=branch, remote="origin")
            if branch in pr_cache:
                pr = pr_cache[branch]
                entry.pr_url = pr.url
                entry.pr_number = pr.number
                entry.title = pr.title
            config.branches.append(entry)
            modified = True

    # Reorder to match merge order
    order = {name: i for i, name in enumerate(detected_branches)}
    config.branches.sort(key=lambda b: order.get(b.name, 999))

    return modified


def validate_branches(config: MicroPythonConfig, detected_branches: list[str]) -> list[str]:
    """Validate config branches against detected branches.

    Returns list of warnings about discrepancies.
    """
    warnings = []
    detected_set = set(detected_branches)
    config_set = {b.name for b in config.branches}

    # Branches in config but not in merge history
    missing_from_history = config_set - detected_set
    if missing_from_history:
        warnings.append(
            f"WARNING: The following branches are in the config but not found in merge history:\n"
            f"  {', '.join(sorted(missing_from_history))}\n"
            "This may indicate they were removed from the integration branch."
        )

    # Branches in merge history but not in config (will be added automatically)
    missing_from_config = detected_set - config_set
    if missing_from_config:
        warnings.append(
            f"INFO: The following branches will be added to config:\n"
            f"  {', '.join(sorted(missing_from_config))}"
        )

    return warnings
