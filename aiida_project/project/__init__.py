from enum import Enum

from .base import BaseProject
from .conda import CondaProject
from .virtualenv import VirtualenvProject

__all__ = ["BaseProject"]


class EngineType(Enum):
    virtualenv = VirtualenvProject
    conda = CondaProject
