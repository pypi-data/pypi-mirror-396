from collections import defaultdict
from collections.abc import Callable
from functools import partial
import inspect
from typing import cast

from .service_builder import ServiceBuilder
from .types import NameType, ParamType


class Container:
    def __init__(self, params: dict[NameType, ParamType]) -> None:
        self._services: dict[NameType, ServiceBuilder] = {}
        self._params: dict[NameType, ParamType] = params
        self._aliases: dict[NameType, NameType] = {}
        self._by_tag: dict[str, list[NameType]] = defaultdict(list)

    def add_alias(self, alias: NameType, service: NameType) -> None:
        self._aliases[alias] = service

    def has(self, name: NameType) -> bool:
        return bool(self.get(name, raise_if_none=False))

    def get(self, name: NameType, *, raise_if_none: bool = True) -> object:
        if isinstance(name, str) and name.startswith("#"):
            return self.get_tagged(name[1:])
        if alias := self._aliases.get(name):
            return self.get(alias)

        if service := self._services.get(name):
            return service.get_instance()

        if param := self._params.get(name):
            return param

        if raise_if_none:
            raise Exception(f"Cannot find {name}")

        return None

    def add_service(self, name: NameType, factory: Callable[[], object], *, is_singleton: bool = True, tags: list[str] | None = None) -> None:
        self._services[name] = ServiceBuilder(factory, is_singleton=is_singleton)
        if not tags:
            return
        for tag in tags:
            self._by_tag[tag].append(name)

    def get_tagged(self, tag: str) -> list[object] | dict[NameType, object]:
        return_dict = tag.startswith("#")
        if return_dict:
            tag = tag[1:]

        names = self._by_tag.get(tag)
        if not names:
            return []

        return {name: self.get(name) for name in names} if return_dict else [self.get(name) for name in names]

    def inject(self, *, ignore_missing: bool = True, **bindings: NameType) -> Callable[..., object]:
        container = self

        def wrapper(f: Callable[..., object]) -> Callable[..., object]:
            args = inspect.getfullargspec(f)
            kwargs = {}
            for arg_name in args.kwonlyargs:
                if binding := bindings.get(arg_name):
                    value = container.get(binding, raise_if_none=not ignore_missing)
                    if value:
                        kwargs[arg_name] = value
                    continue

                try:
                    value = container.get(cast("NameType", args.annotations[arg_name]), raise_if_none=False) or container.get(
                        arg_name, raise_if_none=not ignore_missing
                    )
                    if value:
                        kwargs[arg_name] = value
                except KeyError:
                    value = container.get(arg_name, raise_if_none=not ignore_missing)
                    kwargs[arg_name] = value

            return partial(f, **kwargs)

        return wrapper
