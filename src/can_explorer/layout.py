import dearpygui.dearpygui as dpg
from typing import Final
from enum import IntEnum, auto

WIDTH: Final[int] = 600
HEIGHT: Final[int] = 600


class Tag(IntEnum):
    HEADER = auto()
    BODY = auto()
    FOOTER = auto()


def _header() -> None:
    ...


def _body() -> None:
    with dpg.child_window(tag=Tag.BODY, border=False):
        with dpg.tab_bar():
            with dpg.tab(label="Viewer"):
                _viewer_tab()
            with dpg.tab(label="Settings"):
                _settings_tab()


def _footer() -> None:
    with dpg.child_window(tag=Tag.FOOTER, height=110, border=False, no_scrollbar=True):
        dpg.add_spacer(height=2)
        dpg.add_separator()
        dpg.add_spacer(height=2)

        with dpg.group(horizontal=True):
            dpg.add_text("Plot Scale %")
            dpg.add_spacer()
            dpg.add_slider_int(width=-1, default_value=50, format="")
        dpg.add_spacer(height=2)

        dpg.add_separator()
        dpg.add_spacer()
        with dpg.table(
            header_row=False,
            borders_innerH=False,
            borders_innerV=False,
            borders_outerH=False,
            borders_outerV=False,
        ):
            dpg.add_table_column()
            dpg.add_table_column()
            with dpg.table_row(height=30):
                dpg.add_button(label="Start", width=-1, height=-1)
                dpg.add_button(label="Stop", width=-1, height=-1)


def _viewer_tab():
    ...


def _settings_tab() -> None:
    with dpg.collapsing_header(label="CAN Bus", default_open=True):
        dpg.add_spacer(height=5)
        dpg.add_input_text(label="Interface")
        dpg.add_spacer(height=5)
        dpg.add_input_text(label="Channel")
        dpg.add_spacer(height=5)
        dpg.add_input_int(label="Baudrate")
        dpg.add_spacer(height=5)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Apply", height=30)
            dpg.add_button(label="Clear", height=30)

    dpg.add_spacer(height=5)
    dpg.add_separator()
    dpg.add_spacer(height=5)

    with dpg.collapsing_header(label="GUI"):
        dpg.add_spacer(height=5)
        dpg.add_button(
            label="Launch Font Manager", width=-1, callback=dpg.show_font_manager
        )


def create() -> None:
    _header()
    _body()
    _footer()


def resize() -> None:
    dpg.set_item_height(
        Tag.BODY, (dpg.get_viewport_height() - dpg.get_item_height(Tag.FOOTER) - 20)
    )
