from typing import Dict, Iterable, Optional

import dearpygui.dearpygui as dpg

from can_explorer.layout import DEFAULT_PLOT_HEIGHT, PlotTable, Tag


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

    def __new__(cls, x: Iterable, y: Iterable) -> None:
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

    def __init__(self, can_id: int, x: Iterable, y: Iterable) -> None:
        self.table = PlotTable()
        self.label = Label(can_id)
        self.plot = Plot(x, y)
        self.table.add_widget(self.label)
        self.table.add_widget(self.plot)
        self.table.submit()

    def set_height(self, height: int) -> None:
        dpg.set_item_height(self.label, height)
        dpg.set_item_height(self.plot, height)

    def delete(self) -> None:
        dpg.delete_item(self.table.table_id)


class AxisData(dict):
    x: tuple
    y: tuple

    def __init__(self, payloads: Iterable):
        x = tuple(range(len(payloads)))
        y = tuple(payloads)
        super().__init__(dict(x=x, y=y))


class PlotManager:
    row: Dict[int, Row] = {}
    _x_limit = 250
    _height = DEFAULT_PLOT_HEIGHT

    def __call__(self) -> dict:
        return self.row

    def add(self, can_id: int, payloads: Iterable) -> None:
        if can_id in self.row:
            raise Exception(f"Error: id {can_id} already exists")

        row = Row(can_id, **AxisData(payloads))
        row.set_height(self._height)
        self.row[can_id] = row

    def delete(self, can_id: int) -> None:
        self.row[can_id].delete()
        self.row.pop(can_id)

    def update(self, can_id: int, payloads: Optional[Iterable]) -> None:
        return self.row[can_id].plot.update(payloads)

    def clear_all(self) -> None:
        while self.row:
            self.delete(list(self.row).pop())

    def set_height(self, height: int) -> None:
        self._height = height

        for row in self.row.values():
            row.set_height(self._height)
