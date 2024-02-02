from pathlib import Path
from typing import Optional

import dotenv
from pydantic import BaseSettings
from rich import print

DEFAULT_PROJECT_STRUCTURE = {
    "setup": [
        "profile",
        "computer",
        "code",
    ],
    "git": [],
}


class ProjectConfig(BaseSettings):
    """Configuration class for configuring `aiida-project`."""

    aiida_venv_dir: Path = Path(Path.home(), ".aiida_venvs")
    aiida_project_dir: Path = Path(Path.home(), "project")
    aiida_default_python_path: Optional[Path] = None
    aiida_project_structure: dict = DEFAULT_PROJECT_STRUCTURE
    aiida_project_shell: str = "bash"

    class Config:
        env_file = Path.home() / Path(".aiida_project.env")
        env_file_encoding = "utf-8"

    def is_not_initialised(self):
        if dotenv.get_key(self.Config.env_file, "aiida_project_shell") is None:
            print("[bold red]Error:[/bold red] The AiiDA project config has not been initialised.")
            print("[bold blue]Info:[/bold blue] Please run `aiida-project init` to get started.")
            return True

    def set_key(self, key, value):
        dotenv.set_key(self.Config.env_file, key, value)

    def get_key(self, key):
        return dotenv.get_key(key)
