import multiprocessing as mp
import os
import platform
import sys
from functools import partial
from pathlib import Path
from time import sleep

import can_explorer.app
import pyautogui
import pytest
import Xlib.display
from can_explorer.resources.demo import demo_config
from pyvirtualdisplay.smartdisplay import SmartDisplay

from tests.resources.gui_components import Gui

pytestmark = pytest.mark.skipif(
    platform.system() != "Linux", reason="Only compatible with linux hosts"
)

IN_CI = os.getenv("GITHUB_ACTIONS")

VISIBLE = True
XAUTH = True

pyautogui.locate = partial(pyautogui.locateCenterOnScreen, grayscale=True)


def save_screenshot(display, request, path: Path = Path("screenshots")) -> None:
    name = request.node.name
    major, minor, micro, *_ = sys.version_info
    screenshot = display.waitgrab()
    screenshot.save(str(path / f"{major}-{minor}-{micro}_{name}.png"))


@pytest.fixture
def virtual_gui(request):
    with SmartDisplay(visible=VISIBLE, use_xauth=XAUTH) as display:
        # Attach pyautogui to the virtual display
        pyautogui._pyautogui_x11._display = Xlib.display.Display(os.getenv("DISPLAY"))

        proc = mp.Process(target=can_explorer.app.main, args=(demo_config,))
        proc.start()
        sleep(0.5)

        yield

        if IN_CI:
            save_screenshot(display, request)

        proc.kill()


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
