import binascii
import sys
from typing import Generic, TypeVar, Optional, Callable, Protocol


class SupportsSerialize(Protocol):
    def serialize(self) -> bytes: ...

    @staticmethod
    def read(data: bytes): ...


T = TypeVar('T', bound=SupportsSerialize)


class MessageHandler(Generic[T]):
    types: dict[int, T]
    serializers: dict[T, Callable[[T], bytes]]

    def __init__(self, types):
        self.types = types

    def parse(self, data: bytes) -> Optional[T]:
        if len(data) == 0:
            return None
        message_id = data[0]
        if message_id not in self.types:
            print("Unhandled message {0} {1}"
                  .format(message_id, binascii.b2a_hex(data).decode('utf-8')),
                  file=sys.stderr)
            return None
        return self.types[message_id].read(data)

    def serialize(self, message: T) -> bytes:
        return message.serialize()
