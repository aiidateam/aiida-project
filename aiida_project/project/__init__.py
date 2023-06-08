from enum import Enum
from typing import Type

from .base import BaseProject
from .conda import CondaProject
from .venv import VenvProject

__all__ = ["BaseProject", "VenvProject"]


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
