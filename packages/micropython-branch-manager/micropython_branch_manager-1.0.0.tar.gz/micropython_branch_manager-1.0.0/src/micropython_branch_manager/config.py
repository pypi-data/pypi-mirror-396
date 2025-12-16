"""Configuration models for micropython-branch-manager."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from .exceptions import ConfigError

CONFIG_FILENAME = ".micropython-branches.json"
CONFIG_HEADER = "_generated_by"
CONFIG_HEADER_VALUE = "micropython-branch-manager (mbm) - do not edit manually"


class BranchConfig(BaseModel):
    """Configuration for a single feature branch."""

    name: str
    remote: str = "origin"
    pr_url: str | None = None
    pr_number: int | None = None
    title: str | None = None


class MicroPythonConfig(BaseModel):
    """Root configuration model."""

    model_config = ConfigDict(extra="ignore")

    integration_branch: str = "main"
    remotes: dict[str, str] = Field(default_factory=dict)
    branches: list[BranchConfig] = Field(default_factory=list)

    @classmethod
    def load(cls, submodule_path: Path, require_exists: bool = False) -> "MicroPythonConfig":
        """Load from .micropython-branches.json in submodule root.

        Args:
            submodule_path: Path to the submodule directory.
            require_exists: If True, raise ConfigError if config file doesn't exist.
        """
        config_path = submodule_path / CONFIG_FILENAME
        if not config_path.exists():
            if require_exists:
                raise ConfigError(
                    f"No config file found. Run 'mbm init' first to create {CONFIG_FILENAME}"
                )
            return cls()
        return cls.model_validate_json(config_path.read_text())

    def save(self, submodule_path: Path) -> None:
        """Save to .micropython-branches.json in submodule root."""
        config_path = submodule_path / CONFIG_FILENAME
        # Build dict with header field first, then model fields
        data = {CONFIG_HEADER: CONFIG_HEADER_VALUE, **self.model_dump()}
        config_path.write_text(json.dumps(data, indent=2) + "\n")

    def get_branch(self, name: str) -> BranchConfig | None:
        """Get branch config by name."""
        return next((b for b in self.branches if b.name == name), None)

    def has_branch(self, name: str) -> bool:
        """Check if branch exists in config."""
        return any(b.name == name for b in self.branches)
