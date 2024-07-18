from __future__ import annotations

from collections.abc import Callable, Collection
from dataclasses import dataclass
from typing import cast

import dearpygui.dearpygui as dpg
from dearpygui_ext.themes import create_theme_imgui_light
from wrapt import synchronized

from can_explorer.configs import Default
from can_explorer.plotting import PlotData, PlotRow
from can_explorer.resources import Percentage
from can_explorer.tags import Tag

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
        self._row: dict[int, PlotRow] = {}

    @property
    def tag(self) -> Tag:
        return self._parent.tag

    def setup(self) -> None:
        pass

    @synchronized
    def _add_row(self, can_id: int) -> None:
        row = PlotRow(self.tag.plot_tab)
        dpg.bind_item_font(row.label, self._parent.font.large)
        self._row[can_id] = row

    def get_rows(self) -> dict:
        return self._row.copy()

    @synchronized
    def update(self, can_id: int, plot_data: PlotData) -> None:
        if can_id not in self._row:
            self._add_row(can_id)
        self._row[can_id].update(
            label=self._format(can_id), data=plot_data, height=self._height
        )

    @synchronized
    def remove(self, can_id: int) -> None:
        row = self._row.pop(can_id)
        row.delete()

    @synchronized
    def clear(self) -> None:
        for can_id in self.get_rows():
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

    def setup(self) -> None:
        with dpg.collapsing_header(label="CAN Bus", default_open=True):
            dpg.add_combo(tag=self.tag.settings_interface, label="Interface")
            dpg.add_input_text(tag=self.tag.settings_channel, label="Channel")
            dpg.add_combo(tag=self.tag.settings_baudrate, label="Baudrate")
            dpg.add_spacer(height=5)
            dpg.add_button(tag=self.tag.settings_apply, label="Apply", height=30)
            dpg.add_spacer(height=5)

        with dpg.collapsing_header(label="GUI"):
            with dpg.group(horizontal=True):
                dpg.add_text("ID Format")
                dpg.add_radio_button(
                    ["Hex", "Dec"],
                    tag=self.tag.settings_id_format,
                    horizontal=True,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Theme")
                dpg.add_radio_button(
                    ["Default", "Light"],
                    horizontal=True,
                    callback=lambda sender: dpg.bind_theme(
                        getattr(self._parent.theme, dpg.get_value(sender).lower())
                    ),
                )

            dpg.add_button(
                label="Launch Font Manager", width=-1, callback=dpg.show_font_manager
            )
            dpg.add_button(
                label="Launch Style Editor", width=-1, callback=dpg.show_style_editor
            )
            dpg.add_spacer(height=5)

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


@dataclass
class Font:
    default: int
    large: int


@dataclass
class Theme:
    default: int
    light: int


class MainView:
    font: Font
    theme: Theme

    def __init__(self, tags: Tag | None = None) -> None:
        self.tag = tags or Tag()
        self.plot = PlotView(self)
        self.settings = SettingsView(self)

    def setup(self) -> None:
        self._fonts()
        self._themes()
        self._header()
        self._body()
        self._footer()

    def _fonts(self):
        with dpg.font_registry():
            self.font = Font(
                default=dpg.add_font(Default.FONT, Default.FONT_HEIGHT),
                large=dpg.add_font(Default.FONT, Default.FONT_HEIGHT * 1.75),
            )

        dpg.bind_font(self.font.default)

    def _themes(self):
        with dpg.theme() as default:
            with dpg.theme_component(dpg.mvButton, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, Default.BACKGROUND)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, Default.BACKGROUND)

            self.theme = Theme(default=default, light=create_theme_imgui_light())

        dpg.bind_theme(self.theme.default)

    def _header(self) -> None:
        def tab_callback(sender, app_data, user_data) -> None:
            current_tab = dpg.get_item_label(app_data)

            if current_tab == "Viewer":
                dpg.configure_item(self.tag.plot_tab, show=True)
                dpg.configure_item(self.tag.settings_tab, show=False)
            else:
                dpg.configure_item(self.tag.plot_tab, show=False)
                dpg.configure_item(self.tag.settings_tab, show=True)

        with dpg.tab_bar(tag=self.tag.header, callback=tab_callback):
            dpg.add_tab(label="Viewer")
            dpg.add_tab(label="Settings")

    def _body(self) -> None:
        with dpg.child_window(tag=self.tag.body, border=False):
            with dpg.group(tag=self.tag.plot_tab, show=True):
                self.plot.setup()
            with dpg.group(tag=self.tag.settings_tab, show=False):
                self.settings.setup()

    def _footer(self) -> None:
        with dpg.child_window(
            tag=self.tag.footer, height=110, border=False, no_scrollbar=True
        ):
            dpg.add_spacer(height=2)
            dpg.add_separator()
            dpg.add_spacer(height=2)

            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()
                with dpg.table_row():
                    with dpg.group(horizontal=True):
                        dpg.add_text("Message Buffer Size")
                        dpg.add_spacer()
                        dpg.add_slider_int(
                            tag=self.tag.plot_buffer_slider,
                            width=-1,
                            default_value=Percentage.get(
                                Default.BUFFER_SIZE, Default.BUFFER_MAX
                            ),
                            min_value=2,
                            max_value=100,
                            clamped=True,
                            format="%d%%",
                        )

                    with dpg.group(horizontal=True):
                        dpg.add_text("Plot Height")
                        dpg.add_spacer()
                        dpg.add_slider_int(
                            tag=self.tag.plot_height_slider,
                            width=-1,
                            default_value=Percentage.get(
                                Default.PLOT_HEIGHT, Default.PLOT_HEIGHT_MAX
                            ),
                            min_value=10,
                            max_value=100,
                            clamped=True,
                            format="%d%%",
                        )
            dpg.add_spacer(height=2)

            dpg.add_separator()
            dpg.add_spacer(height=2)
            with dpg.group(horizontal=True):
                dpg.add_button(
                    tag=self.tag.main_button,
                    width=-100,
                    height=50,
                )
                dpg.add_button(
                    tag=self.tag.clear_button,
                    label="Clear",
                    width=-1,
                    height=50,
                )

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
