from typing import Optional

import hid

from .protocol import crypto
from .protocol.features import DeviceFeatureMessages, DeviceFeatureMessage, AuthFeatureMessage
from .protocol.types import BmdHidHandshakeStep
from .util.messagehandler import MessageHandler
from .util.timeout import Timeout


class Authenticator:
    dev: hid.Device
    device_feature_handler: MessageHandler[DeviceFeatureMessage]

    our_challenge = 0
    their_challenge = 0

    def __init__(self, dev: hid.Device):
        self.dev = dev
        self.device_feature_handler = MessageHandler(DeviceFeatureMessages)

    def poll(self):
        data = self.dev.get_feature_report(6, 10)
        return self.device_feature_handler.parse(data)

    def send(self, message: DeviceFeatureMessage):
        data = self.device_feature_handler.serialize(message)
        self.dev.send_feature_report(data)

    def handle(self, message: DeviceFeatureMessage) -> Optional[int]:
        if not isinstance(message, AuthFeatureMessage):
            return None
        if message.step == BmdHidHandshakeStep.PC_CHALLENGE:
            self.their_challenge = message.data
            self.send(AuthFeatureMessage(BmdHidHandshakeStep.DEVICE_CHALLENGE, self.our_challenge))
            return None
        elif message.step == BmdHidHandshakeStep.DEVICE_RESPONSE:
            self.send(AuthFeatureMessage(BmdHidHandshakeStep.PC_RESPONSE, crypto.solve_challenge(self.their_challenge)))
            return None
        elif message.step == BmdHidHandshakeStep.RESULT:
            return message.data
        return None

    def authenticate(self, timeout: Optional[int] = None):
        deadline = Timeout(timeout)
        self.send(AuthFeatureMessage(BmdHidHandshakeStep.PC_CHALLENGE, 0))
        result = None
        while result is None and deadline.remaining():
            result = self.handle(self.poll())
        if result is None:
            raise TimeoutError("Timed out waiting for device auth")
        if result == 0:
            raise RuntimeError("Could not authenticate with device")
        return result
