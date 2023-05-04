import threading
from typing import Optional, Callable

import hid

from .protocol import crypto
from .protocol.features import DeviceFeatureMessage, AuthFeatureMessage
from .protocol.types import BmdHidHandshakeStep
from .util.timeout import Timeout


class Authenticator:
    _timeout: int
    _poll: Callable[[], DeviceFeatureMessage]
    _send: Callable[[DeviceFeatureMessage], None]
    _scheduler: Optional[threading.Timer]
    _on_close: Optional[Callable[[], None]]

    _our_challenge: int
    _their_challenge: int

    def __init__(self,
                 poll: Callable[[], Optional[DeviceFeatureMessage]],
                 send: Callable[[DeviceFeatureMessage], None],
                 timeout: int = 2000,
                 on_close: Optional[Callable[[], None]] = None):
        self._timeout = timeout
        self._poll = poll
        self._send = send
        self._scheduler = None
        self._on_close = on_close

        self._our_challenge = 0x0000000000000000
        self._their_challenge = 0x0000000000000000

    def handle(self, message: DeviceFeatureMessage) -> Optional[int]:
        if not isinstance(message, AuthFeatureMessage):
            return None
        if message.step == BmdHidHandshakeStep.PC_CHALLENGE:
            self._their_challenge = message.data
            self._send(AuthFeatureMessage(BmdHidHandshakeStep.DEVICE_CHALLENGE, self._our_challenge))
            return None
        elif message.step == BmdHidHandshakeStep.DEVICE_RESPONSE:
            self._send(
                AuthFeatureMessage(BmdHidHandshakeStep.PC_RESPONSE, crypto.solve_challenge(self._their_challenge)))
            return None
        elif message.step == BmdHidHandshakeStep.RESULT:
            return message.data
        return None

    def authenticate(self):
        deadline = Timeout(self._timeout)
        self._send(AuthFeatureMessage(BmdHidHandshakeStep.PC_CHALLENGE, 0))
        result = None
        while result is None and deadline.remaining():
            result = self.handle(self._poll())
        if result is None or result == 0:
            self.stop()
            self._on_close()
            raise hid.HIDException("Could not authenticate with device")
        return result

    def start(self):
        self.stop()
        interval = self.authenticate()
        self._scheduler = threading.Timer(interval / 2, self.authenticate)
        self._scheduler.start()

    def stop(self):
        if self._scheduler is not None:
            self._scheduler.cancel()
            self._scheduler.join()
            self._scheduler = None
