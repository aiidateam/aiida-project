"""Functionality to support various shells with `aiida-project`."""

from __future__ import annotations

from enum import Enum
from importlib import resources
from pathlib import Path

import yaml
from pydantic import BaseModel, field_validator


class ShellType(str, Enum):
    bash = "bash"
    zsh = "zsh"
    fish = "fish"


class Shell(BaseModel):
    config_file: Path
    """Path to shell configuration relative to home directory."""
    init_lines: str
    """Lines to add to the shell configuration files when using `aiida-project init`."""
    activate: str
    """AiiDA-specific lines to add to the environment's activate script."""
    deactivate: str
    """AiiDA-specific lines to add to the environment's deactivate script."""

    @field_validator("config_file")
    @classmethod
    def resolve_config_file(cls, value: Path) -> Path:
        """Resolve the shell configuration file."""
        return Path.home() / value


def load_shell(shell_str: str) -> Shell:
    """Load the project class corresponding the engine type."""
    from . import data

    with (resources.files(data) / "shell_fields.yaml").open("r") as handle:
        specs = yaml.safe_load(handle)
    return Shell(**specs[shell_str])
