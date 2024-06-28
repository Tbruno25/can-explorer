import enum
import logging
import sys
import threading
from typing import Callable, Optional

import can
import can.player
import dearpygui.dearpygui as dpg

from can_explorer import can_bus, layout, plotting
from can_explorer.layout import Default


class State(enum.Flag):
    ACTIVE = True
    STOPPED = False


class MainApp:
    _rate = 0.05
    _cancel = threading.Event()
    _state = State.STOPPED
    _worker: threading.Thread

    bus: Optional[can.bus.BusABC] = None
    can_recorder = can_bus.Recorder()
    plot_manager = plotting.PlotManager()

    @property
    def state(self) -> State:
        return self._state

    def is_active(self) -> bool:
        return bool(self._state)

    def repopulate(self) -> None:
        """
        Repopulate all plots in ascending order.
        """
        self.plot_manager.clear_all()
        for can_id, payload_buffer in sorted(self.can_recorder.items()):
            self.plot_manager.add(can_id, payload_buffer)

    def _get_worker(self) -> threading.Thread:
        """
        Get the main loop worker thread.

        Returns:
            threading.Thread: Worker
        """

        def loop() -> None:
            while not self._cancel.wait(self._rate):
                # Note: must convert can_recorder to avoid runtime error
                for can_id in tuple(self.can_recorder):
                    if can_id not in self.plot_manager():
                        self.repopulate()
                        break
                    else:
                        self.plot_manager.update(can_id)
            self._cancel.clear()

        return threading.Thread(target=loop, daemon=True)

    def start(self) -> None:
        """
        Initialize and start app loop.

        Raises:
            Exception: If CAN bus does not exist.
        """
        if self.bus is None:
            raise RuntimeError("Must apply settings before starting")

        self.can_recorder.set_bus(self.bus)
        self.can_recorder.start()

        self._worker = self._get_worker()
        self._worker.start()

        self._state = State.ACTIVE

    def stop(self) -> None:
        """
        Stop the app loop.
        """
        self.can_recorder.stop()
        self._cancel.set()
        self._worker.join()

        self._state = State.STOPPED

    def set_bus(self, bus: can.BusABC) -> None:
        """
        Set CAN bus to use during app loop.
        """
        self.bus = bus


app = MainApp()


def start_stop_button_callback(sender, app_data, user_data) -> None:
    app.stop() if app.is_active() else app.start()
    layout.set_main_button_label(app.state)


def clear_button_callback(sender, app_data, user_data) -> None:
    app.plot_manager.clear_all()


def plot_buffer_slider_callback(sender, app_data, user_data) -> None:
    app.plot_manager.set_limit(layout.get_settings_plot_buffer())


def plot_height_slider_callback(sender, app_data, user_data) -> None:
    app.plot_manager.set_height(layout.get_settings_plot_height())


def settings_apply_button_callback(sender, app_data, user_data) -> None:
    user_settings = dict(
        interface=layout.get_settings_interface(),
        channel=layout.get_settings_channel(),
        bitrate=layout.get_settings_baudrate(),
    )
    if app.is_active():
        raise RuntimeError("App must be stopped before applying new settings")
    bus = can.Bus(**{k: v for k, v in user_settings.items() if v})  # type: ignore
    app.set_bus(bus)


def settings_can_id_format_callback(sender, app_data, user_data) -> None:
    app.plot_manager.set_id_format(layout.get_settings_id_format())
    app.repopulate()


def setup():
    dpg.create_context()

    with dpg.window() as app_main:
        layout.create()

    layout.set_settings_interface_options(can_bus.INTERFACES)
    layout.set_settings_baudrate_options(can_bus.BAUDRATES)
    layout.set_settings_apply_button_callback(settings_apply_button_callback)
    layout.set_settings_can_id_format_callback(settings_can_id_format_callback)

    layout.set_main_button_label(app.state)
    layout.set_main_button_callback(start_stop_button_callback)
    layout.set_clear_button_callback(clear_button_callback)

    layout.set_plot_buffer_slider_callback(plot_buffer_slider_callback)
    layout.set_plot_height_slider_callback(plot_height_slider_callback)

    dpg.create_viewport(title=Default.TITLE, width=Default.WIDTH, height=Default.HEIGHT)
    dpg.set_viewport_resize_callback(layout.resize)
    dpg.setup_dearpygui()
    layout.resize()

    dpg.set_primary_window(app_main, True)


def teardown():
    dpg.destroy_context()


def exception_handler(exc_type, exc_value, exc_traceback):
    logging.debug(msg="ExceptionHandler", exc_info=(exc_type, exc_value, exc_traceback))
    layout.popup_error(name=exc_type.__name__, info=exc_value)


def main(test_config: Optional[Callable] = None):
    setup()

    if test_config:
        test_config()

    sys.excepthook = exception_handler
    dpg.show_viewport()
    dpg.start_dearpygui()

    teardown()


if __name__ == "__main__":
    main()
