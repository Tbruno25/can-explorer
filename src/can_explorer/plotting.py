from __future__ import annotations

from typing import Callable, Iterable

import dearpygui.dearpygui as dpg

from can_explorer.config import Font
from can_explorer.resources import generate_tag
from can_explorer.view import PlotTable


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
