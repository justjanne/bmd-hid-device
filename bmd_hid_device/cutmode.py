import enum

from .protocol.types import BmdHidLed, BmdHidKey


class CutMode(enum.IntEnum):
    CUT = 0x00
    DIS = 0x01
    SMTH_CUT = 0x02

    @staticmethod
    def from_key(key: BmdHidKey):
        if key == BmdHidKey.CUT:
            return CutMode.CUT
        elif key == BmdHidKey.DIS:
            return CutMode.DIS
        elif key == BmdHidKey.SMTH_CUT:
            return CutMode.SMTH_CUT
        else:
            raise Exception("Unknown cut mode: {0}".format(key.name))

    @staticmethod
    def leds() -> BmdHidLed:
        return BmdHidLed.CUT | BmdHidLed.DIS | BmdHidLed.SMTH_CUT

    @staticmethod
    def keys() -> list[BmdHidKey]:
        return [BmdHidKey.CUT, BmdHidKey.DIS, BmdHidKey.SMTH_CUT]

    def led(self) -> BmdHidLed:
        if self == CutMode.CUT:
            return BmdHidLed.CUT
        elif self == CutMode.DIS:
            return BmdHidLed.DIS
        elif self == CutMode.SMTH_CUT:
            return BmdHidLed.SMTH_CUT
        else:
            raise Exception("Unknown cut mode: {0}".format(self.name))

    def key(self) -> BmdHidKey:
        if self == CutMode.CUT:
            return BmdHidKey.CUT
        elif self == CutMode.DIS:
            return BmdHidKey.DIS
        elif self == CutMode.SMTH_CUT:
            return BmdHidKey.SMTH_CUT
        else:
            raise Exception("Unknown cut mode: {0}".format(self.name))
