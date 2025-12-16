import os

from .extension import Extension


class EnvExtension(Extension):
    def __init__(self, *, keys_to_lower: bool = True) -> None:
        self.keys_to_lower = keys_to_lower
        super().__init__()

    def define(self) -> None:
        for k, v in os.environ.items():
            self.add_param(k.lower() if self.keys_to_lower else k, v)
