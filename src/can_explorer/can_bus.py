from __future__ import annotations

from collections import defaultdict, deque
from typing import Final

from can.bus import BusABC
from can.interfaces import VALID_INTERFACES
from can.listener import Listener
from can.notifier import Notifier

INTERFACES: Final = sorted(list(VALID_INTERFACES))

_BAUDRATES = [33_333, 125_000, 250_000, 500_000, 1_000_000]
BAUDRATES: Final = [format(i, "_d") for i in _BAUDRATES]


class _Listener(Listener):
    def __init__(self, buffer: Recorder, *args, **kwargs):
        self.buffer = buffer
        super().__init__(*args, **kwargs)

    def on_message_received(self, msg) -> None:
        val = int.from_bytes(msg.data, byteorder="big")
        self.buffer[msg.arbitration_id].append(val)


class PayloadBuffer(deque):
    MIN = 50
    MAX = 2500

    def __init__(self):
        super().__init__([0] * self.MAX, maxlen=self.MAX)

    def __getitem__(self, index) -> tuple:  # type: ignore [override]
        # Add ability to utilize slicing
        # Note: must convert deque to avoid runtime error
        if isinstance(index, slice):
            return tuple(self)[index.start : index.stop : index.step]
        return tuple(deque.__getitem__(self, index))


class Recorder(defaultdict):
    _active = False
    _notifier: Notifier
    _listener: _Listener
    _bus: BusABC

    def __init__(self):
        super().__init__(PayloadBuffer)

    @property
    def is_active(self) -> bool:
        return self._active

    def start(self) -> None:
        if self.is_active:
            return

        self._listener = _Listener(self)
        self._notifier = Notifier(self._bus, [self._listener])
        self._active = True

    def stop(self) -> None:
        if not self.is_active:
            return

        self._notifier.stop()  # type: ignore [union-attr]
        self._active = False

    def set_bus(self, bus: BusABC) -> None:
        self._bus = bus
