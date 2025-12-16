# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`micropython-branch-manager` (alias: `mbm`) is a Python CLI tool that automates maintaining a MicroPython fork with multiple feature branches integrated on top of upstream. It manages rebasing integration branches with preserved merge commits, adding PRs, tracking branch metadata in JSON config, and generating GitLab MR URLs.

## Development Commands

### Setup
```bash
uv sync
```

### Running the tool locally
```bash
uv run mbm --help
uv run mbm init --integration-branch main
uv run mbm rebase upstream/master
uv run mbm add-pr 12345
uv run mbm sync
uv run mbm config
```

### Testing
```bash
# Run all tests with coverage
uv run pytest tests/ -v --cov=micropython_branch_manager --cov-report=xml --cov-report=term

# Run specific test file
uv run pytest tests/test_specific.py -v
```

### Linting and Type Checking
```bash
# Run all lint/type checks and formatting (recommended)
uv run pre-commit run --all-files

# Run ruff linter
uv run ruff check .

# Auto-fix ruff issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Type check with mypy
uv run mypy src/micropython_branch_manager
```

### Pre-commit Hooks
```bash
# Install hooks
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files
```

### Building
```bash
# Build wheel and sdist
uv build
```

## Architecture

### Core Workflow Model

The tool operates on a MicroPython submodule directory containing a JSON config file (`.micropython-branches.json`). The workflow assumes:

1. **Integration branch** - A branch (typically `main`) that contains merge commits of multiple feature branches on top of upstream
2. **Feature branches** - Individual branches from upstream PRs or local development, tracked in GitHub forks
3. **Update branches** - Temporary branches created during rebase operations for GitLab MR creation
4. **Branch metadata** - Stored in JSON config with remote, PR URL, PR number, and title

### Module Responsibilities

- **cli.py** - Command-line interface using cyclopts. Entry point for all commands.
- **config.py** - Pydantic models for JSON configuration (`MicroPythonConfig`, `BranchConfig`). Handles load/save operations.
- **git.py** - Git operations wrapper (`GitRepo` class). Executes git commands and detects conflict states.
- **branch_sync.py** - Branch detection and synchronization. Extracts branch names from merge commit messages using regex pattern `Merge branch '([^']+)'`.
- **rebase.py** - Orchestrates full rebase workflow via `RebaseManager`. Includes branch validation, PR info lookup, rebase execution, divergence checks, and push operations.
- **pr.py** - PR addition workflow via `PRManager`. Fetches PR from upstream, merges into update branch, updates config, optionally commits to parent repo.
- **github.py** - GitHub API wrapper using `gh` CLI for PR metadata lookup.
- **update_branch.py** - Update branch creation and GitLab MR URL generation.
- **exceptions.py** - Custom exceptions for git conflicts, divergence, and errors.

### Git Operations Flow

**Rebase workflow:**
1. Load config and ensure remotes exist
2. Fetch from remotes (unless `--local`)
3. Extract branches from merge commits between target and integration branch
4. Validate detected branches against JSON config
5. Create update branch from integration branch
6. Rebase with `--rebase-merges --update-refs` to preserve merge structure
7. Check for remote divergence before force-pushing
8. Push feature branches to their configured remotes (GitHub forks)
9. Push update branch to GitLab for MR creation
10. Generate GitLab MR URL

**PR addition workflow:**
1. Parse PR identifier (number, URL, or branch name)
2. Fetch PR metadata using `gh` CLI
3. Create update branch from integration branch
4. Fetch PR branch from upstream: `git fetch upstream pull/{number}/head:{branch}`
5. Merge PR branch with merge commit
6. Update JSON config with new branch entry
7. Optionally commit submodule and config changes to parent repo
8. Generate GitLab MR URL

### Push Strategy

- **Feature branches** - Pushed to their respective GitHub forks (remote specified in config for that branch)
- **Integration/update branches** - Pushed to GitLab (remote typically "origin")
- Update branch is used for creating merge requests back to integration branch

### Error Handling

The tool uses custom exceptions with structured error data:

- `RebaseConflictError` - Raised when rebase encounters conflicts. Includes list of conflicting files and instructions for manual resolution.
- `MergeConflictError` - Raised when PR merge encounters conflicts. Similar structure to rebase conflicts.
- `RemoteDivergenceError` - Raised when remote branch has commits not in local branch. Includes commit counts and suggests options (fetch, force-push, abort).
- `WorkingTreeDirtyError` - Raised when working tree has uncommitted changes.

Conflict detection uses `git status --porcelain` to identify files with conflict markers (`UU`, `AA`, `DD` prefixes).

## Configuration File

`.micropython-branches.json` structure:
```json
{
  "integration_branch": "main",
  "remotes": {
    "upstream": "https://github.com/micropython/micropython.git",
    "origin": "git@github.com:username/micropython.git"
  },
  "branches": [
    {
      "name": "feature-branch-1",
      "remote": "origin",
      "pr_url": "https://github.com/micropython/micropython/pull/12345",
      "pr_number": 12345,
      "title": "Add feature X"
    }
  ],
  "gh_author": "username"
}
```

## Dependencies

- **pydantic** - Config models with validation
- **cyclopts** - CLI framework
- **GitHub CLI (`gh`)** - PR metadata lookup (optional, warnings issued if not found)

## Testing Notes

Test files should be placed in `tests/` directory. The project uses pytest with coverage reporting configured in `pyproject.toml`.
