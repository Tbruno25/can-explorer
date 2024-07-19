from collections import defaultdict, deque
from typing import DefaultDict

import can

from can_explorer.configs import Default
from can_explorer.plotting import PlotData, convert_payloads


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


class PlotModel:
    def __init__(self) -> None:
        self._data: DefaultDict[int, PayloadBuffer] = defaultdict(PayloadBuffer)
        self._len = Default.BUFFER_SIZE

    def add_message(self, message: can.Message) -> None:
        can_id = message.arbitration_id
        val = int.from_bytes(message.data, byteorder="big")
        self._data[can_id].append(val)

    def get_data(self, can_id: int) -> PlotData:
        return convert_payloads(self._data[can_id][-self._len :])

    def set_limit(self, limit: int) -> None:
        """
        Set the number of values to plot on the x axis.

        Args:
            limit (int): N values
        """
        self._len = limit
