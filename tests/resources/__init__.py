import multiprocessing as mp
import os
import queue
import time

import dearpygui.dearpygui as dpg
from can_explorer import CanExplorer

WITHIN_CI = os.getenv("GITHUB_ACTIONS")


class TestCommander:
    def __init__(self, app: CanExplorer):
        self.app = app
        self.process: mp.Process | None = None
        self.command_queue = mp.Queue()
        self.result_queue = mp.Queue()

    def start_gui(self):
        self.process = mp.Process(target=self.app.run)
        time.sleep(1)  # Give the GUI time to start up

    def stop_gui(self):
        if self.process:
            self.process.kill()

    def click_start_stop_button(self):
        self.command_queue.put("click_start_stop_button")
        return self.result_queue.get()

    def click_clear_button(self):
        self.command_queue.put("click_clear_button")
        return self.result_queue.get()

    def set_plot_buffer(self, value: int):
        self.command_queue.put(("set_plot_buffer", value))
        return self.result_queue.get()

    def set_plot_height(self, value: int):
        self.command_queue.put(("set_plot_height", value))
        return self.result_queue.get()


class TestReceiver(CanExplorer):
    def __init__(self, app: CanExplorer):
        self.app = app
        self.command_queue = mp.Queue()
        self.result_queue = mp.Queue()

    def run(self):
        # ... existing setup ...

        while True:
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
