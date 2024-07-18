import multiprocessing as mp
import os
import sys
from functools import partial
from pathlib import Path
from time import sleep

import dearpygui.dearpygui as dpg
import pyautogui
import pytest
from can_explorer.app import CanExplorer
from can_explorer.configs import Default
from can_explorer.resources import HOST_OS
from can_explorer.resources.demo import demo_config

from tests.resources import WITHIN_CI
from tests.resources.gui_components import Gui

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

        yield

        display.stop()


@pytest.fixture
def process(virtual_display):
    app = CanExplorer()
    proc = mp.Process(target=app.run, args=(demo_config,))
    proc.start()
    sleep(1)

    yield

    proc.kill()


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


def test_gui_launch_basic(app, controller, tag):
    assert dpg.is_dearpygui_running()

    # Check if the main window was created
    assert dpg.does_item_exist(tag.header)
    assert dpg.does_item_exist(tag.body)
    assert dpg.does_item_exist(tag.footer)

    # Check if key UI elements exist
    assert dpg.does_item_exist(tag.main_button)
    assert dpg.does_item_exist(tag.clear_button)
    assert dpg.does_item_exist(tag.plot_buffer_slider)
    assert dpg.does_item_exist(tag.plot_height_slider)

    # Check if the settings tab exists
    assert dpg.does_item_exist(tag.settings_tab)

    # Verify initial state
    assert not controller.is_active()
    assert dpg.get_item_label(tag.main_button) == "Start"


def test_gui_must_be_inactive_to_apply_settings(app, tag, controller):
    pytest.skip("Todo")
    # app.run()

    # dpg.set_value(tag.settings_interface, "virtual")
    # controller.settings_apply_button_callback()

    # controller.start_stop_button_callback()
    # assert controller.is_active()

    # dpg.set_value(tag.settings_interface, None)
    # with pytest.raises(RuntimeError):
    #     controller.settings_apply_button_callback()


def test_gui_visualizes_traffic(virtual_gui):
    pyautogui.click(pyautogui.locate(Gui.Button.START))
    sleep(1)
    viewer_traffic = pyautogui.locate(Gui.Acceptance.VISUALIZES_TRAFFIC, confidence=0.5)
    assert viewer_traffic is not None
