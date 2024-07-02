from typing import Callable, Dict, Iterable

from can_explorer.can_bus import PayloadBuffer
from can_explorer.config import Default
from can_explorer.plotting import AxisData, Row


class PlotModel:
    _height = Default.PLOT_HEIGHT
    _x_limit = Default.BUFFER_SIZE
    _id_format: Callable = Default.ID_FORMAT

    def __init__(self) -> None:
        self.row: Dict[int, Row] = {}
        self.payload: Dict[int, PayloadBuffer] = {}

    def __call__(self) -> dict[int, Row]:
        """
        Get all of the currently active plots.

        Returns:
            dict[int, Row]: Plots
        """
        return self.row

    def _slice(self, payloads: PayloadBuffer) -> Iterable:
        """
        Reduce the number of payloads by returning the N newest amount.

        Note: N == current PlotManager limit value

        Args:
            payloads (PayloadBuffer)

        Returns:
            Iterable: Reduced payloads
        """
        return payloads[len(payloads) - self._x_limit :]

    def add(self, can_id: int, payloads: PayloadBuffer) -> None:
        """
        Create a new plot.

        Args:
            can_id (int)
            payloads (PayloadBuffer)

        Raises:
            Exception: If plot already exists
        """
        if can_id in self.row:
            raise Exception(f"Error: id {can_id} already exists")

        row = Row(
            can_id, self._id_format, self._height, **AxisData(self._slice(payloads))
        )

        self.payload[can_id] = payloads
        self.row[can_id] = row

    def delete(self, can_id: int) -> None:
        """
        Remove a plot.

        Args:
            can_id (int)
        """
        self.payload[can_id].pop()
        self.row[can_id].delete()
        self.row.pop(can_id)

    def update(self, can_id: int) -> None:
        """
        Update a plot.

        Args:
            can_id (int)
            payloads (PayloadBuffer)
        """
        row = self.row[can_id]

        row.plot.update(**AxisData(self._slice(self.payload[can_id])))

    def clear_all(self) -> None:
        """
        Remove all plots.
        """
        while self.row:
            self.delete(list(self.row).pop())

    def set_height(self, height: int) -> None:
        """
        Set height to use for plots.

        Args:
            height (int): Height in pixels
        """
        self._height = height

        for row in self.row.values():
            row.set_height(self._height)

    def set_id_format(self, id_format: Callable) -> None:
        """
        Set the format CAN id's will be displayed as.

        Args:
            id_format (Callable)
        """
        self._id_format = id_format

        for row in self.row.values():
            row.set_label(self._id_format)

    def set_limit(self, x_limit: int) -> None:
        """
        Set the number of payloads to plot on the x axis.

        Args:
            x_limit (int): Number of payloads
        """
        self._x_limit = x_limit

        for can_id in self.row:
            self.update(can_id)
