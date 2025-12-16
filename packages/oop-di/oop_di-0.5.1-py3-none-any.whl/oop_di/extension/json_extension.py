import importlib
from json import load
from pathlib import Path
from typing import cast

from ..types import NameType, ParamType
from .extension import Extension


class JsonExtension(Extension):
    def __init__(self, json_path: Path) -> None:
        self.json_path = json_path
        super().__init__()

    def define(self) -> None:
        with Path(self.json_path).open(encoding="utf-8") as file:
            data = cast("dict[str, object]", load(file))

        self._load_parameters(cast("dict[str, ParamType]", data.get("parameters", {})))
        self._load_aliases(cast("dict[str, NameType]", data.get("aliases", {})))
        self._load_services(cast("dict[str, object]", data.get("services", {})))
        importlib.invalidate_caches()

    def _load_parameters(self, data: dict[str, ParamType]) -> None:
        for k, v in data.items():
            self.add_param(self._resolve_key(k), v)

    def _load_aliases(self, data: dict[str, NameType]) -> None:
        for k, v in cast("dict[str,str]", data).items():
            self.add_alias(self._resolve_key(k), self._resolve_key(v))

    def _load_services(self, data: dict[str, object]) -> None:
        for k, v in data.items():
            if not isinstance(v, list):
                raise ValueError(f"services.{k} must be a list")
            self._load_module(k, cast("list[dict[str, object]]", v))

    def _load_module(self, mod: str, data: list[dict[str, object]]) -> None:
        for service in data:
            self._load_service(mod, str(service["class"]), service)

    def _load_service(self, mod: str, item: str, data: dict[str, object]) -> None:
        service = cast("type", self._resolve_key(f"@{mod}.{item}"))
        parameters: dict[str, NameType] = {}
        for k, v in cast("dict[str, str]", data.get("parameters", {})).items():
            parameters[k] = self._resolve_key(v)

        tags = cast("list[str]", data.get("tags", []))
        is_singleton = bool(data.get("is_singleton", True))
        if name := data.get("name"):
            self.add_named_service(
                self._resolve_key(str(name)),
                service,
                tags=tags,
                is_singleton=is_singleton,
                **parameters,
            )
        else:
            self.add_service(
                service, tags=tags, is_singleton=is_singleton, **parameters
            )
        for alias in cast("list[NameType]", data.get("aliases", [])):
            self.add_alias(alias, service)

    @classmethod
    def _resolve_key(cls, key: str) -> NameType:
        if not key.startswith("@"):
            return key

        mod, class_name = key[1:].rsplit(".", 1)
        loaded = importlib.import_module(mod)

        return cast("type", getattr(loaded, class_name))
