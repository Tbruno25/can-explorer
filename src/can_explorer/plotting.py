from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import dearpygui.dearpygui as dpg

from can_explorer.configs import Default
from can_explorer.tags import generate_tag


class LabelItem(str):
    def __new__(cls) -> LabelItem:
        label = dpg.add_button(
            tag=str(generate_tag()),
            enabled=False,
        )

        return super().__new__(cls, label)


class PlotItem(str):
    x_axis: str
    y_axis: str
    series: str

    def __new__(cls, x: Iterable, y: Iterable) -> PlotItem:
        with dpg.plot(
            tag=str(generate_tag()),
            no_title=True,
            no_menus=True,
            no_child=True,
            no_mouse_pos=True,
            no_highlight=True,
            no_box_select=True,
        ) as plot:
            plot = super().__new__(cls, plot)
            plot.x_axis = dpg.add_plot_axis(
                axis=dpg.mvXAxis, lock_min=True, lock_max=True, no_tick_labels=True
            )
            plot.y_axis = dpg.add_plot_axis(
                axis=dpg.mvYAxis, lock_min=True, lock_max=True, no_tick_labels=True
            )
            plot.series = dpg.add_line_series(parent=plot.y_axis, x=x, y=y)

        return plot

    def update(self, x: Iterable, y: Iterable) -> None:
        dpg.set_axis_limits(self.x_axis, min(x), max(x))
        dpg.set_axis_limits(self.y_axis, min(y), max(y))
        dpg.configure_item(self.series, x=x, y=y)


class PercentageWidthTableRow:
    # https://github.com/hoffstadt/DearPyGui/discussions/1306

    def __init__(self, **kwargs) -> None:
        self.table_id = dpg.add_table(
            header_row=False,
            policy=dpg.mvTable_SizingStretchProp,
            **kwargs,
        )
        self.stage_id = dpg.add_stage()
        dpg.push_container_stack(self.stage_id)

    def add_widget(self, uuid: Any, percentage: float) -> None:
        dpg.add_table_column(
            init_width_or_weight=percentage / 100.0, parent=self.table_id
        )
        dpg.set_item_width(uuid, -1)

    def submit(self) -> None:
        dpg.pop_container_stack()
        with dpg.table_row(parent=self.table_id):
            dpg.unstage(self.stage_id)

    def delete(self) -> None:
        dpg.delete_item(self.table_id)
        # dpg.delete_item(self.stage_id)


class PlotRow(PercentageWidthTableRow):
    label: LabelItem
    plot: PlotItem

    def __init__(
        self,
        parent: int,
        can_id: int,
        x: Iterable,
        y: Iterable,
    ) -> None:
        super().__init__(parent=parent)
        self.can_id = can_id
        self.label = LabelItem()
        self.plot = PlotItem(x, y)
        self.add_widget(self.label, Default.LABEL_COLUMN_WIDTH)
        self.add_widget(self.plot, Default.PLOT_COLUMN_WIDTH)
        self.submit()


class PlotData:
    x: Iterable
    y: Iterable


class PayloadAxisData(dict):
    x: tuple
    y: tuple

    def __init__(self, payloads: Iterable):
        x = tuple(range(len(payloads)))  # type: ignore [arg-type]
        y = tuple(payloads)
        super().__init__(dict(x=x, y=y))
