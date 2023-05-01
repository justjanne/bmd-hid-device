from typing import Callable

from .protocol.types import BmdHidLed, BmdHidJogLed


class LedStateHandler:
    on_update_system: Callable[[BmdHidLed], None]
    on_update_jog: Callable[[BmdHidJogLed], None]

    batch_refs: int = 0

    system_changed: bool = False
    jog_changed: bool = False

    system: BmdHidLed
    jog: BmdHidJogLed

    def __init__(self, on_update_system, on_update_jog):
        self.on_update_system = on_update_system
        self.on_update_jog = on_update_jog

    def __enter__(self):
        self.batch_refs += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.batch_refs -= 1
        if self.system_changed:
            self.on_update_system(self.system)
        if self.jog_changed:
            self.on_update_jog(self.jog)

    def _handle_changes(self):
        if self.batch_refs == 0:
            if self.system_changed:
                self.on_update_system(self.system)
            if self.jog_changed:
                self.on_update_jog(self.jog)

    def clear(self):
        self.system = BmdHidLed(0)
        self.jog = BmdHidJogLed(0)
        self.system_changed = True
        self.jog_changed = True
        self._handle_changes()

    def on(self, led: BmdHidLed | BmdHidJogLed):
        if isinstance(led, BmdHidLed):
            self.system |= led
            self.system_changed = True
        if isinstance(led, BmdHidJogLed):
            self.jog |= led
            self.jog_changed = True
        self._handle_changes()

    def off(self, led: BmdHidLed | BmdHidJogLed):
        if isinstance(led, BmdHidLed):
            self.system &= ~led
            self.system_changed = True
        if isinstance(led, BmdHidJogLed):
            self.jog &= ~led
            self.jog_changed = True
        self._handle_changes()

    def update(self, led: BmdHidLed | BmdHidJogLed):
        if isinstance(led, BmdHidLed):
            self.system = led
            self.system_changed = True
        if isinstance(led, BmdHidJogLed):
            self.jog = led
            self.jog_changed = True
        self._handle_changes()
