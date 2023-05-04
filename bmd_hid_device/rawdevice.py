#!/usr/bin/env python3
import threading
from typing import Optional, Callable

import hid

from .auth import Authenticator
from .protocol.events import OnInputEvent, OnInputEvents
from .protocol.features import DeviceFeatureMessage, DeviceFeatureMessages
from .protocol.requests import SetConfigRequest, SetConfigRequests
from .util.deviceinfo import HidDeviceInfo
from .util.messagehandler import MessageHandler


class BmdRawDevice:
    dev: Optional[hid.Device]
    device_info: HidDeviceInfo
    on_close: Optional[Callable[[], None]]
    authenticator: Authenticator

    on_input_event_handler: MessageHandler[OnInputEvent]
    set_config_request_handler: MessageHandler[SetConfigRequest]
    device_feature_handler: MessageHandler[DeviceFeatureMessage]

    serial: str
    timeout: int = 0

    def __init__(self, device_info: HidDeviceInfo, on_close: Optional[Callable[[], None]] = None):
        try:
            self.dev = hid.Device(
                vid=device_info["vendor_id"],
                pid=device_info["product_id"],
                serial=device_info["serial_number"]
            )
        except hid.HIDException as e:
            self.close()
            raise e
        self.on_input_event_handler = MessageHandler(OnInputEvents)
        self.set_config_request_handler = MessageHandler(SetConfigRequests)
        self.device_feature_handler = MessageHandler(DeviceFeatureMessages)

        self.on_close = on_close
        self.device_info = device_info
        self.authenticator = Authenticator(self.poll_feature, self.send_feature, 2000, self.close)
        self.authenticator.start()

    def __str__(self):
        return "{0} {1}, {2}".format(
            self.device_info["manufacturer_string"],
            self.device_info["product_string"],
            self.device_info["serial_number"]
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def isclosed(self):
        return self.dev is None

    def close(self):
        if self.dev is not None:
            self.dev.close()
            self.dev = None
        self.authenticator.stop()
        if self.on_close is not None:
            self.on_close()

    def poll(self, timeout: Optional[int] = None) -> Optional[OnInputEvent]:
        if self.isclosed():
            raise hid.HIDException("device is closed")
        try:
            data = self.dev.read(4096, timeout=timeout)
        except hid.HIDException as e:
            self.close()
            raise e
        if data is None:
            return None
        return self.on_input_event_handler.parse(data)

    def send(self, message: SetConfigRequest):
        if self.isclosed():
            raise hid.HIDException("device is closed")
        try:
            self.dev.write(self.set_config_request_handler.serialize(message))
        except hid.HIDException as e:
            self.close()
            raise e

    def poll_feature(self):
        if self.isclosed():
            raise hid.HIDException("device is closed")
        try:
            data = self.dev.get_feature_report(6, 10)
        except hid.HIDException as e:
            self.close()
            raise e
        if data is None:
            return None
        return self.device_feature_handler.parse(data)

    def send_feature(self, message: DeviceFeatureMessage):
        if self.isclosed():
            raise hid.HIDException("device is closed")
        try:
            self.dev.send_feature_report(self.device_feature_handler.serialize(message))
        except hid.HIDException as e:
            self.close()
            raise e

    def __authenticate(self):
        self.timeout = self.authenticator.authenticate()
        # reauthenticate 10 seconds before the timeout
        self.scheduler = threading.Timer(self.timeout - 10, self.__authenticate)
        self.scheduler.start()
        return self.timeout
