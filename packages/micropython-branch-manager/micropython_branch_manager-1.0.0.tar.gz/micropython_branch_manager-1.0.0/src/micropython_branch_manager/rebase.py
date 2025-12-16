"""Rebase workflow orchestration for micropython-branch-manager."""

import sys
from pathlib import Path

from .config import BranchConfig, MicroPythonConfig
from .exceptions import GitError, RebaseConflictError, RemoteDivergenceError
from .git import GitRepo
from .update_branch import (
    find_gitlab_remote,
    format_mr_description,
    get_gitlab_mr_url,
    git_url_to_https,
)


class RebaseManager:
    """Orchestrates the rebase workflow."""

    def __init__(self, submodule_path: Path):
        self.submodule_path = submodule_path
        self.git = GitRepo(submodule_path)

    def execute(
        self,
        target: str = "upstream/master",
        local_only: bool = False,
        dry_run: bool = False,
        force_push: bool = False,
        resume: bool = False,
    ) -> None:
        """Execute sequential PR integration workflow."""
        if resume:
            return self._resume_rebase(target, local_only, dry_run, force_push)

        # Phase 1: Preparation
        config = self._prepare(target, local_only)

        # Phase 2: Sequential integration
        update_branch = f"{config.integration_branch}_update"
        if dry_run:
            print(f"DRY RUN: Would create update branch: {update_branch}")
        else:
            print(f"Creating update branch from {target}...")
            self.git.checkout(update_branch, create=True, force=True)
            self.git.run("reset", "--hard", target)

        for idx, branch_config in enumerate(config.branches):
            if not dry_run:
                # Pass config on first save to store in state file
                self._save_progress(idx, update_branch, target, config if idx == 0 else None)
            self._integrate_pr(branch_config, target, update_branch, dry_run)

        # Phase 3: Push
        push_results: dict[str, bool] = {}
        divergence_errors: list[RemoteDivergenceError] = []
        if not local_only and not dry_run:
            push_results, divergence_errors = self._push_branches(config, update_branch, force_push)

        # Phase 4: Summary
        self._print_summary(config, update_branch, target, dry_run, push_results, divergence_errors)
        if not dry_run:
            self._cleanup_progress()

    def _prepare(self, target: str, local_only: bool) -> MicroPythonConfig:
        """Load config, setup remotes, fetch."""
        config = MicroPythonConfig.load(self.submodule_path, require_exists=True)

        for name, url in config.remotes.items():
            self.git.ensure_remote(name, url)

        if not local_only:
            print("Fetching from remotes...")
            self.git.fetch()

        self.git.require_clean()
        return config

    def _integrate_pr(
        self, branch: BranchConfig, target: str, update_branch: str, dry_run: bool = False
    ) -> None:
        """Fetch fresh PR, rebase onto target, merge into update branch."""
        print(f"\n{'=' * 60}")
        print(f"Integrating: {branch.name}")
        if branch.title:
            print(f"  {branch.title}")
        print(f"{'=' * 60}")

        if dry_run:
            print(f"  DRY RUN: Would integrate {branch.name}")
            return

        # Step A: Fetch fresh content
        source_branch = self._fetch_pr_branch(branch)

        # Step B: Rebase PR onto target (not update_branch)
        # Each feature branch is rebased directly onto upstream/master
        rebase_branch = f"rebase-{branch.name}"
        self.git.checkout(rebase_branch, create=True, force=True)
        self.git.run("reset", "--hard", source_branch)

        try:
            self.git.rebase(target, update_refs=False)
        except RebaseConflictError as e:
            # Enhance with PR context
            e.pr_context = {
                "pr_number": branch.pr_number,
                "branch_name": branch.name,
                "branch_title": branch.title,
            }
            print(f"\nConflict while rebasing {branch.name}.")
            print("Resolve conflicts manually, then run:")
            print(f"  cd {self.submodule_path}")
            print("  git rebase --continue")
            print("  mbm rebase --resume")
            raise

        # Steps C-E: Complete the integration
        self._complete_integration(branch, update_branch)
        print(f"✓ Integrated {branch.name}")

    def _complete_integration(self, branch: BranchConfig, update_branch: str) -> None:
        """Complete PR integration after rebase: merge, amend with config, update refs, cleanup."""
        from .config import CONFIG_FILENAME

        rebase_branch = f"rebase-{branch.name}"

        # Merge into integration
        self.git.checkout(update_branch)
        merge_msg = f"Merge branch '{branch.name}'"
        if branch.title:
            merge_msg += f"\n\n{branch.title}"
        self.git.merge(rebase_branch, merge_msg, no_ff=True)

        # Include config in merge commit
        config = MicroPythonConfig.load(self.submodule_path)
        config.save(self.submodule_path)
        self.git.run("add", CONFIG_FILENAME)
        self.git.run("commit", "--amend", "--no-edit")

        # Update feature branch ref and set tracking to correct remote
        self.git.run("branch", "-f", branch.name, rebase_branch)
        upstream_ref = f"{branch.remote}/{branch.name}"
        self.git.set_branch_upstream(branch.name, upstream_ref)

        # Cleanup
        self.git.run("branch", "-D", rebase_branch, check=False)
        if branch.pr_number:
            temp_branch = f"pr-{branch.pr_number}-temp"
            self.git.run("branch", "-D", temp_branch, check=False)

    def _fetch_pr_branch(self, branch: BranchConfig) -> str:
        """Fetch PR or local branch, return source branch name."""
        if branch.pr_number:
            # Fetch from upstream PR, using + to force update if temp branch exists
            temp_branch = f"pr-{branch.pr_number}-temp"
            print(f"  Fetching PR #{branch.pr_number} from upstream...")
            self.git.run("fetch", "upstream", f"+pull/{branch.pr_number}/head:{temp_branch}")
            return temp_branch
        else:
            # Fetch from configured remote (local development branch)
            print(f"  Fetching {branch.name} from {branch.remote}...")
            self.git.run("fetch", branch.remote, branch.name)
            remote_ref = f"{branch.remote}/{branch.name}"

            # Ensure local branch exists
            if not self.git.branch_exists(branch.name):
                self.git.create_branch(branch.name, remote_ref)

            return branch.name

    def _save_progress(
        self,
        index: int,
        update_branch: str,
        target: str,
        config: MicroPythonConfig | None = None,
    ) -> None:
        """Save rebase progress state."""
        import json

        state = {
            "index": index,
            "update_branch": update_branch,
            "target": target,
        }

        git_dir = Path(self.git.run("rev-parse", "--git-dir"))
        if not git_dir.is_absolute():
            git_dir = self.submodule_path / git_dir
        state_file = git_dir / "mbm-rebase-state.json"

        # On first save (index 0), include the full config
        if index == 0 and config:
            state["config"] = json.loads(config.model_dump_json())

        # Load existing state to preserve config if it exists
        if state_file.exists():
            existing_state = json.loads(state_file.read_text())
            if "config" in existing_state:
                state["config"] = existing_state["config"]

        state_file.write_text(json.dumps(state))

    def _cleanup_progress(self) -> None:
        """Remove progress state file."""
        git_dir = Path(self.git.run("rev-parse", "--git-dir"))
        if not git_dir.is_absolute():
            git_dir = self.submodule_path / git_dir
        state_file = git_dir / "mbm-rebase-state.json"
        state_file.unlink(missing_ok=True)

    def _push_branches(
        self, config: MicroPythonConfig, update_branch: str, force_push: bool
    ) -> tuple[dict[str, bool], list[RemoteDivergenceError]]:
        """Push all branches to their remotes with safety checks.

        Returns tuple of:
        - dict mapping branch name to push success status
        - list of divergence errors encountered
        """
        print("\nPushing branches...")
        push_results: dict[str, bool] = {}
        divergence_errors: list[RemoteDivergenceError] = []

        # Check for divergence and push feature branches
        for branch in config.branches:
            remote_ref = f"{branch.remote}/{branch.name}"
            try:
                self.git.check_divergence(branch.name, remote_ref, force_push)
                print(f"Pushing {branch.name} to {branch.remote}...")
                self.git.push(branch.remote, branch.name, force=True)
                push_results[branch.name] = True
            except RemoteDivergenceError as e:
                divergence_errors.append(e)
                push_results[branch.name] = False
            except GitError as e:
                # Permission denied or other push error - continue with other branches
                print(f"WARNING: Failed to push {branch.name} to {branch.remote}: {e}")
                push_results[branch.name] = False

        # Push update branch to GitLab
        gitlab_remote = find_gitlab_remote(self.git)
        if gitlab_remote:
            try:
                print(f"Pushing {update_branch} to {gitlab_remote}...")
                self.git.push(gitlab_remote, update_branch, force=True)
                push_results[update_branch] = True
            except GitError as e:
                print(f"WARNING: Failed to push {update_branch} to {gitlab_remote}: {e}")
                push_results[update_branch] = False

        return push_results, divergence_errors

    def _print_summary(
        self,
        config: MicroPythonConfig,
        update_branch: str,
        target: str,
        dry_run: bool,
        push_results: dict[str, bool] | None = None,
        divergence_errors: list[RemoteDivergenceError] | None = None,
    ) -> None:
        """Print summary with MR URL and push results."""
        if push_results is None:
            push_results = {}
        if divergence_errors is None:
            divergence_errors = []

        if dry_run:
            print("\n=== DRY RUN SUMMARY ===")
            print(f"Would rebase onto {target}")
            print(f"Would integrate {len(config.branches)} branches")
        else:
            print("\n=== REBASE COMPLETE ===")
            print(f"Rebased onto {target}")
            print(f"Integrated {len(config.branches)} branches")

            # Display push results
            if push_results:
                pushed = [name for name, success in push_results.items() if success]
                failed = [name for name, success in push_results.items() if not success]

                if pushed:
                    print(f"\n✓ Successfully pushed {len(pushed)} branch(es):")
                    for name in pushed:
                        print(f"  - {name}")

                if failed:
                    print(f"\n✗ Failed to push {len(failed)} branch(es):")
                    for name in failed:
                        print(f"  - {name}")
                    print("\n  (Check permissions or remote configuration)")

        gitlab_remote = find_gitlab_remote(self.git)
        remotes = self.git.list_remotes()

        if gitlab_remote:
            url = remotes[gitlab_remote]
            base = git_url_to_https(url)
            # Get short hash of target for title
            target_hash = self.git.run("rev-parse", "--short", target)
            mr_title = f"{config.integration_branch}: Rebase to {target} @ {target_hash}"
            mr_description = format_mr_description(config, remotes)
            mr_url = get_gitlab_mr_url(
                base,
                update_branch,
                config.integration_branch,
                title=mr_title,
                description=mr_description,
            )
            print(f"\nCreate MR: {mr_url}")

        # Display divergence errors at the end
        if divergence_errors:
            print("\n=== DIVERGENCE ERRORS ===", file=sys.stderr)
            print(
                "The following branches have diverged from their remotes.",
                file=sys.stderr,
            )
            print("Use --force-push to override.\n", file=sys.stderr)
            for i, err in enumerate(divergence_errors):
                if i > 0:
                    print("---", file=sys.stderr)
                print(
                    f"{err.branch}: remote has {err.remote_commits} commit(s) "
                    f"not in local, local has {err.local_commits} commit(s) not in remote",
                    file=sys.stderr,
                )

    def _resume_rebase(
        self, target: str, local_only: bool, dry_run: bool, force_push: bool
    ) -> None:
        """Resume interrupted rebase."""
        import json

        git_dir = Path(self.git.run("rev-parse", "--git-dir"))
        if not git_dir.is_absolute():
            git_dir = self.submodule_path / git_dir

        state_file = git_dir / "mbm-rebase-state.json"
        if not state_file.exists():
            from .exceptions import GitError

            raise GitError(
                "No rebase in progress to resume. Use 'mbm rebase' to start a new rebase."
            )

        state = json.loads(state_file.read_text())

        # Load config from state file instead of working tree
        # (working tree may not have config when on feature branch)
        if "config" in state:
            config = MicroPythonConfig.model_validate(state["config"])
        else:
            # Fallback to working tree for backward compatibility
            config = MicroPythonConfig.load(self.submodule_path)

        update_branch = state["update_branch"]

        # Check if there's an in-progress git rebase
        rebase_dir = git_dir / "rebase-merge"
        if rebase_dir.exists():
            # Complete the current rebase
            try:
                self.git.run("rebase", "--continue")
            except GitError as e:
                # Still conflicts, can't continue
                raise RebaseConflictError(
                    "Rebase conflicts still exist. "
                    "Resolve them and run 'mbm rebase --resume' again."
                ) from e

            # Complete the interrupted PR integration (merge, amend, update refs, cleanup)
            current_idx = state["index"]
            branch = config.branches[current_idx]
            print(f"Completing integration of {branch.name}...")
            self._complete_integration(branch, update_branch)
            print(f"✓ Integrated {branch.name}")

            # Move to next index
            start_idx = current_idx + 1
        else:
            # No in-progress rebase, start from next index
            start_idx = state["index"] + 1
        if start_idx >= len(config.branches):
            # Already finished all branches
            print("All branches integrated.")
        else:
            print(f"Resuming from branch {start_idx + 1}/{len(config.branches)}...")
            for idx in range(start_idx, len(config.branches)):
                self._save_progress(idx, update_branch, state["target"])
                self._integrate_pr(
                    config.branches[idx], state["target"], update_branch, dry_run=False
                )

        # Push and summarize
        push_results: dict[str, bool] = {}
        divergence_errors: list[RemoteDivergenceError] = []
        if not local_only and not dry_run:
            push_results, divergence_errors = self._push_branches(config, update_branch, force_push)
        self._print_summary(
            config, update_branch, state["target"], dry_run, push_results, divergence_errors
        )
        self._cleanup_progress()
