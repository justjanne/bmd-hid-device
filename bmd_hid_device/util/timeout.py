import time
from typing import Optional


class Timeout:
    deadline: Optional[int]

    def __init__(self, timeout: Optional[int] = None):
        if timeout is None:
            self.deadline = None
        else:
            self.deadline = time.monotonic_ns() + timeout * 1_000_000

    def remaining(self) -> int:
        return self.deadline is None or self.deadline > time.monotonic_ns()
