from __future__ import annotations

from collections.abc import Callable, Collection
from typing import cast

import dearpygui.dearpygui as dpg
from wrapt import synchronized

from can_explorer.configs import Default
from can_explorer.plotting import PlotData, PlotRow
from can_explorer.resources import Percentage
from can_explorer.tags import Tag
from can_explorer.ui_builder import UIBuilder

# Some dpg functionality is not thread safe
#   ie: adding and removing widgets
# The synchronized decorator is used to provide
# the instance with a lock for thread safety
# https://github.com/GrahamDumpleton/wrapt/blob/develop/blog/07-the-missing-synchronized-decorator.md


class PlotView:
    _format: Callable = Default.ID_FORMAT
    _height: int = Default.PLOT_HEIGHT

    def __init__(self, parent: MainView) -> None:
        self._parent = parent
        self._row_keys: list[int] = []
        self._row_values: list[PlotRow] = []
        self._row_dict: dict[int, PlotRow] = {}

    @property
    def tag(self) -> Tag:
        return self._parent.tag

    def _add_row(self) -> None:
        row = PlotRow(self.tag.plot_tab)
        dpg.bind_item_font(row.label, self._parent.font.large)  # type: ignore
        self._row_values.append(row)

    def _sync_rows(self) -> None:
        """
        Pair the current row_keys with the row_values.
        Automatically hide's any rows not being used.
        """
        while len(self._row_keys) > len(self._row_values):
            self._add_row()

        sorted_rows = dict(zip(sorted(self._row_keys), self._row_values))

        for row in self._row_values:
            if row in sorted_rows.values():
                row.show()
            else:
                row.hide()

        self._row_dict = sorted_rows

    def get_rows(self) -> dict:
        return self._row_dict.copy()

    @synchronized
    def update(self, can_id: int, plot_data: PlotData) -> None:
        if can_id not in self._row_keys:
            self._row_keys.append(can_id)
            self._sync_rows()
        self._row_dict[can_id].update(
            label=self._format(can_id), data=plot_data, height=self._height
        )

    @synchronized
    def remove(self, can_id: int) -> None:
        self._row_keys.remove(can_id)
        self._row_dict[can_id].hide()

    @synchronized
    def clear(self) -> None:
        for can_id in self._row_keys:
            self.remove(can_id)

    @synchronized
    def set_format(self, id_format: Callable) -> None:
        """
        Set the format CAN id's will be displayed as.

        Args:
            id_format (Callable)
        """
        for can_id, row in self.get_rows().items():
            row.update(label=id_format(can_id))

        self._format = id_format

    @synchronized
    def set_height(self, height: int) -> None:
        """
        Set the height of all plots.

        Args:
            height (int)
        """
        for row in self.get_rows().values():
            row.update(height=height)

        self._height = height


class SettingsView:
    def __init__(self, parent: MainView) -> None:
        self._parent = parent

    @property
    def tag(self) -> Tag:
        return self._parent.tag

    def get_interface(self) -> str:
        return dpg.get_value(self.tag.settings_interface)

    def get_channel(self) -> str:
        return dpg.get_value(self.tag.settings_channel)

    def get_baudrate(self) -> int:
        return dpg.get_value(self.tag.settings_baudrate)

    def get_id_format(self) -> Callable:
        return cast(
            Callable,
            hex if dpg.get_value(self.tag.settings_id_format).lower() == "hex" else int,
        )

    def set_apply_button_callback(self, callback: Callable) -> None:
        dpg.configure_item(self.tag.settings_apply, callback=callback)

    def set_can_id_format_callback(self, callback: Callable) -> None:
        dpg.configure_item(self.tag.settings_id_format, callback=callback)

    def set_interface_options(
        self, iterable: Collection[str], default: str = ""
    ) -> None:
        dpg.configure_item(
            self.tag.settings_interface, items=iterable, default_value=default
        )

    def set_channel(self, channel: str = "") -> None:
        dpg.configure_item(self.tag.settings_channel, default_value=channel)

    def set_baudrate_options(
        self, iterable: Collection[str], default: str = ""
    ) -> None:
        dpg.configure_item(
            self.tag.settings_baudrate, items=iterable, default_value=default
        )


class MainView:
    def __init__(self, tags: Tag | None = None) -> None:
        self.tag = tags or Tag()
        self.ui = UIBuilder(self)
        self.plot = PlotView(self)
        self.settings = SettingsView(self)
        self.font = None
        self.theme = None

    def resize(self) -> None:
        dpg.set_item_height(
            self.tag.body,
            (
                dpg.get_viewport_height()
                - dpg.get_item_height(self.tag.footer)
                - Default.FOOTER_OFFSET
            ),
        )
        dpg.set_item_width(self.tag.settings_apply, dpg.get_viewport_width() // 4)

    @staticmethod
    def popup_error(name: str | Exception, info: str | Exception) -> None:
        # https://github.com/hoffstadt/DearPyGui/discussions/1308

        # guarantee these commands happen in the same frame
        with dpg.mutex():
            viewport_width = dpg.get_viewport_client_width()
            viewport_height = dpg.get_viewport_client_height()

            with dpg.window(label="ERROR", modal=True, no_close=True) as modal_id:
                dpg.add_text(name, color=(255, 0, 0))  # red
                dpg.add_separator()
                dpg.add_text(info)
                with dpg.group():
                    dpg.add_button(
                        label="Close",
                        width=-1,
                        user_data=(modal_id, True),
                        callback=lambda sender, app_data, user_data: dpg.delete_item(
                            user_data[0]
                        ),
                    )

        # guarantee these commands happen in another frame
        dpg.split_frame()
        width = dpg.get_item_width(modal_id)
        height = dpg.get_item_height(modal_id)
        dpg.set_item_pos(
            modal_id,
            [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2],
        )

    def get_plot_buffer(self) -> int:
        percentage = dpg.get_value(self.tag.plot_buffer_slider)
        return Percentage.reverse(percentage, Default.BUFFER_MAX)

    def get_plot_height(self) -> int:
        percentage = dpg.get_value(self.tag.plot_height_slider)
        return Percentage.reverse(percentage, Default.PLOT_HEIGHT_MAX)

    def set_main_button_label(self, state: bool) -> None:
        dpg.set_item_label(self.tag.main_button, ("Stop", "Start")[not state])

    def set_main_button_callback(self, callback: Callable) -> None:
        dpg.configure_item(self.tag.main_button, callback=callback)

    def set_clear_button_callback(self, callback: Callable) -> None:
        dpg.configure_item(self.tag.clear_button, callback=callback)

    def set_plot_buffer_slider_callback(self, callback: Callable) -> None:
        dpg.configure_item(self.tag.plot_buffer_slider, callback=callback)

    def set_plot_height_slider_callback(self, callback: Callable) -> None:
        dpg.configure_item(self.tag.plot_height_slider, callback=callback)
