import abc
from typing import Optional

from .devices import BmdDeviceId
from .inputhandler import InputEventHandler
from .ledstatehandler import LedStateHandler
from .protocol.events import OnJogEvent, OnKeyEvent, OnBatteryEvent
from .protocol.requests import SetLedRequest, SetJogLedRequest, SetJogModeRequest
from .protocol.types import BmdHidJogMode, BmdHidKey, BmdHidLed, BmdHidJogLed
from .rawdevice import BmdRawDevice


class BmdHidDevice(abc.ABC):
    _device: BmdRawDevice
    _input: InputEventHandler
    leds: LedStateHandler
    held_keys: list[BmdHidKey]

    def __init__(self, device_id: BmdDeviceId):
        self._device = BmdRawDevice(device_id)
        self._device.authenticate()
        self.held_keys = []

        self._input = InputEventHandler(self.on_key_down, self.on_key_up)
        self.leds = LedStateHandler(self._on_update_system_leds, self._on_update_jog_leds)

    def __str__(self):
        return "BmdHidDevice({0}, timeout {1} sec)".format(self._device, self._device.timeout)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.leds.clear()
        self.close()

    def isclosed(self):
        return self._device.isclosed()

    def close(self):
        self._device.close()

    @abc.abstractmethod
    def on_jog_event(self, mode: BmdHidJogMode, value: int):
        pass

    @abc.abstractmethod
    def on_key_down(self, key: BmdHidKey):
        pass

    @abc.abstractmethod
    def on_key_up(self, key: BmdHidKey):
        pass

    @abc.abstractmethod
    def on_battery(self, charging: bool, level: int):
        pass

    def set_jog_mode(self, mode: BmdHidJogMode):
        self._device.send(SetJogModeRequest(mode, 0))

    def _on_update_system_leds(self, leds: BmdHidLed):
        self._device.send(SetLedRequest(leds))

    def _on_update_jog_leds(self, leds: BmdHidJogLed):
        self._device.send(SetJogLedRequest(leds))

    def poll(self, timeout: Optional[int] = None):
        message = self._device.poll(timeout)
        if message is None:
            return
        if isinstance(message, OnJogEvent):
            self.on_jog_event(message.mode, message.value)
        elif isinstance(message, OnKeyEvent):
            self._input.update(set(message.keys))
            self.held_keys = message.keys
        elif isinstance(message, OnBatteryEvent):
            self.on_battery(message.charging, message.level)
        else:
            raise Exception("Unhandled message {0}".format(type(message)))

    def poll_forever(self):
        while True:
            try:
                self.poll()
            except KeyboardInterrupt:
                print("Thread interrupted via keyboard")
                break
