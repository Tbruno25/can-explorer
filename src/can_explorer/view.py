from typing import Any, Callable, Iterable, Union, cast

import dearpygui.dearpygui as dpg
from dearpygui_ext.themes import create_theme_imgui_light

from can_explorer.config import Default, Font, Tag, Theme
from can_explorer.resources import Percentage


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


class PlotTable(PercentageWidthTableRow):
    def __init__(self, **kwargs) -> None:
        super().__init__(parent=Tag.TAB_VIEWER, **kwargs)

    def add_label(self, uuid: Any) -> None:
        return super().add_widget(uuid, Default.TABLE_COLUMN_1_WIDTH)

    def add_plot(self, uuid: Any):
        return super().add_widget(uuid, Default.TABLE_COLUMN_2_WIDTH)


class AppView:
    @staticmethod
    def _init_fonts():
        with dpg.font_registry():
            Font.DEFAULT = dpg.add_font(Default.FONT, Default.FONT_HEIGHT)
            Font.LABEL = dpg.add_font(Default.FONT, Default.FONT_HEIGHT * 1.75)

        dpg.bind_font(Font.DEFAULT)

    def _init_themes(self):
        with dpg.theme() as default:
            with dpg.theme_component(dpg.mvButton, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, Default.BACKGROUND)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, Default.BACKGROUND)

        Theme.DEFAULT = default
        Theme.LIGHT = create_theme_imgui_light()

        dpg.bind_theme(Theme.DEFAULT)

    @staticmethod
    def _header() -> None:
        def tab_callback(sender, app_data, user_data) -> None:
            current_tab = dpg.get_item_label(app_data)

            if current_tab == "Viewer":
                dpg.configure_item(Tag.TAB_VIEWER, show=True)
                dpg.configure_item(Tag.TAB_SETTINGS, show=False)
            else:
                dpg.configure_item(Tag.TAB_VIEWER, show=False)
                dpg.configure_item(Tag.TAB_SETTINGS, show=True)

        with dpg.tab_bar(tag=Tag.HEADER, callback=tab_callback):
            dpg.add_tab(label="Viewer")
            dpg.add_tab(label="Settings")

    def _body(self) -> None:
        with dpg.child_window(tag=Tag.BODY, border=False):
            with dpg.group(tag=Tag.TAB_VIEWER, show=True):
                self._viewer_tab()
            with dpg.group(tag=Tag.TAB_SETTINGS, show=False):
                self._settings_tab()

    @staticmethod
    def _footer() -> None:
        with dpg.child_window(
            tag=Tag.FOOTER, height=110, border=False, no_scrollbar=True
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
                            tag=Tag.SETTINGS_PLOT_BUFFER,
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
                            tag=Tag.SETTINGS_PLOT_HEIGHT,
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
                    tag=Tag.MAIN_BUTTON,
                    width=-100,
                    height=50,
                )
                dpg.add_button(
                    tag=Tag.CLEAR_BUTTON,
                    label="Clear",
                    width=-1,
                    height=50,
                )

    @staticmethod
    def _viewer_tab() -> None:
        ...

    @staticmethod
    def _settings_tab() -> None:
        with dpg.collapsing_header(label="CAN Bus", default_open=True):
            dpg.add_combo(tag=Tag.SETTINGS_INTERFACE, label="Interface")
            dpg.add_input_text(tag=Tag.SETTINGS_CHANNEL, label="Channel")
            dpg.add_combo(tag=Tag.SETTINGS_BAUDRATE, label="Baudrate")
            dpg.add_spacer(height=5)
            dpg.add_button(tag=Tag.SETTINGS_APPLY, label="Apply", height=30)
            dpg.add_spacer(height=5)

        with dpg.collapsing_header(label="GUI"):
            with dpg.group(horizontal=True):
                dpg.add_text("ID Format")
                dpg.add_radio_button(
                    ["Hex", "Dec"],
                    tag=Tag.SETTINGS_ID_FORMAT,
                    horizontal=True,
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Theme")
                dpg.add_radio_button(
                    ["Default", "Light"],
                    horizontal=True,
                    callback=lambda sender: dpg.bind_theme(
                        getattr(Theme, dpg.get_value(sender).upper())
                    ),
                )

            dpg.add_button(
                label="Launch Font Manager", width=-1, callback=dpg.show_font_manager
            )
            dpg.add_button(
                label="Launch Style Editor", width=-1, callback=dpg.show_style_editor
            )
            dpg.add_spacer(height=5)

    def create(self) -> None:
        self._init_fonts()
        self._init_themes()
        self._header()
        self._body()
        self._footer()

    @staticmethod
    def resize() -> None:
        dpg.set_item_height(
            Tag.BODY,
            (
                dpg.get_viewport_height()
                - dpg.get_item_height(Tag.FOOTER)
                - Default.FOOTER_OFFSET
            ),
        )
        dpg.set_item_width(Tag.SETTINGS_APPLY, dpg.get_viewport_width() // 4)

    @staticmethod
    def popup_error(name: Union[str, Exception], info: Union[str, Exception]) -> None:
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

    @staticmethod
    def get_settings_plot_buffer() -> int:
        percentage = dpg.get_value(Tag.SETTINGS_PLOT_BUFFER)
        return Percentage.reverse(percentage, Default.BUFFER_MAX)

    @staticmethod
    def get_settings_plot_height() -> int:
        percentage = dpg.get_value(Tag.SETTINGS_PLOT_HEIGHT)
        return Percentage.reverse(percentage, Default.PLOT_HEIGHT_MAX)

    @staticmethod
    def get_settings_interface() -> str:
        return dpg.get_value(Tag.SETTINGS_INTERFACE)

    @staticmethod
    def get_settings_channel() -> str:
        return dpg.get_value(Tag.SETTINGS_CHANNEL)

    @staticmethod
    def get_settings_baudrate() -> int:
        return dpg.get_value(Tag.SETTINGS_BAUDRATE)

    @staticmethod
    def get_settings_id_format() -> Callable:
        return cast(
            Callable,
            hex if dpg.get_value(Tag.SETTINGS_ID_FORMAT).lower() == "hex" else int,
        )

    @staticmethod
    def set_main_button_label(state: bool) -> None:
        dpg.set_item_label(Tag.MAIN_BUTTON, ("Stop", "Start")[not state])

    @staticmethod
    def set_main_button_callback(callback: Callable) -> None:
        dpg.configure_item(Tag.MAIN_BUTTON, callback=callback)

    @staticmethod
    def set_clear_button_callback(callback: Callable) -> None:
        dpg.configure_item(Tag.CLEAR_BUTTON, callback=callback)

    @staticmethod
    def set_plot_buffer_slider_callback(callback: Callable) -> None:
        dpg.configure_item(Tag.SETTINGS_PLOT_BUFFER, callback=callback)

    @staticmethod
    def set_plot_height_slider_callback(callback: Callable) -> None:
        dpg.configure_item(Tag.SETTINGS_PLOT_HEIGHT, callback=callback)

    @staticmethod
    def set_settings_apply_button_callback(callback: Callable) -> None:
        dpg.configure_item(Tag.SETTINGS_APPLY, callback=callback)

    @staticmethod
    def set_settings_can_id_format_callback(callback: Callable) -> None:
        dpg.configure_item(Tag.SETTINGS_ID_FORMAT, callback=callback)

    @staticmethod
    def set_settings_interface_options(
        iterable: Iterable[str], default: str = ""
    ) -> None:
        dpg.configure_item(
            Tag.SETTINGS_INTERFACE, items=iterable, default_value=default
        )

    @staticmethod
    def set_settings_channel_options(default: str = "") -> None:
        dpg.configure_item(Tag.SETTINGS_CHANNEL, default_value=default)

    @staticmethod
    def set_settings_baudrate_options(
        iterable: Iterable[str], default: str = ""
    ) -> None:
        dpg.configure_item(Tag.SETTINGS_BAUDRATE, items=iterable, default_value=default)
