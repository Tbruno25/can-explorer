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

    X_AXIS = dict(axis=dpg.mvXAxis, lock_min=True, lock_max=True, no_tick_labels=True)

    Y_AXIS = dict(axis=dpg.mvYAxis, lock_min=True, lock_max=True, no_tick_labels=True)


class AxisData(dict):
    x: tuple
    y: tuple

    def __init__(self, payloads: Iterable):
        x = tuple(range(len(payloads)))
        y = tuple(payloads)
        super().__init__(dict(x=x, y=y))


class Plot(str):
    x_axis: str
    y_axis: str
    series: str

    def __new__(cls, payloads: Iterable) -> None:
        with dpg.plot(
            tag=f"{Tag.PLOT_ITEM}{dpg.generate_uuid()}", **Config.PLOT
        ) as plot:
            plot = super().__new__(cls, plot)
            plot.x_axis = dpg.add_plot_axis(**Config.X_AXIS)
            plot.y_axis = dpg.add_plot_axis(**Config.Y_AXIS)
            plot.series = dpg.add_line_series(parent=plot.y_axis, **AxisData(payloads))

        return plot

    def update(self, payloads: Iterable) -> None:
        axis_data = AxisData(payloads)
        dpg.set_axis_limits(self.x_axis, min(axis_data["x"]), max(axis_data["x"]))
        dpg.set_axis_limits(self.y_axis, min(axis_data["y"]), max(axis_data["y"]))
        dpg.configure_item(self.series, **axis_data)


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
        self.table = PlotTable()
        self.label = Label(can_id)
        self.plot = Plot(payloads)
        self.table.add_widget(self.label)
        self.table.add_widget(self.plot)
        self.table.submit()

    def set_height(self, height: int) -> None:
        dpg.set_item_height(self.label, height)
        dpg.set_item_height(self.plot, height)

    def delete(self) -> None:
        dpg.delete_item(self.table.table_id)


class PlotManager:
    row: Dict[int, Row] = {}

    def __call__(self) -> dict:
        return self.row

    def add(self, can_id: int, payloads: Iterable) -> None:
        if can_id in self.row:
            raise Exception(f"Error: id {can_id} already exists")

        row = Row(can_id, payloads)
        self.row[can_id] = row

    def delete(self, can_id: int) -> None:
        self.row[can_id].delete()
        self.row.pop(can_id)

    def update(self, can_id: int, payloads: Iterable) -> None:
        return self.row[can_id].plot.update(payloads)

    def clear_all(self) -> None:
        while self.row:
            self.delete(list(self.row).pop())

    def set_height(self, height: int) -> None:
        for row in self.row.values():
            row.set_height(height)
