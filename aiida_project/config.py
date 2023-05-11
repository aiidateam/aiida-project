from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Union

import dotenv
from pydantic import BaseSettings
from rich import print

from .project import load_project_class
from .project.base import BaseProject

DEFAULT_PROJECT_STRUCTURE = {
    "setup": [
        "profile",
        "computer",
        "code",
    ],
    "code": [],
}


class ShellType(str, Enum):
    bash = "bash"
    zsh = "zsh"
    fish = "fish"


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


class ProjectDict:
    _projects_path = Path(ProjectConfig().aiida_project_dir, ".aiida_projects")

    def __init__(self):
        if not self._projects_path.exists():
            self._projects_path.joinpath("virtualenv").mkdir(parents=True, exist_ok=True)
            self._projects_path.joinpath("conda").mkdir(parents=True, exist_ok=True)

    @property
    def projects(self) -> Dict[str, BaseProject]:
        projects = {}
        for project_file in self._projects_path.glob("**/*.json"):
            engine = load_project_class(str(project_file.parent.name))
            project = engine.parse_file(project_file)
            projects[project.name] = project
        return projects

    def add_project(self, project: BaseProject) -> None:
        """Add a project to the configuration files."""
        with Path(self._projects_path, project.engine, f"{project.name}.json").open("w") as handle:
            handle.write(project.json())

    def remove_project(self, project: Union[str, BaseProject]) -> None:
        """Remove a project from the configuration files."""
        project = self.projects[project] if isinstance(project, str) else project
        Path(self._projects_path, project.engine, f"{project.name}.json").unlink()
