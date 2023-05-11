from os import environ
from pathlib import Path
from typing import Dict, Optional, Union

import dotenv
from pydantic import BaseSettings

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


class ProjectConfig(BaseSettings):
    """Configuration class for configuring `aiida-project`."""

    aiida_venv_dir: Path = Path(Path.home(), ".aiida_venvs")
    aiida_project_dir: Path = Path(Path.home(), "project")
    aiida_default_python_path: Optional[Path] = None
    aiida_project_structure: dict = DEFAULT_PROJECT_STRUCTURE

    class Config:
        env_file = Path.home() / Path(".aiida_project.env")
        env_file_encoding = "utf-8"

    def __init__(self, **configuration):
        super().__init__(**configuration)
        env_config = dotenv.dotenv_values(self.Config.env_file)
        if env_config.get("aiida_venv_dir", None) is None:
            dotenv.set_key(
                self.Config.env_file,
                "aiida_venv_dir",
                environ.get("WORKON_HOME", self.aiida_venv_dir.as_posix()),
            )
        if env_config.get("aiida_project_dir", None) is None:
            dotenv.set_key(
                self.Config.env_file, "aiida_project_dir", self.aiida_project_dir.as_posix()
            )


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
