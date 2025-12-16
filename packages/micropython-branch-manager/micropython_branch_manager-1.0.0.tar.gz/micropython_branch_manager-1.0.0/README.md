# micropython-branch-manager

Tool for managing MicroPython fork integration branches.

## Overview

`micropython-branch-manager` (alias: `mbm`) automates the workflow of maintaining a MicroPython fork with multiple feature branches integrated on top of upstream. It handles:

- Rebasing integration branches onto upstream with preserved merge commits
- Adding PRs from upstream via merge commits
- Tracking branch metadata in versioned JSON config
- Safety checks for remote divergence
- Generating GitLab MR URLs

## Installation

```bash
uv tool install micropython-branch-manager
```

Or install from source:

```bash
git clone <repository-url>
cd micropython-branch-manager
uv sync
uv pip install -e .
```

## Usage

### Initialize configuration

Initialize config in a MicroPython submodule. Automatically detects the current branch and existing git remotes:

```bash
cd path/to/micropython
mbm init
```

Or specify the integration branch explicitly:

```bash
mbm init --integration-branch main
```

### Rebase integration branch

Rebase the integration branch and all feature branches onto upstream:

```bash
mbm rebase upstream/master
```

Options:
- `--local` - Skip fetch and push operations
- `--dry-run` - Show what would happen without making changes
- `--force-push` - Skip remote divergence checks (use with caution)
- `--resume` - Resume after resolving conflicts

### Add a PR to integration branch

Add an upstream PR via merge commit. The PR author's fork is automatically detected and a remote is created if needed:

```bash
mbm add-pr 12345                                    # By PR number
mbm add-pr feature-branch                           # By branch name
mbm add-pr https://github.com/.../pull/12345       # By URL
```

The command will:
1. Fetch PR metadata from GitHub (including author)
2. Find or create a remote for the author's fork
3. Fetch the PR branch from upstream
4. Merge it into the update branch
5. Push the update branch to GitLab
6. Display a GitLab MR creation URL

### Sync configuration

Update JSON config to match current merge commit history. Requires a GitHub username to look up PR metadata:

```bash
mbm sync <github-username>
```

### Show configuration

Display current configuration:

```bash
mbm config
```

## Example Usage

### Setting up a new integration branch

```bash
# Navigate to MicroPython submodule and checkout your integration branch
cd path/to/micropython
git checkout mimxrt

# Initialize mbm - auto-detects current branch and remotes
mbm init
# Output:
# Using current branch as integration branch: mimxrt
#
# Detected 3 remote(s):
#   - andrewleech: git@github.com:andrewleech/micropython.git
#   - gitlab: git@gitlab.example.com:yourname/micropython.git
#   - upstream: https://github.com/micropython/micropython.git
#
# Created .micropython-branches.json
```

### Adding PRs to the integration branch

```bash
# Add first PR - remote auto-detected from PR author
mbm add-pr 18333
# Output:
# Fetching PR info for: 18333
# Found PR #18333: ports/mimxrt: Update nxp_driver to MCUX_2.16.100.
# Branch: mcux_sdk_2.16
# State: OPEN
#
# Creating update branch from mimxrt...
# Fetching PR #18333 from upstream...
#
# Updating config...
# Merging mcux_sdk_2.16 into mimxrt_update...
# Merge completed successfully
#
# Pushing mimxrt_update to gitlab...
#
# === PR ADDED SUCCESSFULLY ===
# PR #18333: ports/mimxrt: Update nxp_driver to MCUX_2.16.100.
# Branch: mcux_sdk_2.16
#
# Create MR: https://gitlab.example.com/.../merge_requests/new?...

# Add more PRs - each builds on the previous update branch
mbm add-pr 18229
mbm add-pr 18398
mbm add-pr 18392

# When adding a PR from a new author, remote is created automatically
mbm add-pr 18515
# Output includes:
# Adding remote 'APIUM' -> https://github.com/APIUM/micropython.git
#
# At the end, a clickable GitLab MR URL is shown that pre-fills
# the title and description with all integrated branches
```

### Viewing current configuration

```bash
mbm config
# Output:
# Integration branch: mimxrt
#
# Branches (8):
#   andrewleech/mcux_sdk_2.16: ports/mimxrt: Update nxp_driver to MCUX_2.16.100.
#     - https://github.com/micropython/micropython/pull/18333
#   andrewleech/manifest_c_module: Add c_module() manifest function for user C modules
#     - https://github.com/micropython/micropython/pull/18229
#   alonbl/adc: mimxrt: adc: rt117x: initialize LPADC2 and support channel groups
#     - https://github.com/micropython/micropython/pull/17874
#   APIUM/mimxrt1176-alt11-pwm: mimxrt: Add ALT11 pin mode support for MIMXRT1176.
#     - https://github.com/micropython/micropython/pull/18515
#
# Remotes (4):
#   APIUM: https://github.com/APIUM/micropython.git
#   alonbl: https://github.com/alonbl/micropython.git
#   andrewleech: git@github.com:andrewleech/micropython.git
#   upstream: https://github.com/micropython/micropython.git
```

### Generated GitLab MR

The MR creation URL pre-fills the title and description with all integrated branches:

![GitLab MR Example](docs/gitlab_mr_example.png)

## Configuration File

The configuration file `.micropython-branches.json` is auto-generated by `mbm init` and updated by other commands. It should not be edited manually.

Example configuration:

```json
{
  "_generated_by": "micropython-branch-manager (mbm) - do not edit manually",
  "integration_branch": "main",
  "remotes": {
    "upstream": "https://github.com/micropython/micropython.git",
    "andrewleech": "https://github.com/andrewleech/micropython.git"
  },
  "branches": [
    {
      "name": "feature-branch-1",
      "remote": "andrewleech",
      "pr_url": "https://github.com/micropython/micropython/pull/12345",
      "pr_number": 12345,
      "title": "Add feature X"
    }
  ]
}
```

