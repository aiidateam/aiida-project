from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


def recursive_mkdir(project_path: Path, structure: dict | list | Path) -> None:  # type: ignore[type-arg]
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
    dir_structure: dict[str, dict | list | Path] | list[Path] | Path  # type: ignore[type-arg]

    _engine: str = ""

    @property
    def engine(self) -> str:
        return self._engine

    @abstractmethod
    def create(self, python_path: Path) -> None:
        """Create the project."""
        Path(self.project_path, ".aiida").mkdir(parents=True, exist_ok=True)
        recursive_mkdir(self.project_path, self.dir_structure)

    @abstractmethod
    def destroy(self) -> None:
        """Destroy the project."""
        shutil.rmtree(self.project_path, ignore_errors=True)

    @abstractmethod
    def append_activate_text(self, text: str) -> None:
        """Append a text to the activate script."""

    @abstractmethod
    def append_deactivate_text(self, text: str) -> None:
        """Append a text to the deactivate script."""

    @abstractmethod
    def install(self, packages: list[str]) -> None:
        """Install a list of packages from the PyPI or a GitHub repository."""
