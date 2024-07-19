from __future__ import annotations

import logging
import sys
from collections.abc import Callable

import can
import dearpygui.dearpygui as dpg

from can_explorer.configs import CANBus, Default
from can_explorer.controllers import Controller
from can_explorer.models import PlotModel
from can_explorer.tags import Tag
from can_explorer.views import MainView


class CanExplorer:
    def __init__(
        self,
        model: PlotModel | None = None,
        view: MainView | None = None,
        controller: Controller | None = None,
        bus: can.BusABC | None = None,
        tags: Tag | None = None,
    ):
        if controller and any([model, view]):
            raise RuntimeError(
                "Too many arguments | [model, view] or [controller] can be supplied, but not both."
            )

        elif controller is None:
            self.model = model or PlotModel()
            self.view = view or MainView()
            self.controller = Controller(self.model, self.view)

        else:
            self.model = controller.model
            self.view = controller.view
            self.controller = controller

        if bus is not None:
            self.controller.set_bus(bus)

        if tags is not None:
            self.view.tag = tags

    def setup(self):
        dpg.create_context()

        main_window = self.view.ui.build()

        self.view.settings.set_interface_options(CANBus.INTERFACES)
        self.view.settings.set_baudrate_options(CANBus.BAUDRATES)
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

        dpg.set_primary_window(main_window, True)

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
