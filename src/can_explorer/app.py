import enum
import threading
from typing import Optional

import can
import dearpygui.dearpygui as dpg

from can_explorer import can_bus, layout, plotting
from can_explorer.layout import Default


class MainButtonState(enum.Flag):
    START = True
    STOP = False


class MainApp:
    _rate = 0.05
    _cancel = threading.Event()
    _worker: threading.Thread
    _state: MainButtonState

    bus: Optional[can.bus.BusABC] = None
    can_recorder = can_bus.Recorder()
    plot_manager = plotting.PlotManager()

    @property
    def is_active(self) -> bool:
        return bool(self._active)

    def set_state(self, state: MainButtonState) -> None:
        self._active = not state

        if self.is_active:
            self.start()
        else:
            self.stop()

    def repopulate(self) -> None:
        """
        Repopulate all plots in ascending order.
        """
        self.plot_manager.clear_all()
        for can_id, payload_buffer in sorted(self.can_recorder.data.items()):
            self.plot_manager.add(can_id, payload_buffer)

    def _get_plot_worker(self) -> threading.Thread:
        def loop():
            while not self._cancel.wait(self._rate):
                for can_id, payload_buffer in self.can_recorder.data.items():
                    if can_id not in self.plot_manager():
                        self.repopulate()
                        break
                    else:
                        self.plot_manager.update(can_id, payload_buffer)
            self._cancel.clear()

        return threading.Thread(target=loop, daemon=True)

    def start(self):
        if self.bus is None:
            raise Exception("ERROR: Must apply settings before starting")

        self.can_recorder.set_bus(self.bus)
        self.can_recorder.start()

        self._worker = self._get_plot_worker()
        self._worker.start()

    def stop(self):
        self._cancel.set()
        self._worker.join()


app = MainApp()


def start_stop_button_callback(sender, app_data, user_data) -> None:
    state = MainButtonState(user_data)
    try:
        app.set_state(state)
        dpg.configure_item(sender, label=state.name.capitalize(), user_data=app.is_active)  # type: ignore[union-attr]

    except Exception as e:
        layout.popup_error(name=type(e).__name__, info=e)


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

    try:
        app.bus = can.Bus(**{k: v for k, v in user_settings.items() if v})  # type: ignore

    except Exception as e:
        layout.popup_error(name=type(e).__name__, info=e)


dpg.create_context()


with dpg.window() as app_main:
    layout.create()


layout.set_settings_interface_options(can_bus.INTERFACES)
layout.set_settings_baudrate_options(can_bus.BAUDRATES)
layout.set_settings_apply_button_callback(settings_apply_button_callback)

layout.set_main_button_callback(start_stop_button_callback)
layout.set_clear_button_callback(clear_button_callback)

layout.set_plot_buffer_slider_callback(plot_buffer_slider_callback)
layout.set_plot_height_slider_callback(plot_height_slider_callback)


dpg.create_viewport(title="CAN Explorer", width=Default.WIDTH, height=Default.HEIGHT)
dpg.set_viewport_resize_callback(layout.resize)
# dpg.set_viewport_max_height(645)
# dpg.set_viewport_max_width(750)
dpg.setup_dearpygui()
layout.resize()

dpg.show_viewport()
dpg.set_primary_window(app_main, True)
dpg.start_dearpygui()
dpg.destroy_context()
