import math
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator, Iterable

import dearpygui.dearpygui as dpg

from can_explorer.layout import DEFAULT_PLOT_HEIGHT, PlotTable, Tag

# creating data
sindatax = []
sindatay = []
for i in range(0, 500):
    sindatax.append(i / 1000)
    sindatay.append(0.5 + 0.5 * math.sin(50 * i / 1000))


class Config:
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


class PlotLabel(int):
    ...


class PlotData(str):
    ...


@dataclass
class RowItem:
    table: PlotTable
    label: PlotLabel | None = None
    plot: PlotData | None = None


class PlotManager:
    height = DEFAULT_PLOT_HEIGHT
    plots: dict[str, RowItem] = {}

    def _make_label(self, id: int | str) -> int:
        return dpg.add_button(
            tag=f"{Tag.PLOT_LABEL}{dpg.generate_uuid()}",
            label=id,
            height=self.height,
            enabled=False,
        )

    def _make_plot(self, payloads: Iterable) -> PlotData:
        with dpg.plot(
            tag=f"{Tag.PLOT_DATA}{dpg.generate_uuid()}",
            height=self.height,
            **Config.PLOT,
        ) as plot:
            dpg.add_plot_axis(**Config.X_AXIS)
            with dpg.plot_axis(
                **Config.Y_AXIS,
            ):
                # series belong to a y axis
                dpg.add_line_series(sindatax, sindatay)

        return PlotData(plot)

    @staticmethod
    @contextmanager
    def _make_row() -> Generator:
        row = RowItem(PlotTable())
        try:
            yield row
        finally:
            row.table.add_widget(row.label)
            row.table.add_widget(row.plot)
            row.table.submit()

    def add_plot(self, id: int | str, payload: Iterable) -> None:
        with self._make_row() as row_item:
            row_item.label = self._make_label(id)
            row_item.plot = self._make_plot(payload)
        self.plots[id] = row_item
