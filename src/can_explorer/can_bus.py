from collections import defaultdict, deque
from typing import DefaultDict, Final

from can import bus, interfaces, listener, notifier

INTERFACES: Final = list(interfaces.VALID_INTERFACES)

_BAUDRATES = [33_333, 125_000, 250_000, 500_000, 1_000_000]
BAUDRATES: Final = [format(i, "_d") for i in _BAUDRATES]


class _Listener(listener.Listener):
    def __init__(self, buffer: defaultdict, *args, **kwargs):
        self.buffer = buffer
        super().__init__(*args, **kwargs)

    def on_message_received(self, msg) -> None:
        if self.is_active:
            val = int.from_bytes(msg.data, byteorder="big")
            self.buffer[msg.arbitration_id].append(val)


class _PayloadBuffer(deque):
    maxlen = 2500

    def __init__(self, length: int = 200):
        super().__init__([0] * length)


class Recorder:
    data: DefaultDict[int, _PayloadBuffer] = defaultdict(_PayloadBuffer)
    _active = False
    _notifier = None
    _listener = None

    def __init__(self, bus: bus.BusABC):
        self._bus = bus

        notifier.Notifier(bus, [_Listener(self.data)])

    @property
    def is_active(self) -> bool:
        return self._active

    def start(self) -> None:
        if self.is_active:
            return

        self._listener = _Listener(self.data)
        self._notifier = notifier.Notifier(self._bus, self._listener)
        self._active = True

    def stop(self) -> None:
        if not self.is_active:
            return

        self._notifier.stop()
