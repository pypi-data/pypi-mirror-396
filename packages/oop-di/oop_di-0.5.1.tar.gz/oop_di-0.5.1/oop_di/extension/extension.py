from abc import ABC, abstractmethod
from collections.abc import Callable

from ..definition import Definition
from ..types import NameType, ParamType


class Extension(ABC):
    def __init__(self) -> None:
        self._definitions: dict[NameType, Definition] = {}
        self._params: dict[NameType, ParamType] = {}
        self._aliases: dict[NameType, NameType] = {}
        self.define()

    def add_alias(self, alias: NameType, service: NameType) -> None:
        self._aliases[alias] = service

    def add_service(self, service: type, *, tags: list[str] | None = None, is_singleton: bool = True, **bind: NameType) -> None:
        self._definitions[service] = Definition(service, service, bind, is_singleton=is_singleton, tags=tags or [])

    def add_named_service(self, name: NameType, service: type, *, tags: list[str] | None = None, is_singleton: bool = True, **bind: NameType) -> None:
        self._definitions[name] = Definition(name, service, bind, is_singleton=is_singleton, tags=tags or [])

    def add_factory(self, name: NameType, factory: Callable[..., object], *, tags: list[str] | None = None, is_singleton: bool = True, **bind: NameType) -> None:
        self._definitions[name] = Definition(name, factory, bind, is_singleton=is_singleton, tags=tags or [])

    def add_param(self, name: NameType, value: ParamType) -> None:
        self._params[name] = value

    def get_definitions(self) -> dict[NameType, Definition]:
        return self._definitions

    def get_aliases(self) -> dict[NameType, NameType]:
        return self._aliases

    def get_params(self) -> dict[NameType, ParamType]:
        return self._params

    @abstractmethod
    def define(self) -> None:
        ...
