from collections.abc import Callable
import inspect
from inspect import FullArgSpec
from typing import cast

from .container import Container
from .definition import Definition
from .exception import CircularImportError, DefinitionNotFoundError
from .extension import Extension
from .types import NameType, ParamType


class ContainerDefinition:
    def __init__(self) -> None:
        self._definitions: dict[NameType, Definition] = {}
        self._params: dict[NameType, ParamType] = {}
        self._in_compile: dict[NameType, bool] = {}
        self._aliases: dict[NameType, NameType] = {}

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

    def add_extension(self, extension: Extension) -> None:
        self._definitions.update(extension.get_definitions())
        self._aliases.update(extension.get_aliases())
        self._params.update(extension.get_params())

    def compile(self) -> Container:
        container = Container(self._params)
        for name in self._definitions:
            self._compile_definition(name, container)

        for alias, service in self._aliases.items():
            container.add_alias(alias, service)

        return container

    def _compile_definition(self, name: NameType, container: Container) -> None:
        if name in self._aliases:
            return self._compile_definition(self._aliases[name], container)
        if name in self._params:
            return None

        definition = self._definitions.get(name)
        if not definition:
            raise DefinitionNotFoundError(f"No definition for {name} found")
        if self._in_compile.get(definition.name, None):
            raise CircularImportError("Circular import error")

        self._in_compile[definition.name] = True
        if container.has(definition.name):
            self._in_compile.pop(definition.name)
            return None

        self._resolve_dependencies(definition, container)
        container.add_service(
            definition.name,
            self._bind_factory_to_container(definition, container),
            is_singleton=definition.is_singleton,
            tags=definition.tags,
        )

        self._in_compile.pop(definition.name)
        return None

    @classmethod
    def _bind_factory_to_container(cls, definition: Definition, container: Container) -> Callable[..., object]:
        factory = definition.factory
        bindings = definition.bindings
        args = inspect.getfullargspec(factory)

        def bound_factory() -> object:
            arguments: list[object] = []
            for arg_name in args.args:
                if arg_name == "self":
                    continue
                if binding := bindings.get(arg_name):
                    arguments.append(container.get(binding))
                    continue
                try:
                    arguments.append(
                        container.get(cast("NameType", args.annotations[arg_name]), raise_if_none=False)
                        or container.get(arg_name)
                    )
                except KeyError:
                    arguments.append(container.get(arg_name))
            kwargs = {}
            for arg_name in args.kwonlyargs:
                if binding := bindings.get(arg_name):
                    kwargs[arg_name] = container.get(binding)
                    continue
                if args.kwonlydefaults and args.kwonlydefaults.get(arg_name):
                    d = args.kwonlydefaults.get(arg_name)
                    kwargs[arg_name] = d
                    continue

                try:
                    kwargs[arg_name] = (container.get(cast("NameType", args.annotations[arg_name]), raise_if_none=False)
                                        or container.get(arg_name))
                except KeyError:
                    kwargs[arg_name] = container.get(arg_name)

            return factory(*arguments, **kwargs)

        return bound_factory

    def _resolve_dependencies(self, definition: Definition, container: Container) -> None:
        factory = definition.factory
        bindings = definition.bindings
        args = inspect.getfullargspec(factory)

        self._resolve_args(args, bindings, container)
        self._resolve_kwargs(args, bindings, container)

    def _resolve_kwargs(self, args: FullArgSpec, bindings: dict[str, NameType], container: Container) -> None:
        for arg_name in args.kwonlyargs:
            if binding := bindings.get(arg_name):
                if isinstance(binding, str) and binding.startswith("#"):
                    self._compile_tagged(binding.strip("#"), container)
                    continue
                self._compile_definition(binding, container)
                continue
            if args.kwonlydefaults and args.kwonlydefaults.get(arg_name):
                continue

            try:
                self._compile_definition(cast("NameType", args.annotations[arg_name]), container)
            except (KeyError, DefinitionNotFoundError):
                self._compile_definition(arg_name, container)

    def _resolve_args(self, args: FullArgSpec, bindings: dict[str, NameType], container: Container) -> None:
        for arg_name in args.args:
            if arg_name == "self":
                continue

            if binding := bindings.get(arg_name):
                if isinstance(binding, str) and binding.startswith("#"):
                    self._compile_tagged(binding.strip("#"), container)
                    continue
                self._compile_definition(binding, container)
                continue

            try:
                self._compile_definition(cast("NameType", args.annotations[arg_name]), container)
            except (KeyError, DefinitionNotFoundError):
                self._compile_definition(arg_name, container)

    def _compile_tagged(self, tag: str, container: Container) -> None:
        for name, definition in self._definitions.items():
            if tag in definition.tags:
                self._compile_definition(name, container)
