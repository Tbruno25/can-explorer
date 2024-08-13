import sys
from pathlib import Path

import dearpygui.dearpygui as dpg
import pyautogui
import pytest
from can_explorer.resources import HOST_OS

from tests.resources import WITHIN_CI
from tests.resources.gui_components import Gui


def save_snapshot(request, path: Path = Path("screenshots")) -> None:
    name = request.node.name
    major, minor, micro, *_ = sys.version_info
    screenshot = pyautogui.screenshot()
    screenshot.save(str(path / f"{HOST_OS}_{major}-{minor}-{micro}_{name}.png"))


@pytest.fixture(autouse=True)
def snapshot(request):
    yield

    if WITHIN_CI:
        save_snapshot(request)


def test_gui_launch(app, controller, tag):
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


@pytest.mark.skip("Reimplement")
def test_gui_visualizes_traffic(dpgtester):
    dpgtester.start_gui()
    viewer_traffic = pyautogui.locateCenterOnScreen(
        Gui.Acceptance.VISUALIZES_TRAFFIC, confidence=True, grayscale=True
    )
    assert viewer_traffic is not None
