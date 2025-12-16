from collections.abc import Callable
from dataclasses import dataclass

from .types import NameType


@dataclass
class Definition:
    name: NameType
    factory: Callable[..., object]
    bindings: dict[str, NameType]
    is_singleton: bool
    tags: list[str]
