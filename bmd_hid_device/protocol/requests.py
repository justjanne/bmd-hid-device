import struct
from typing import NamedTuple

from .types import BmdHidLed, BmdHidJogMode, BmdHidJogLed


class SetLedRequest(NamedTuple):
    leds: BmdHidLed

    @staticmethod
    def id() -> int:
        return 2

    @staticmethod
    def read(message: bytes):
        leds, = struct.unpack_from('<xI', message)
        return SetLedRequest(BmdHidLed(leds))

    def serialize(self) -> bytes:
        return struct.pack('<BI', self.id(), int(self.leds))


class SetJogModeRequest(NamedTuple):
    mode: BmdHidJogMode
    value: int = 0

    @staticmethod
    def id() -> int:
        return 3

    @staticmethod
    def read(message: bytes):
        mode, value = struct.unpack_from('<xBix', message)
        return SetJogModeRequest(BmdHidJogMode(mode), value)

    def serialize(self) -> bytes:
        return struct.pack('<BBiB', self.id(), int(self.mode), self.value, 0xff)


class SetJogLedRequest(NamedTuple):
    leds: BmdHidJogLed

    @staticmethod
    def id() -> int:
        return 4

    @staticmethod
    def read(message: bytes):
        leds, = struct.unpack_from('<xB', message)
        return SetJogLedRequest(BmdHidJogLed(leds))

    def serialize(self) -> bytes:
        return struct.pack('<BB', self.id(), int(self.leds))


SetConfigRequest = SetLedRequest | SetJogModeRequest | SetJogLedRequest
SetConfigRequests = {
    SetLedRequest.id(): SetLedRequest,
    SetJogModeRequest.id(): SetJogModeRequest,
    SetJogLedRequest.id(): SetJogLedRequest,
}
