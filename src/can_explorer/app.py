from __future__ import annotations

import logging
import sys
from collections.abc import Callable

import dearpygui.dearpygui as dpg

from can_explorer import can_bus
from can_explorer.configs import Default
from can_explorer.controllers import Controller
from can_explorer.models import PlotModel
from can_explorer.views import MainView


class CanExplorer:
    def __init__(self) -> None:
        self.model = PlotModel()
        self.view = MainView()
        self.controller = Controller(self.model, self.view)

    def setup(self):
        dpg.create_context()

        with dpg.window() as app:
            self.view.setup()

        self.view.settings.set_interface_options(can_bus.INTERFACES)
        self.view.settings.set_baudrate_options(can_bus.BAUDRATES)
        self.view.settings.set_apply_button_callback(
            self.controller.settings_apply_button_callback
        )
        self.view.settings.set_can_id_format_callback(
            self.controller.settings_can_id_format_callback
        )

        self.view.set_main_button_label(self.controller.state)
        self.view.set_main_button_callback(self.controller.start_stop_button_callback)
        self.view.set_clear_button_callback(self.controller.clear_button_callback)

        self.view.set_plot_buffer_slider_callback(
            self.controller.plot_buffer_slider_callback
        )
        self.view.set_plot_height_slider_callback(
            self.controller.plot_height_slider_callback
        )

        dpg.create_viewport(
            title=Default.TITLE, width=Default.WIDTH, height=Default.HEIGHT
        )
        dpg.set_viewport_resize_callback(self.view.resize)
        dpg.setup_dearpygui()
        self.view.resize()

        dpg.set_primary_window(app, True)

    def teardown(self):
        if self.controller.is_active():
            self.controller.stop()
        dpg.destroy_context()

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        logging.debug(
            msg="ExceptionHandler", exc_info=(exc_type, exc_value, exc_traceback)
        )
        self.view.popup_error(name=exc_type.__name__, info=exc_value)

    def run(self, test_config: Callable | None = None, show: bool = True):
        self.setup()

        if test_config:
            test_config(self)

        sys.excepthook = self.exception_handler

        if show:
            dpg.show_viewport()

        dpg.start_dearpygui()

        self.teardown()
