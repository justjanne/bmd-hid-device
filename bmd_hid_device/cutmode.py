import enum

from .protocol.types import BmdHidLed


class CutMode(enum.IntEnum):
    CUT = 0x00
    DIS = 0x01
    SMTH_CUT = 0x02

    @staticmethod
    def leds() -> BmdHidLed:
        return BmdHidLed.CUT | BmdHidLed.DIS | BmdHidLed.SMTH_CUT

    def led(self) -> BmdHidLed:
        if self == CutMode.CUT:
            return BmdHidLed.CUT
        elif self == CutMode.DIS:
            return BmdHidLed.DIS
        elif self == CutMode.SMTH_CUT:
            return BmdHidLed.SMTH_CUT
        else:
            raise Exception("Unknown cut mode: {0}".format(self))
