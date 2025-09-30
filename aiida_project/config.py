from __future__ import annotations

from pathlib import Path
from typing import Any

import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich import print

DEFAULT_PROJECT_STRUCTURE = {
    "setup": [
        "profile",
        "computer",
        "code",
    ],
}


class ProjectConfig(BaseSettings):
    """Configuration class for configuring `aiida-project`."""

    aiida_venv_dir: Path = Path(Path.home(), ".aiida_venvs")
    aiida_project_dir: Path = Path(Path.home(), "project")
    aiida_default_python_path: Path | None = None
    aiida_project_structure: dict[str, Any] = DEFAULT_PROJECT_STRUCTURE
    aiida_project_shell: str = "bash"
    model_config = SettingsConfigDict(
        env_file=Path.home() / Path(".aiida_project.env"), env_file_encoding="utf-8"
    )

    def is_not_initialised(self) -> bool:
        if dotenv.get_key(self.model_config["env_file"], "aiida_project_shell") is None:  # type: ignore[arg-type]
            print("[bold red]Error:[/bold red] The AiiDA project config has not been initialised.")
            print("[bold blue]Info:[/bold blue] Please run `aiida-project init` to get started.")
            return True
        else:
            return False

    def set_key(self, key: str, value: Any) -> None:
        dotenv.set_key(self.model_config["env_file"], key, value)  # type: ignore[arg-type]
