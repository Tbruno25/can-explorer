from typing import Iterable

from can_explorer.can_bus import PayloadBuffer
from can_explorer.configs import Default


def convert_payloads(payloads: Iterable) -> dict:
    return dict(
        x=tuple(range(len(payloads))),  # type: ignore [arg-type]
        y=tuple(payloads),
    )


class PlotModel:
    _len = Default.BUFFER_SIZE

    def __init__(self) -> None:
        self._plot: dict[int, Iterable] = {}

    def update_plot(self, can_id: int, payloads: PayloadBuffer) -> None:
        """
        Update a plot.

        Args:
            can_id (int)
            payloads (PayloadBuffer)
        """
        plot_data = convert_payloads(payloads[-self._len :])
        self._plot[can_id] = plot_data

    def get_plot_data(self, can_id: int) -> dict:
        return self._plot[can_id]  # type: ignore

    def get_plots(self) -> dict:
        """
        Get all plots.
        """
        return self._plot.copy()

    def clear(self) -> None:
        """
        Remove all plots.
        """
        self._plot.clear()

    def set_limit(self, limit: int) -> None:
        """
        Set the number of values to plot on the x axis.

        Args:
            limit (int): N values
        """
        self._len = limit
