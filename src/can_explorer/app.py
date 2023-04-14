import enum
import math

import can
import dearpygui.dearpygui as dpg

from can_explorer import can_bus, layout, plotting, threads

# creating data
payload = []
for i in range(0, 500):
    payload.append(0.5 + 0.5 * math.sin(50 * i / 1000))

data = {i: payload for i in range(10)}

bus = None
can_recorder = None
plot_manager = plotting.PlotManager()
plot_worker = None


class State(enum.Flag):
    START = True
    STOP = False


class AutoPlotter(threads.StoppableThread):
    def __init__(
        self, data: can_bus.CANData, manager: plotting.PlotManager, rate: float = 0.05
    ):
        super().__init__()
        self.data = data
        self.manager = manager
        self.rate = rate

    def run(self) -> None:
        while not self.cancel.wait(self.rate):
            for can_id, payload in self.data.items():
                if can_id in self.manager.plots:
                    break
                self.manager.add_plot(can_id, payload)


def start_stop_button_callback(sender, app_data, user_data) -> None:
    global can_recorder
    global plot_worker

    state = State(user_data)
    is_active = not state
    dpg.configure_item(sender, label=state.name.capitalize(), user_data=is_active)  # type: ignore[union-attr]

    try:
        if is_active:
            # can_recorder = can_bus.Recorder(bus)
            # can_recorder.start()
            plot_worker = AutoPlotter(data, plot_manager)
            plot_worker.start()
        else:
            # can_recorder.stop()
            plot_worker.stop()

    except Exception as e:
        layout.popup_error(name=type(e).__name__, info=e)


def clear_button_callback(sender, app_data, user_data) -> None:
    plot_manager.clear_all()


def plot_scale_slider_callback(sender, app_data, user_data) -> None:
    raise NotImplementedError


def plot_height_input_callback(sender, app_data, user_data) -> None:
    plot_manager.set_height(layout.get_settings_user_plot_height())


def settings_apply_button_callback(sender, app_data, user_data) -> None:
    global bus

    user_settings = dict(
        interface=layout.get_settings_user_interface(),
        channel=layout.get_settings_user_channel(),
        bitrate=layout.get_settings_user_baudrate(),
    )

    try:
        bus = can.Bus(**{k: v for k, v in user_settings.items() if v})
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
