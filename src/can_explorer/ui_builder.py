from dataclasses import dataclass

import dearpygui.dearpygui as dpg
from dearpygui_ext.themes import create_theme_imgui_light

from can_explorer.configs import Default
from can_explorer.resources import Percentage
from can_explorer.tags import Tag


@dataclass
class Font:
    default: int
    large: int


@dataclass
class Theme:
    default: int
    light: int


class UIBuilder:
    def __init__(self, parent):
        self._parent = parent

    @property
    def tag(self) -> Tag:
        return self._parent.tag

    def build(self) -> int | str:
        with dpg.window() as window:
            self.add_fonts()
            self.add_themes()
            self.create_header()
            self.create_body()
            self.create_footer()

        return window

    def create_header(self):
        with dpg.tab_bar(tag=self.tag.header, callback=self.tab_callback):
            dpg.add_tab(label="Viewer")
            dpg.add_tab(label="Settings")

    def create_body(self):
        with dpg.child_window(tag=self.tag.body, border=False):
            with dpg.group(tag=self.tag.plot_tab, show=True):
                pass  # Plot setup will be added here
            with dpg.group(tag=self.tag.settings_tab, show=False):
                self.add_settings()

    def create_footer(self):
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

    def add_fonts(self):
        with dpg.font_registry():
            self._parent.font = Font(
                default=dpg.add_font(Default.FONT, Default.FONT_HEIGHT),
                large=dpg.add_font(Default.FONT, Default.FONT_HEIGHT * 1.75),
            )

        dpg.bind_font(self._parent.font.default)

    def add_themes(self):
        with dpg.theme() as default:
            with dpg.theme_component(dpg.mvButton, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, Default.BACKGROUND)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, Default.BACKGROUND)

            self._parent.theme = Theme(
                default=default, light=create_theme_imgui_light()
            )

        dpg.bind_theme(self._parent.theme.default)

    def add_settings(self):
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
                        getattr(self.theme, dpg.get_value(sender).lower())
                    ),
                )

            dpg.add_button(
                label="Launch Font Manager", width=-1, callback=dpg.show_font_manager
            )
            dpg.add_button(
                label="Launch Style Editor", width=-1, callback=dpg.show_style_editor
            )
            dpg.add_spacer(height=5)

    def tab_callback(self, sender, app_data, user_data):
        current_tab = dpg.get_item_label(app_data)
        dpg.configure_item(self.tag.plot_tab, show=(current_tab == "Viewer"))
        dpg.configure_item(self.tag.settings_tab, show=(current_tab != "Viewer"))
