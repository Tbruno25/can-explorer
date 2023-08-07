import multiprocessing as mp
import os
import sys
from functools import partial
from pathlib import Path
from time import sleep

import can_explorer.app
import pyautogui
import pytest
from can_explorer.resources import HOST_OS
from can_explorer.resources.demo import demo_config

from tests.resources import WITHIN_CI
from tests.resources.gui_components import Gui

if HOST_OS == "linux":
    import Xlib.display
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
def gui_process(virtual_display):
    proc = mp.Process(target=can_explorer.app.main, args=(demo_config,))
    proc.start()
    sleep(1)

    yield

    proc.kill()


@pytest.fixture
def virtual_gui(request, gui_process):
    if HOST_OS == "windows":
        # Ensure window is active
        app_title = can_explorer.app.Default.TITLE
        app_window = pygetwindow.getWindowsWithTitle(app_title)[0]
        app_window.restore()

    else:
        # Attach pyautogui to the virtual display
        pyautogui._pyautogui_x11._display = Xlib.display.Display(os.getenv("DISPLAY"))

    yield

    if WITHIN_CI:
        save_screenshot(request)


"""
@pytest.fixture
def apply_settings():
    pyautogui.click(pyautogui.locate(Gui.Tab.SETTINGS))
    pyautogui.click(pyautogui.locate(Gui.Input.INTERFACE))
    pyautogui.moveRel(0, 50)
    pyautogui.scroll(-10)
    pyautogui.click(pyautogui.locate(Gui.Input.VIRTUAL))
    pyautogui.click(pyautogui.locate(Gui.Button.APPLY))
    pyautogui.click(
        pyautogui.locate(Gui.Tab.VIEWER), clicks=2, interval=1
    )  # twice for reliability
"""


def test_gui_launch_basic(virtual_gui):
    pass  # Todo


def test_gui_visualizes_traffic(virtual_gui):
    pyautogui.click(pyautogui.locate(Gui.Button.START))
    sleep(1)
    viewer_traffic = pyautogui.locate(Gui.Acceptance.VISUALIZES_TRAFFIC, confidence=0.5)
    assert viewer_traffic is not None
