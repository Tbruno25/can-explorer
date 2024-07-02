import enum
import logging
import sys
import threading
from typing import Callable, Optional

import can
import dearpygui.dearpygui as dpg
from can.bus import BusABC

from can_explorer import can_bus
from can_explorer.can_bus import Recorder
from can_explorer.config import Default
from can_explorer.model import PlotModel
from can_explorer.view import AppView


class State(enum.Flag):
    ACTIVE = True
    STOPPED = False


class AppController:
    def __init__(
        self,
        model: PlotModel,
        view: AppView,
        bus: Optional[BusABC] = None,
        recorder: Optional[Recorder] = None,
        refresh_rate: Optional[float] = Default.REFRESH_RATE,
    ) -> None:
        self.model = model
        self.view = view
        self.recorder = Recorder() if recorder is None else recorder

        self._bus = bus
        self._rate = refresh_rate
        self._cancel = threading.Event()
        self._worker = threading.Thread()
        self._state = State.STOPPED

    @property
    def state(self) -> State:
        return self._state

    @property
    def bus(self) -> Optional[BusABC]:
        return self._bus

    @property
    def worker(self) -> threading.Thread:
        return self._worker

    def is_active(self) -> bool:
        return bool(self.state)

    def set_bus(self, bus: can.BusABC) -> None:
        """
        Set CAN bus to use during app loop.
        """
        self._bus = bus

    def start(self) -> None:
        """
        Initialize and start app loop.

        Raises:
            Exception: If CAN bus does not exist.
        """

        if self.bus is None:
            raise RuntimeError("Must apply settings before starting")

        self.recorder.set_bus(self.bus)
        self.recorder.start()

        self.create_worker_thread()
        self.worker.start()

        self.view.set_main_button_label(True)

        self._state = State.ACTIVE

    def stop(self) -> None:
        """
        Stop the app loop.
        """
        self.recorder.stop()
        self._cancel.set()
        self.worker.join()

        self.view.set_main_button_label(False)

        self._state = State.STOPPED

    def repopulate(self) -> None:
        """
        Repopulate all plots in ascending order.
        """
        self.model.clear_all()
        for can_id, payload_buffer in sorted(self.recorder.items()):
            self.model.add(can_id, payload_buffer)

    def _worker_loop(self) -> None:
        while not self._cancel.wait(self._rate):
            # Note: must convert can_recorder to avoid runtime error
            for can_id in tuple(self.recorder):
                if can_id not in self.model():
                    self.repopulate()
                    break
                else:
                    self.model.update(can_id)
        self._cancel.clear()

    def create_worker_thread(self) -> None:
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)

    def start_stop_button_callback(self, sender, app_data, user_data) -> None:
        self.stop() if self.is_active() else self.start()

    def clear_button_callback(self, sender, app_data, user_data) -> None:
        self.model.clear_all()

    def plot_buffer_slider_callback(self, sender, app_data, user_data) -> None:
        self.model.set_limit(self.view.get_settings_plot_buffer())

    def plot_height_slider_callback(self, sender, app_data, user_data) -> None:
        self.model.set_height(self.view.get_settings_plot_height())

    def settings_apply_button_callback(self, sender, app_data, user_data) -> None:
        user_settings = dict(
            interface=self.view.get_settings_interface(),
            channel=self.view.get_settings_channel(),
            bitrate=self.view.get_settings_baudrate(),
        )
        if self.is_active():
            raise RuntimeError("App must be stopped before applying new settings")
        bus = can.Bus(**{k: v for k, v in user_settings.items() if v})  # type: ignore
        self.set_bus(bus)

    def settings_can_id_format_callback(self, sender, app_data, user_data) -> None:
        self.model.set_id_format(self.view.get_settings_id_format())
        self.repopulate()

    def setup(self):
        dpg.create_context()

        with dpg.window() as app:
            self.view.create()

        self.view.set_settings_interface_options(can_bus.INTERFACES)
        self.view.set_settings_baudrate_options(can_bus.BAUDRATES)
        self.view.set_settings_apply_button_callback(
            self.settings_apply_button_callback
        )
        self.view.set_settings_can_id_format_callback(
            self.settings_can_id_format_callback
        )

        self.view.set_main_button_label(self.state)
        self.view.set_main_button_callback(self.start_stop_button_callback)
        self.view.set_clear_button_callback(self.clear_button_callback)

        self.view.set_plot_buffer_slider_callback(self.plot_buffer_slider_callback)
        self.view.set_plot_height_slider_callback(self.plot_height_slider_callback)

        dpg.create_viewport(
            title=Default.TITLE, width=Default.WIDTH, height=Default.HEIGHT
        )
        dpg.set_viewport_resize_callback(self.view.resize)
        dpg.setup_dearpygui()
        self.view.resize()

        dpg.set_primary_window(app, True)

    @staticmethod
    def teardown():
        dpg.destroy_context()

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        logging.debug(
            msg="ExceptionHandler", exc_info=(exc_type, exc_value, exc_traceback)
        )
        self.view.popup_error(name=exc_type.__name__, info=exc_value)

    def run(self, test_config: Optional[Callable] = None):
        self.setup()

        if test_config:
            test_config(self)

        sys.excepthook = self.exception_handler
        dpg.show_viewport()
        dpg.start_dearpygui()

        self.teardown()
