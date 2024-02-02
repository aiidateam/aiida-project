from __future__ import annotations

import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Union
from ..config import ProjectConfig
from enum import Enum

from pydantic import BaseModel


def recursive_mkdir(project_path: Path, structure: Union[dict, list, Path]) -> None:
    """Recursively make the provided directory structure."""
    if isinstance(structure, dict):
        for key, value in structure.items():
            Path(project_path, key).mkdir(exist_ok=True, parents=True)
            recursive_mkdir(Path(project_path, key), value)
    elif isinstance(structure, list):
        for value in structure:
            Path(project_path, value).mkdir(exist_ok=True, parents=True)


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


class BaseProject(BaseModel, ABC):
    name: str
    project_path: Path
    venv_path: Path
    dir_structure: Union[Dict[str, Union[dict, list, Path]], List[Path], Path]

    _engine = ""

    @property
    def engine(self):
        return self._engine

    @abstractmethod
    def create(self, python_path: Path):
        """Create the project."""
        Path(self.project_path, ".aiida").mkdir(parents=True, exist_ok=True)
        recursive_mkdir(self.project_path, self.dir_structure)

    @abstractmethod
    def destroy(self):
        """Destroy the project."""
        shutil.rmtree(self.project_path, ignore_errors=True)

    @abstractmethod
    def append_activate_text(self, text: str) -> None:
        """Append a text to the activate script."""

    @abstractmethod
    def append_deactivate_text(self, text: str) -> None:
        """Append a text to the deactivate script."""

    @abstractmethod
    def install(self, package):
        """Install a package from PyPI."""

    @abstractmethod
    def install_local(self, path):
        """Install a package from a local directory."""

    def clone_repo(self, repo, path):
        """Clone a ``git`` repository from a remote source."""
        clone_command = ["git", "clone", "--single-branch", f"{repo}", f"{path.resolve()}"]
        subprocess.run(clone_command, capture_output=True)
