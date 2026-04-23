"""Functionality to support various shells with `aiida-project`."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from importlib import resources
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator

BLOCK_START = "# >>> aiida-project >>>"
BLOCK_END = "# <<< aiida-project <<<"


class ShellType(str, Enum):
    bash = "bash"
    zsh = "zsh"
    fish = "fish"

    @property
    def rc_file(self) -> Path | None:
        """Absolute path to the shell's rc file, or None if not applicable."""
        return {
            ShellType.bash: Path.home() / ".bashrc",
            ShellType.zsh: Path.home() / ".zshrc",
        }.get(self)


class Shell(BaseModel):
    config_file: Path
    """Path to shell configuration relative to home directory."""
    init_lines: str
    """Lines to add to the shell configuration files when using `aiida-project init`."""
    activate: str
    """AiiDA-specific lines to add to the environment's activate script."""
    deactivate: str
    """AiiDA-specific lines to add to the environment's deactivate script."""
    version: int
    """Shell config version from shell_fields.yaml."""

    @field_validator("config_file")
    @classmethod
    def resolve_config_file(cls, value: Path) -> Path:
        """Resolve the shell configuration file."""
        return Path.home() / value

    def write_config(self, env_file_path: str | Path) -> bool:
        """Write init lines to the dedicated config file.

        Returns True if this is a re-init (file already existed).
        """
        is_reinit = self.config_file.exists()
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.config_file.write_text(
            f"# version: {self.version}\n" + self.init_lines.format(env_file_path=env_file_path)
        )
        return is_reinit

    def ensure_source_line(self, rc_file: Path) -> None:
        """Add source line block to rc_file if not already present."""
        rc_file.touch(exist_ok=True)

        if BLOCK_START not in rc_file.read_text():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with rc_file.open("a") as handle:
                handle.write(
                    f"\n{BLOCK_START}\n"
                    f"# Configured on {timestamp}\n"
                    f"source {self.config_file}\n"
                    f"{BLOCK_END}\n"
                )

    def _installed_version(self) -> int:
        """Read the version from the installed config file."""
        first_line = self.config_file.read_text().split("\n")[0]
        try:
            return int(first_line.removeprefix("# version: "))
        except ValueError:
            return 0

    @property
    def is_outdated(self) -> bool:
        """Whether the installed shell config is older than the current version."""
        if not self.config_file.exists():
            return False
        return self._installed_version() < self.version


def load_shell(shell_str: str) -> Shell:
    """Load the shell configuration for the given shell type."""
    from . import data

    with (resources.files(data) / "shell_fields.yaml").open("r") as handle:
        specs = yaml.safe_load(handle)
    return Shell(version=specs["version"], **specs[shell_str])
