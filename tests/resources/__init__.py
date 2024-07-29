import multiprocessing as mp
import os
import queue
import time
from unittest.mock import patch

import dearpygui.dearpygui as dpg
import pyautogui
from can_explorer import CanExplorer

WITHIN_CI = os.getenv("GITHUB_ACTIONS")


def get_button_click_coordinates():
    # Get GUI window position
    gui_x, gui_y = dpg.get_viewport_pos()

    button_coordinates = []

    # Iterate through all items in the registry
    for item in dpg.get_all_items():
        if dpg.get_item_type(item) == "mvAppItemType::mvButton":
            # Get button position and dimensions using rect_min and rect_max
            button_min_x, button_min_y = dpg.get_item_rect_min(item)
            button_max_x, button_max_y = dpg.get_item_rect_max(item)

            # Calculate button center
            button_center_x = (button_min_x + button_max_x) / 2
            button_center_y = (button_min_y + button_max_y) / 2

            # Calculate absolute screen coordinates for button center
            abs_x = gui_x + button_center_x
            abs_y = gui_y + button_center_y

            button_coordinates.append((item, abs_x, abs_y))
    return button_coordinates


class CanExplorerTestWrapper:
    def __init__(self, app: CanExplorer):
        self.app = app
        self.tag = app.view.tag
        self.command_queue = mp.Queue()
        self.result_queue = mp.Queue()

    def click_main_button(self):
        buttons = get_button_click_coordinates()
        for button, x, y in buttons:
            if button == self.tag.main_button:
                pyautogui.click(x, y)

    def command_loop(self):
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()
            try:
                command = self.command_queue.get_nowait()
                if isinstance(command, tuple):
                    method, arg = command
                    result = getattr(self, method)(arg)
                else:
                    result = getattr(self, command)()
                self.result_queue.put(result)
            except queue.Empty:
                pass

    def start_sim_log(self):
        pass

    def run(self):
        with patch.object(dpg, "start_dearpygui", new=self.command_loop):
            self.app.run()


class TestCommander:
    def __init__(self, app: CanExplorerTestWrapper):
        self.app = app

    def start_gui(self):
        self.process = mp.Process(target=self.app.run)
        self.process.start()
        time.sleep(1)

    def stop_gui(self):
        if self.process:
            self.process.kill()

    def items(self):
        self.app.command_queue.put("items")
        return self.app.result_queue.get()

    def click_main_button(self):
        self.app.command_queue.put("click_main_button")
        return self.app.result_queue.get()

    def click_clear_button(self):
        self.app.command_queue.put("click_clear_button")
        return self.app.result_queue.get()

    def set_buffer_slider(self, value: int):
        self.app.command_queue.put(("set_buffer_slider", value))
        return self.app.result_queue.get()

    def set_height_slider(self, value: int):
        self.app.command_queue.put(("set_height_slider", value))
        return self.app.result_queue.get()
