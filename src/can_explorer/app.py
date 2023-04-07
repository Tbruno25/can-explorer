import dearpygui.dearpygui as dpg
import layout

dpg.create_context()

with dpg.window() as app_main:
    layout.create()


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
