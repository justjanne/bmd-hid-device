from typing import NamedTuple


class BmdDeviceId(NamedTuple):
    vid: int
    pid: int


DavinciSpeedEditor = BmdDeviceId(0x1edb, 0xda0e)
DavinciKeyboard = BmdDeviceId(0x1edb, 0xda0b)
