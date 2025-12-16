from collections.abc import Callable


class ServiceBuilder:
    def __init__(self, factory: Callable[..., object], *, is_singleton: bool) -> None:
        self.factory = factory
        self.is_singleton = is_singleton
        self.instance = None

    def get_instance(self) -> object:
        if not self.is_singleton:
            return self.factory()
        if self.instance:
            return self.instance
        self.instance = self.factory()

        return self.instance
