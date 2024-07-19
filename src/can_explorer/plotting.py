from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import Any

import dearpygui.dearpygui as dpg

from can_explorer.configs import Default
from can_explorer.tags import generate_tag


def convert_payloads(payloads: Collection) -> PlotData:
    return PlotData(
        x=tuple(range(len(payloads))),
        y=tuple(payloads),
    )


@dataclass
class PlotData:
    x: Collection
    y: Collection


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

    def __new__(cls) -> PlotItem:
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
            plot.series = dpg.add_line_series(parent=plot.y_axis, x=[], y=[])

        return plot


class _PercentageWidthTableRow:
    # https://github.com/hoffstadt/DearPyGui/discussions/1306

    def __init__(self, parent: int, **kwargs) -> None:
        self.table_id = dpg.add_table(
            parent=parent,
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


class PlotRow:
    def __init__(self, parent: int) -> None:
        row = _PercentageWidthTableRow(parent)  # Must create first
        self.id = row.table_id
        self.label = LabelItem()
        self.plot = PlotItem()
        row.add_widget(self.label, Default.LABEL_COLUMN_WIDTH)
        row.add_widget(self.plot, Default.PLOT_COLUMN_WIDTH)
        row.submit()

    def delete(self) -> None:
        dpg.delete_item(self.id)

    def hide(self) -> None:
        dpg.hide_item(self.id)

    def show(self) -> None:
        dpg.show_item(self.id)

    def update(
        self,
        label: str | None = None,
        data: PlotData | None = None,
        height: int | None = None,
    ) -> None:
        if label is not None:
            dpg.set_item_label(self.label, label)

        if data is not None:
            dpg.set_axis_limits(self.plot.x_axis, min(data.x), max(data.x))
            dpg.set_axis_limits(self.plot.y_axis, min(data.y), max(data.y))
            dpg.configure_item(self.plot.series, x=data.x, y=data.y)

        if height is not None:
            dpg.set_item_height(self.label, height)
            dpg.set_item_height(self.plot, height)
