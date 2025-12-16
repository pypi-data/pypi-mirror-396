"""Cooldown lock."""

import threading
import time
from types import TracebackType


class CooldownLock:
    """Cooldown lock."""

    def __init__(self, cooldown: float) -> None:
        """Initialize cooldown lock."""
        self._lock = threading.Lock()
        self._cooldown = cooldown
        self._earliest_use_time = 0

    def acquire(self) -> None:
        """Acquire cooldown lock."""
        self._lock.acquire()

        remaining_cooldown = self._earliest_use_time - time.monotonic()
        if remaining_cooldown > 0:
            time.sleep(remaining_cooldown)

    def release(self) -> None:
        """Release cooldown lock."""
        if not self._lock.locked():
            raise RuntimeError("Lock not held")

        self._earliest_use_time = time.monotonic() + self._cooldown
        self._lock.release()

    def __enter__(self) -> "CooldownLock":
        """Enter cooldown lock."""
        self.acquire()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        """Exit cooldown lock."""
        self.release()
