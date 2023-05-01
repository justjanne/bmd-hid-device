from typing import Callable

from .protocol.types import BmdHidKey


class InputEventHandler:
    on_key_down: Callable[[BmdHidKey], None]
    on_key_up: Callable[[BmdHidKey], None]

    keys: set[BmdHidKey] = set()

    def __init__(self, on_key_down, on_key_up):
        self.on_key_down = on_key_down
        self.on_key_up = on_key_up

    def update(self, keys: set[BmdHidKey]):
        removed = self.keys - keys
        added = keys - self.keys
        self.keys = keys
        for key in removed:
            self.on_key_up(key)
        for key in added:
            self.on_key_down(key)
