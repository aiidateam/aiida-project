from enum import Enum
from pathlib import Path
from typing import Dict, Type, Union

from ..config import ProjectConfig
from .base import BaseProject
from .conda import CondaProject
from .venv import VenvProject


def load_project_class(engine_type: str) -> Type[BaseProject]:
    """Load the project class corresponding the engine type."""
    engine_project_dict = {
        "venv": VenvProject,
        "conda": CondaProject,
    }
    return engine_project_dict[engine_type]


class EngineType(str, Enum):
    venv = "venv"
    conda = "conda"


class ProjectDict:
    _projects_path = Path(ProjectConfig().aiida_project_dir, ".aiida_projects")

    def __init__(self):
        if not self._projects_path.exists():
            self._projects_path.joinpath("venv").mkdir(parents=True, exist_ok=True)
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
