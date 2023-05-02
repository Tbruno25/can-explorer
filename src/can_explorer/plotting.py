from __future__ import annotations

from typing import Callable, Dict, Iterable

import dearpygui.dearpygui as dpg

from can_explorer.can_bus import PayloadBuffer
from can_explorer.layout import Default, Font, PlotTable
from can_explorer.resources import generate_tag


class Config:
    LABEL = dict(enabled=False)

    PLOT = dict(
        no_title=True,
        no_menus=True,
        no_child=True,
        no_mouse_pos=True,
        no_highlight=True,
        no_box_select=True,
    )

    X_AXIS = dict(axis=dpg.mvXAxis, lock_min=True, lock_max=True, no_tick_labels=True)

    Y_AXIS = dict(axis=dpg.mvYAxis, lock_min=True, lock_max=True, no_tick_labels=True)


class Plot(str):
    x_axis: str
    y_axis: str
    series: str

    def __new__(cls, x: Iterable, y: Iterable) -> Plot:
        with dpg.plot(tag=str(generate_tag()), **Config.PLOT) as plot:
            plot = super().__new__(cls, plot)
            plot.x_axis = dpg.add_plot_axis(**Config.X_AXIS)
            plot.y_axis = dpg.add_plot_axis(**Config.Y_AXIS)
            plot.series = dpg.add_line_series(parent=plot.y_axis, x=x, y=y)

        return plot

    def update(self, x: Iterable, y: Iterable) -> None:
        dpg.set_axis_limits(self.x_axis, min(x), max(x))
        dpg.set_axis_limits(self.y_axis, min(y), max(y))
        dpg.configure_item(self.series, x=x, y=y)


class Label(str):
    def __new__(cls) -> Label:
        label = dpg.add_button(
            tag=str(generate_tag()),
            **Config.LABEL,
        )
        dpg.bind_item_font(label, Font.LABEL)

        return super().__new__(cls, label)


class Row:
    table: PlotTable
    label: Label
    plot: Plot
    height: int
    label_format: Callable

    def __init__(
        self, can_id: int, id_format: Callable, height: int, x: Iterable, y: Iterable
    ) -> None:
        self._can_id = can_id
        self.table = PlotTable()
        self.label = Label()
        self.plot = Plot(x, y)
        self.table.add_label(self.label)
        self.table.add_plot(self.plot)
        self.table.submit()
        self.set_label(id_format)
        self.set_height(height)

    def set_height(self, height: int) -> None:
        dpg.set_item_height(self.label, height)
        dpg.set_item_height(self.plot, height)
        self.height = height

    def set_label(self, id_format: Callable) -> None:
        dpg.set_item_label(self.label, id_format(self._can_id))
        self.label_format = id_format

    def delete(self) -> None:
        dpg.delete_item(self.table.table_id)


class AxisData(dict):
    x: tuple
    y: tuple

    def __init__(self, payloads: Iterable):
        x = tuple(range(len(payloads)))  # type: ignore [arg-type]
        y = tuple(payloads)
        super().__init__(dict(x=x, y=y))


class PlotManager:
    row: Dict[int, Row] = {}
    payload: Dict[int, PayloadBuffer] = {}
    _height = Default.PLOT_HEIGHT
    _x_limit = Default.BUFFER_SIZE
    _id_format: Callable = Default.ID_FORMAT

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
