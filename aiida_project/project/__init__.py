from .base import EngineType, ProjectDict, BaseProject
from .venv import VenvProject
from .conda import CondaProject
from typing import Type

__all__ = [
    "EngineType",
    "BaseProject",
    "VenvProject",
    "ProjectDict",
]


def load_project_class(engine_type: str) -> Type[BaseProject]:
    """Load the project class corresponding the engine type."""
    engine_project_dict = {
        "venv": VenvProject,
        "conda": CondaProject,
    }
    return engine_project_dict[engine_type]
