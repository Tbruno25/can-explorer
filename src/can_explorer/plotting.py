from __future__ import annotations

from typing import Dict, Iterable

import dearpygui.dearpygui as dpg

from can_explorer.can_bus import PayloadBuffer
from can_explorer.layout import Default, Font, PlotTable, Tag


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
        with dpg.plot(
            tag=f"{Tag.PLOT_ITEM}{dpg.generate_uuid()}", **Config.PLOT
        ) as plot:
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
    def __new__(cls, can_id: int) -> Label:
        label = dpg.add_button(
            tag=f"{Tag.PLOT_LABEL}{dpg.generate_uuid()}",
            label=hex(can_id),
            **Config.LABEL,
        )
        dpg.bind_item_font(label, Font.LABEL)

        return super().__new__(cls, label)


class Row:
    table: PlotTable
    label: Label
    plot: Plot
    height: int

    def __init__(self, can_id: int, height: int, x: Iterable, y: Iterable) -> None:
        self.table = PlotTable()
        self.label = Label(can_id)
        self.plot = Plot(x, y)
        self.table.add_label(self.label)
        self.table.add_plot(self.plot)
        self.table.submit()
        self.set_height(height)

    def set_height(self, height: int) -> None:
        dpg.set_item_height(self.label, height)
        dpg.set_item_height(self.plot, height)
        self.height = height

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
    _height = Default.PLOT_HEIGHT
    _x_limit = Default.BUFFER_SIZE

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

        row = Row(can_id, self._height, **AxisData(self._slice(payloads)))
        self.row[can_id] = row

    def delete(self, can_id: int) -> None:
        """
        Remove a plot.

        Args:
            can_id (int)
        """
        self.row[can_id].delete()
        self.row.pop(can_id)

    def update(self, can_id: int, payloads: PayloadBuffer) -> None:
        """
        Update a plot.

        Note: Current PlotManager height and limit values are automatically applied.

        Args:
            can_id (int)
            payloads (PayloadBuffer)
        """
        row = self.row[can_id]

        if row.height != self._height:
            row.set_height(self._height)

        row.plot.update(**AxisData(self._slice(payloads)))

    def clear_all(self) -> None:
        """
        Remove all plots.
        """
        while self.row:
            self.delete(list(self.row).pop())

    def set_height(self, height: int) -> None:
        """
        Set height to use for plots.

        Note: Won't affect existing plots until update() is called

        Args:
            height (int): Height in pixels
        """
        self._height = height

    def set_limit(self, x_limit: int) -> None:
        """
        Set the number of payloads to plot on the x axis.

        Note: Won't affect existing plots until update() is called

        Args:
            x_limit (int): Number of payloads
        """
        self._x_limit = x_limit
