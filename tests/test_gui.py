import os
import sys
from functools import partial
from pathlib import Path
from random import randint

import dearpygui.dearpygui as dpg
import pyautogui
import pytest
from can_explorer.configs import Default
from can_explorer.resources import HOST_OS

from tests.resources import WITHIN_CI

if HOST_OS == "linux":
    import Xlib.display
    from pyvirtualdisplay.smartdisplay import SmartDisplay

elif HOST_OS == "darwin":
    from pyvirtualdisplay.smartdisplay import SmartDisplay

elif HOST_OS == "windows":
    import pygetwindow

pyautogui.locate = partial(pyautogui.locateCenterOnScreen, grayscale=True)


def save_screenshot(request, path: Path = Path("screenshots")) -> None:
    name = request.node.name
    major, minor, micro, *_ = sys.version_info
    screenshot = pyautogui.screenshot()
    screenshot.save(str(path / f"{HOST_OS}_{major}-{minor}-{micro}_{name}.png"))


@pytest.fixture
def virtual_display():
    if HOST_OS == "windows":
        # Virtual display not needed
        yield

    else:
        display = SmartDisplay(visible=True, use_xauth=True)
        display.start()

        yield display

        display.stop()


@pytest.fixture
def virtual_gui(request, process):
    if HOST_OS == "windows":
        # Ensure window is active
        app_title = Default.TITLE
        app_window = pygetwindow.getWindowsWithTitle(app_title)[0]
        app_window.restore()

    elif HOST_OS == "linux":
        # Attach pyautogui to the virtual display
        pyautogui._pyautogui_x11._display = Xlib.display.Display(os.getenv("DISPLAY"))

    yield

    if WITHIN_CI:
        save_screenshot(request)


def test_gui_launch(app, controller, tag):
    app.setup()

    assert dpg.is_dearpygui_running()

    assert dpg.does_item_exist(tag.header)
    assert dpg.does_item_exist(tag.body)
    assert dpg.does_item_exist(tag.footer)

    assert dpg.does_item_exist(tag.main_button)
    assert dpg.does_item_exist(tag.clear_button)
    assert dpg.does_item_exist(tag.plot_buffer_slider)
    assert dpg.does_item_exist(tag.plot_height_slider)

    assert dpg.does_item_exist(tag.settings_tab)

    assert not controller.is_active()
    assert dpg.get_item_label(tag.main_button) == "Start"


def test_gui_visualizes_traffic(dpgtester, sim_log):
    dpgtester.start_gui()
    dpgtester.click_button("Start")
    # viewer_traffic = pyautogui.locate(Gui.Acceptance.VISUALIZES_TRAFFIC, confidence=0.5)
    # assert viewer_traffic is not None


def test_rapid_gui_interaction(dpgtester, sim_log):
    dpgtester.start_gui()
    dpgtester.click_button("Start")

    for _ in range(5):
        dpgtester.drag_slider("Message Buffer Size", randint(2, 100))
        dpgtester.drag_slider("Plot Height", randint(10, 100))
