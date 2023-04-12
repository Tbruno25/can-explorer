from collections import defaultdict, deque
from typing import Final

from can import bus, interfaces, listener, notifier

INTERFACES: Final = list(interfaces.VALID_INTERFACES)

_BAUDRATES = [33_333, 125_000, 250_000, 500_000, 1_000_000]
BAUDRATES: Final = [format(i, "_d") for i in _BAUDRATES]


class _Listener(listener.Listener):
    def __init__(self, buffer: defaultdict, *args, **kwargs):
        self.buffer = buffer
        super().__init__(*args, **kwargs)

    def on_message_received(self, msg):
        val = int.from_bytes(msg.data, byteorder="big")
        self.buffer[msg.arbitration_id].append(val)


class _PayloadBuffer(deque):
    maxlen = 2500

    def __init__(self, length: int = 200):
        super().__init__([0] * length)


class Recorder:
    data: defaultdict[int, _PayloadBuffer] = defaultdict(_PayloadBuffer)

    def __init__(self, bus: bus.BusABC):
        notifier.Notifier(bus, [_Listener(self.data)])
