from __future__ import annotations

from collections import defaultdict, deque
from random import randint
from typing import Final

from can import Message
from can.bus import BusABC
from can.interfaces import VALID_INTERFACES
from can.listener import Listener as _Listener
from can.notifier import Notifier

from can_explorer.configs import Default

INTERFACES: Final = sorted(list(VALID_INTERFACES))

_BAUDRATES = [33_333, 125_000, 250_000, 500_000, 1_000_000]
BAUDRATES: Final = [format(i, "_d") for i in _BAUDRATES]


def generate_random_can_message() -> Message:
    """
    Generate a random CAN message.
    """
    message_id = randint(1, 25)
    data_length = randint(1, 8)
    data = (randint(0, 255) for _ in range(data_length))
    return Message(arbitration_id=message_id, data=data)


class PayloadBuffer(deque):
    def __init__(self):
        self.MIN = Default.BUFFER_MIN
        self.MAX = Default.BUFFER_MAX
        super().__init__([0] * self.MAX, maxlen=self.MAX)

    def __getitem__(self, index) -> tuple:  # type: ignore [override]
        # Add ability to utilize slicing
        # Note: must convert deque to avoid runtime error
        if isinstance(index, slice):
            return tuple(self)[index.start : index.stop : index.step]
        return tuple(deque.__getitem__(self, index))


class Listener(_Listener):
    def __init__(self, recorder: Recorder, *args, **kwargs):
        self.recorder = recorder
        super().__init__(*args, **kwargs)

    def on_message_received(self, message) -> None:
        self.recorder.add_message(message)


class Recorder:
    _active = False
    _bus: BusABC
    _listener: Listener
    _notifier: Notifier

    def __init__(self):
        self._data = defaultdict(PayloadBuffer)

    def is_active(self) -> bool:
        return self._active

    def start(self) -> None:
        if self.is_active():
            return

        if self._bus is None:
            raise Exception("Error: must set bus before starting.")

        self._listener = Listener(self)
        self._notifier = Notifier(self._bus, [self._listener])
        self._active = True

    def stop(self) -> None:
        if not self.is_active():
            return

        self._notifier.stop()
        self._active = False

    def add_message(self, message: Message) -> None:
        val = int.from_bytes(message.data, byteorder="big")
        self._data[message.arbitration_id].append(val)

    def clear_data(self) -> None:
        self._data.clear()

    def get_data(self) -> dict:
        return self._data.copy()

    def set_bus(self, bus: BusABC) -> None:
        self._bus = bus
