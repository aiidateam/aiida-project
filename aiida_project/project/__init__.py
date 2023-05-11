from enum import Enum
from typing import Type

from .base import BaseProject
from .conda import CondaProject
from .virtualenv import VirtualenvProject

__all__ = ["BaseProject", "VirtualenvProject"]


def load_project_class(engine_type: str) -> Type[BaseProject]:
    """Load the project class corresponding the engine type."""
    engine_project_dict = {
        "virtualenv": VirtualenvProject,
        "conda": CondaProject,
    }
    return engine_project_dict[engine_type]


class EngineType(str, Enum):
    virtualenv = "virtualenv"
    conda = "conda"
