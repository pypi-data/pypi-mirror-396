class DependencyInjectionError(Exception):
    ...


class CircularImportError(DependencyInjectionError):
    ...


class DefinitionNotFoundError(DependencyInjectionError):
    ...
