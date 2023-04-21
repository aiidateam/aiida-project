import shutil
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel


class BaseProject(BaseModel, ABC):
    name: str
    project_path: Path
    venv_path: Path

    _engine = ""

    @property
    def engine(self):
        return self._engine

    @abstractmethod
    def create(self, python_path=None):
        """Create the project."""
        Path(self.project_path, ".aiida").mkdir(parents=True, exist_ok=True)

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
