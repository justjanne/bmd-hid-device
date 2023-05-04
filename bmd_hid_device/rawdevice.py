#!/usr/bin/env python3
import threading
from typing import Optional

import hid

from .auth import Authenticator
from .protocol.events import OnInputEvent, OnInputEvents
from .protocol.features import DeviceFeatureMessages, DeviceFeatureMessage, SerialFeatureMessage
from .protocol.requests import SetConfigRequest, SetConfigRequests
from .util.deviceinfo import HidDeviceInfo
from .util.messagehandler import MessageHandler


class BmdRawDevice:
    dev: Optional[hid.Device]
    scheduler: Optional[threading.Timer] = None

    on_input_event_handler: MessageHandler[OnInputEvent]
    set_config_request_handler: MessageHandler[SetConfigRequest]
    device_feature_handler: MessageHandler[DeviceFeatureMessage]

    serial: str
    timeout: int = 0

    def __init__(self, device_info: HidDeviceInfo):
        self.dev = hid.Device(vid=device_info["vendor_id"], pid=device_info["product_id"],
                              serial=device_info["serial_number"])
        self.on_input_event_handler = MessageHandler(OnInputEvents)
        self.set_config_request_handler = MessageHandler(SetConfigRequests)
        self.device_feature_handler = MessageHandler(DeviceFeatureMessages)

    def __str__(self):
        return "{0} {1}, {2}".format(self.dev.manufacturer, self.dev.product, self.serial)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def isclosed(self):
        return self.dev is None

    def close(self):
        if self.scheduler is not None:
            self.scheduler.cancel()
            self.scheduler.join()
            self.scheduler = None
        if self.dev is not None:
            self.dev.close()
            self.dev = None

    def poll(self, timeout: Optional[int] = None) -> Optional[OnInputEvent]:
        if self.dev is None:
            raise IOError("device is closed")
        data = self.dev.read(4096, timeout=timeout)
        if data is None:
            return None
        return self.on_input_event_handler.parse(data)

    def send(self, message: SetConfigRequest):
        if self.dev is None:
            raise IOError("device is closed")
        self.dev.write(self.set_config_request_handler.serialize(message))

    def authenticate(self):
        # TODO: parse feature report 1 (length 8), used for unknown purposes
        serial_message = self.device_feature_handler.parse(self.dev.get_feature_report(8, 33))
        if not isinstance(serial_message, SerialFeatureMessage):
            raise IOError("Could not parse serial message")
        if serial_message.device_serial != self.dev.serial:
            raise IOError("Device serial and descriptor serial do not match: {0}, {1}".format(
                serial_message.device_serial,
                self.dev.serial
            ))
        self.serial = serial_message.device_serial
        self.__authenticate()

    def __authenticate(self):
        self.timeout = Authenticator(self.dev).authenticate()
        # reauthenticate 10 seconds before the timeout
        self.scheduler = threading.Timer(self.timeout - 10, self.__authenticate)
        self.scheduler.start()
        return self.timeout
