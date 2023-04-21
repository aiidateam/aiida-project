from enum import Enum
from pathlib import Path

from .base import BaseProject
from .conda import CondaProject
from .virtualenv import VirtualenvProject


class EngineType(Enum):
    virtualenv = VirtualenvProject
    conda = CondaProject


def get_project(engine: str, name: str, project_path: Path, venv_path: Path) -> BaseProject:
    """Get a ``BaseProject`` instance using the corresponding environment engine."""

    return EngineType[engine].value(name=name, project_path=project_path, venv_path=venv_path)
