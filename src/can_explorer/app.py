import enum
import threading
from typing import Optional

import can
import dearpygui.dearpygui as dpg

from can_explorer import can_bus, layout, plotting


class MainButtonState(enum.Flag):
    START = True
    STOP = False


class MainApp:
    _rate = 0.05
    _cancel = threading.Event()
    _worker: Optional[threading.Thread] = None
    _state: Optional[MainButtonState] = None

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

    def _get_plot_worker(self) -> threading.Thread:
        def worker():
            while not self._cancel.wait(self._rate):
                for can_id, payloads in self.can_recorder.data.items():
                    if can_id not in self.plot_manager():
                        self.plot_manager.add(can_id, payloads)
                    else:
                        self.plot_manager.update(can_id, payloads)
            self._cancel.clear()

        return threading.Thread(target=worker, daemon=True)

    def start(self):
        if self.bus is None:
            raise Exception("ERROR: bus not set")

        self.can_recorder.bus = self.bus
        self.can_recorder.start()

        self._worker = self._get_plot_worker()
        self._worker.start()

    def stop(self):
        self._cancel.set()
        self._worker.join()

    def set_plot_limit(self, x_limit: int) -> None:
        # if not PayloadBuffer.MIN <= x_limit <= PayloadBuffer.MAX:
        #     raise Exception(f"Error: value must be between {PayloadBuffer.MIN} - {PayloadBuffer.MAX}")
        ...


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


def plot_scale_slider_callback(sender, app_data, user_data) -> None:
    raise NotImplementedError


def plot_height_input_callback(sender, app_data, user_data) -> None:
    app.plot_manager.set_height(layout.get_settings_user_plot_height())


def settings_apply_button_callback(sender, app_data, user_data) -> None:
    user_settings = dict(
        interface=layout.get_settings_user_interface(),
        channel=layout.get_settings_user_channel(),
        bitrate=layout.get_settings_user_baudrate(),
    )

    try:
        app.bus = can.Bus(**{k: v for k, v in user_settings.items() if v})

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

layout.set_plot_scale_slider_callback(plot_scale_slider_callback)
layout.set_settings_plot_height_callback(plot_height_input_callback)


dpg.create_viewport(title="CAN Explorer", width=layout.WIDTH, height=layout.HEIGHT)
dpg.set_viewport_resize_callback(layout.resize)
# dpg.set_viewport_max_height(645)
# dpg.set_viewport_max_width(750)
dpg.setup_dearpygui()
layout.resize()

dpg.show_viewport()
dpg.set_primary_window(app_main, True)
dpg.start_dearpygui()
dpg.destroy_context()
