import enum

import can
import dearpygui.dearpygui as dpg

from can_explorer import can_bus, layout, plotting

bus = None
plot_manager = plotting.PlotManager()


class State(enum.Flag):
    START = True
    STOP = False


def start_stop_button_callback(sender, app_data, user_data) -> None:
    state = State(user_data)
    dpg.configure_item(sender, label=state.name.capitalize(), user_data=not state)  # type: ignore[union-attr]


def plot_scale_slider_callback(sender, app_data, user_data) -> None:
    raise NotImplementedError


def plot_height_input_callback(sender, app_data, user_data) -> None:
    global plot_manager
    for plot in plot_manager.plots.values():
        for i in dpg.get_item_children(plot):
            dpg.set_item_height(i, layout.get_settings_user_plot_height())


def settings_apply_button_callback(sender, app_data, user_data) -> None:
    global bus

    try:
        bus = can.Bus(
            interface=layout.get_settings_user_interface(),
            channel=layout.get_settings_user_channel(),
            bitrate=layout.get_settings_user_baudrate(),
        )
    except Exception as e:
        layout.popup_box("ERROR", e)


dpg.create_context()


with dpg.window() as app_main:
    layout.create()


layout.set_settings_interface_options(can_bus.INTERFACES)
layout.set_settings_baudrate_options(can_bus.BAUDRATES)
layout.set_settings_apply_button_callback(settings_apply_button_callback)

layout.set_main_button_callback(start_stop_button_callback)
layout.set_plot_scale_slider_callback(plot_scale_slider_callback)
layout.set_settings_plot_height_callback(plot_height_input_callback)


dpg.create_viewport(title="CAN Explorer", width=layout.WIDTH, height=layout.HEIGHT)
dpg.set_viewport_resize_callback(layout.resize)
# dpg.set_viewport_max_height(645)
# dpg.set_viewport_max_width(750)
dpg.setup_dearpygui()
layout.resize()

plot_manager = plotting.PlotManager()
for i in range(100, 126):
    plot_manager.add_plot(str(i), "")


dpg.show_viewport()
dpg.set_primary_window(app_main, True)
dpg.start_dearpygui()
dpg.destroy_context()
