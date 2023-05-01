import struct
from typing import NamedTuple

from .types import BmdHidJogMode, BmdHidKey


class OnJogEvent(NamedTuple):
    mode: BmdHidJogMode
    value: int

    @staticmethod
    def id() -> int:
        return 3

    @staticmethod
    def read(message: bytes):
        mode, value = struct.unpack_from('<xBix', message)
        return OnJogEvent(BmdHidJogMode(mode), value)

    def serialize(self):
        return struct.pack('<BBiB', self.id(), int(self.mode), self.value, 0xff)


# Key Presses are reported in Input Report ID 4 as an array of 6 LE16 keycodes
# that are currently being held down. 0x0000 is no key. No auto-repeat, no hw
# detection of the 'fast double press'. Every time the set of key being held
# down changes, a new report is sent.
class OnKeyEvent(NamedTuple):
    keys: list[BmdHidKey]

    @staticmethod
    def id() -> int:
        return 4

    @staticmethod
    def read(message: bytes):
        keys = struct.unpack_from('<x6H', message)
        return OnKeyEvent([BmdHidKey(key) for key in keys if key != 0])

    def serialize(self):
        keys = [0, 0, 0, 0, 0, 0]
        for i in range(0, min(len(self.keys), 6)):
            keys[i] = self.keys[i]
        return struct.pack('<B6H', self.id(), *keys)


class OnBatteryEvent(NamedTuple):
    charging: bool
    level: int

    @staticmethod
    def id() -> int:
        return 7

    @staticmethod
    def read(message: bytes):
        charging, level = struct.unpack_from('<x2B', message)
        return OnBatteryEvent(charging, level)

    def serialize(self):
        return struct.pack('<B?B', self.id(), self.charging, self.level)


OnInputEvent = OnJogEvent | OnKeyEvent | OnBatteryEvent
OnInputEvents = {
    OnJogEvent.id(): OnJogEvent,
    OnKeyEvent.id(): OnKeyEvent,
    OnBatteryEvent.id(): OnBatteryEvent,
}
