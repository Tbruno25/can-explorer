from typing import Dict, Iterable

import dearpygui.dearpygui as dpg

from can_explorer.layout import DEFAULT_PLOT_HEIGHT, PlotTable, Tag


class Config:
    LABEL = dict(enabled=False, height=DEFAULT_PLOT_HEIGHT)

    PLOT = dict(
        no_title=True,
        no_menus=True,
        no_child=True,
        no_mouse_pos=True,
        no_highlight=True,
        no_box_select=True,
        height=DEFAULT_PLOT_HEIGHT,
    )

    X_AXIS = dict(
        axis=dpg.mvXAxis
    )  # , lock_min=True, lock_max=True, no_tick_labels=True)

    Y_AXIS = dict(
        axis=dpg.mvYAxis
    )  # , lock_min=True, lock_max=True, no_tick_labels=True)


def _parse_payloads(payloads: Iterable) -> dict:
    return dict(x=tuple(range(len(payloads))), y=tuple(payloads))


class Plot(str):
    x_axis: str
    y_axis: str

    def __new__(cls, x: Iterable, y: Iterable) -> None:
        with dpg.plot(
            tag=f"{Tag.PLOT_ITEM}{dpg.generate_uuid()}", **Config.PLOT
        ) as plot:
            plot = super().__new__(cls, plot)
            plot.x_axis = dpg.add_plot_axis(**Config.X_AXIS)
            plot.y_axis = dpg.add_plot_axis(**Config.Y_AXIS)
            dpg.add_line_series(parent=plot.y_axis, x=x, y=y)

        return plot

    def update(self, x: Iterable, y: Iterable) -> None:
        dpg.configure_item(self.y_axis, x=x, y=y)
        dpg.fit_axis_data(self.y_axis)


class Label(str):
    def __new__(cls, can_id: int) -> None:
        label = dpg.add_button(
            tag=f"{Tag.PLOT_LABEL}{dpg.generate_uuid()}",
            label=hex(can_id),
            **Config.LABEL,
        )
        return super().__new__(cls, label)


class Row:
    table: PlotTable
    label: Label
    plot: Plot

    def __init__(self, can_id: int, payloads: Iterable) -> None:
        self._table = PlotTable()
        self.label = Label(can_id)
        self.plot = Plot(**_parse_payloads(payloads))

        self._table.add_widget(self.label)
        self._table.add_widget(self.plot)
        self._table.submit()

    def set_height(self, height: int) -> None:
        dpg.set_item_height(self.label, height)
        dpg.set_item_height(self.plot, height)

    def delete(self) -> None:
        dpg.delete_item(self.table.table_id)


class PlotManager:
    height = DEFAULT_PLOT_HEIGHT
    plots: Dict[int, Row] = {}

    @staticmethod
    def _handle_payloads(payloads: Iterable) -> dict:
        return dict(x=tuple(range(len(payloads))), y=tuple(payloads))

    def add_plot(self, can_id: int, payloads: Iterable) -> None:
        row = Row(can_id, payloads)
        self.plots[can_id] = row

    def remove_plot(self, can_id: int) -> None:
        self.plots.pop(can_id)

    def clear_all(self) -> None:
        while self.plots:
            self.remove_plot(list(self.plots).pop())
