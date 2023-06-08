import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Union

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
