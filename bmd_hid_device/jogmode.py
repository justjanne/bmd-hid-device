import enum

from .protocol.types import BmdHidJogLed, BmdHidJogMode


class JogMode(enum.IntEnum):
    SHTL = 0x00
    JOG = 0x01
    SCRL = 0x02

    @staticmethod
    def leds() -> BmdHidJogLed:
        return BmdHidJogLed.SHTL | BmdHidJogLed.JOG | BmdHidJogLed.SCRL

    def mode(self) -> BmdHidJogMode:
        if self == JogMode.SHTL:
            return BmdHidJogMode.ABSOLUTE
        elif self == JogMode.JOG:
            return BmdHidJogMode.RELATIVE
        elif self == JogMode.SCRL:
            return BmdHidJogMode.RELATIVE
        else:
            raise Exception("Unknown jog mode: {0}".format(self))

    def led(self) -> BmdHidJogLed:
        if self == JogMode.SHTL:
            return BmdHidJogLed.SHTL
        elif self == JogMode.JOG:
            return BmdHidJogLed.JOG
        elif self == JogMode.SCRL:
            return BmdHidJogLed.SCRL
        else:
            raise Exception("Unknown jog mode: {0}".format(self))
