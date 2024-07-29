import multiprocessing as mp
import os
import queue
import time
from unittest.mock import patch

import dearpygui.dearpygui as dpg
from can_explorer import CanExplorer

WITHIN_CI = os.getenv("GITHUB_ACTIONS")


def simulate_click(button_tag):
    # Simulate the button press
    dpg.configure_item(button_tag, state=dpg.mvGuiState_Pressed)
    dpg.split_frame()  # Process a single frame to update the UI
    # Simulate the button release
    dpg.configure_item(button_tag, state=dpg.mvGuiState_None)
    dpg.split_frame()  # Process a single frame to update the UI
    # Trigger the button's callback
    dpg.run_callbacks(dpg.mvMouseButton_Left, button_tag, None)


class CanExplorerTestWrapper:
    def __init__(self, app: CanExplorer):
        self.app = app
        self.tag = app.view.tag
        self.command_queue = mp.Queue()
        self.result_queue = mp.Queue()

    def click_main_button(self):
        simulate_click(self.tag.main_button)

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
