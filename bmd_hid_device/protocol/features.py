import struct
from typing import NamedTuple

from .types import BmdHidHandshakeStep


class AuthFeatureMessage(NamedTuple):
    step: BmdHidHandshakeStep
    data: int

    @staticmethod
    def id():
        return 6

    @staticmethod
    def read(message: bytes):
        step, data = struct.unpack_from('<xBQ', message)
        return AuthFeatureMessage(BmdHidHandshakeStep(step), data)

    def serialize(self) -> bytes:
        return struct.pack('<BBQ', self.id(), int(self.step), self.data)


class SerialFeatureMessage(NamedTuple):
    device_serial: str

    @staticmethod
    def id():
        return 8

    @staticmethod
    def read(message: bytes):
        device_serial: bytes
        device_serial, = struct.unpack_from('<x32s', message)
        return SerialFeatureMessage(device_serial.decode('ascii'))

    def serialize(self) -> bytes:
        return struct.pack('<B32s', self.id(), self.device_serial.encode('ascii'))


DeviceFeatureMessage = AuthFeatureMessage | SerialFeatureMessage
DeviceFeatureMessages = {
    AuthFeatureMessage.id(): AuthFeatureMessage,
    SerialFeatureMessage.id(): SerialFeatureMessage,
}