Fields:
- `integration_branch` - The branch that integrates all feature branches
- `remotes` - Git remotes used by the tool (auto-detected from git config)
- `branches` - List of integrated feature branches with their metadata

## Workflow

### Rebase strategy

Each PR is rebased independently onto the target (e.g., `upstream/master`), then merged sequentially into the update branch. This keeps feature branches as clean forks from upstream:

```
*   c1c523ebd7 - Merge branch 'mimxrt1176-alt11-pwm' (HEAD -> mimxrt_update)
|\
| * e16d226353 - mimxrt: Add ALT11 pin mode support for MIMXRT1176. (mimxrt1176-alt11-pwm)
* |   a288f37e95 - Merge branch 'adc'
|\ \
| * | 30aa89db5e - mimxrt/machine_adc: rt117x: Support channel groups. (adc)
| * | b045f8ae4f - mimxrt/machine_adc: rt117x: Initialize LPADC2.
* | |   6f84252a13 - Merge branch 'mimx_sdcard_timeouts'
|\ \ \
| * | | 623409093a - mimxrt/sdcard: Improve robustness of sdcard driver. (mimx_sdcard_timeouts)
| * | | 5dd59d4e07 - mimxrt/sdcard: Fix deadlock in sdcard_power_off.
* | | |   62c3ccf986 - Merge branch 'mimx_Flash_doc'
|\ \ \ \
| * | | | cad3bd124a - docs/mimxrt: Add docs for mimxrt.Flash. (mimx_Flash_doc)
| |/ / /
* | | |   864c580cfa - Merge branch 'dp83867-phy-driver'
|\ \ \ \
| * | | | 76fcf3ce95 - mimxrt/eth: Improve Dual Ethernet configuration. (dp83867-phy-driver)
| * | | | 7ad3bbaff7 - mimxrt/boards/MIMXRT1170_EVK: Remove obsolete pin defines.
| * | | | 6a70a07795 - mimxrt/eth: Add DP83867 PHY driver support.
| |/ / /
* | | |   03163eaaeb - Merge branch 'phyboard-rt1170'
|\ \ \ \
| * | | | 99d763bffb - mimxrt: Add PHYBOARD-RT1170 board support. (phyboard-rt1170)
| |/ / /
* | | |   345a5419a3 - Merge branch 'manifest_c_module'
|\ \ \ \
| * | | | 12b45387e5 - tools/ci: Add c_module() testing for RP2 and STM32. (manifest_c_module)
| * | | | ... (more commits)
* | | | |   b61786d615 - Merge branch 'mcux_sdk_2.16'
|\ \ \ \ \
| * | | | | 66be1ee6a8 - mimxrt/fsl_lpuart: Use wrapper for IRQ Idle support. (mcux_sdk_2.16)
| * | | | | 8c34a2df96 - ports/mimxrt: Update nxp_driver to MCUX_2.16.100.
|/ / / / /
* / / / / 78ff170de9 - all: Bump version to 1.27.0. (upstream/master, mimxrt)
```

Each feature branch forks directly from `upstream/master`, and all merges flow into the update branch.

### Typical rebase workflow

1. Fetch latest from all remotes
2. Create update branch from target (e.g., `upstream/master`)
3. For each PR in config order:
   - Fetch fresh PR content from upstream
   - Rebase onto target
   - Merge into update branch
4. Push feature branches to their GitHub forks
5. Push update branch to GitLab
6. Display GitLab MR URL for review

### Push strategy

- **Feature branches**: Pushed to their respective GitHub forks (remote specified in config)
- **Update branch**: Pushed to GitLab for MR creation
- The config file is included in each merge commit for traceability

## Safety Features

### Remote divergence detection

Before force-pushing rebased branches, the tool checks if remote branches have been updated:

1. Compares local and remote branch tips using `git rev-list`
2. Collects all divergence errors and reports them at the end
3. Continues pushing other branches even if some diverge
4. Use `--force-push` to override divergence checks

Skip pushing entirely with `--local` flag.

## Conflict Handling

When rebase conflicts occur:

1. The tool identifies which PR caused the conflict
2. Displays conflicting files and resolution instructions
3. Saves progress to `.git/mbm-rebase-state.json`
4. User resolves conflicts and runs `git rebase --continue`
5. Resume with `mbm rebase --resume`

Example:

```
Rebase stopped due to conflicts while integrating PR #12345 (feature-branch).
Conflicting files:
  ports/stm32/main.c
  py/compile.c

Please resolve conflicts manually, then run:
  cd /path/to/micropython
  git rebase --continue

Then resume the integration:
  mbm rebase --resume
```

## Development

### Setup

```bash
git clone <repository-url>
cd micropython-branch-manager
uv sync
```

### Run tests

```bash
uv run pytest tests/ -v
```

### Linting

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src/micropython_branch_manager
```

### Pre-commit hooks

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

## Requirements

- Python 3.11+
- Git
- GitHub CLI (`gh`) - for PR metadata lookup
  - Install: https://cli.github.com/
  - Authenticate: `gh auth login`

## Versioning & Releases

This project uses **dynamic versioning** from git tags via `hatch-vcs`.

- Version is automatically determined from git tags
- Release process: Create and push a git tag (e.g., `v1.0.0`)
- CI automatically publishes tagged releases to PyPI

Example release workflow:
```bash
git tag v1.0.0
git push origin v1.0.0  # Triggers CI deployment to PyPI
```

Between releases, development versions include git commit info (e.g., `0.1.1.dev0+g08d098b.d20251212`).

## License

MIT
