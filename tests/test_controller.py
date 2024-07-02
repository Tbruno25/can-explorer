import time
from unittest.mock import Mock

import dearpygui.dearpygui as dpg
import pytest
from can_explorer import AppController, PlotModel
from can_explorer.config import Tag
from can_explorer.resources import generate_random_can_message

DELAY = 0.1

NONE = (None, None, None)


def test_controller_starts_worker(fake_controller):
    fake_controller.start()
    assert fake_controller.worker.is_alive()


def test_controller_stops_worker(fake_controller):
    fake_controller.start()
    assert fake_controller.is_active()
    assert fake_controller.worker.is_alive()
    fake_controller.stop()
    assert not fake_controller.worker.is_alive()


@pytest.mark.skip
def test_controller_populates_data_in_ascending_order(vbus1, vbus2):
    controller = AppController(model=PlotModel(), view=Mock(), bus=vbus1)
    controller.start()

    for _ in range(100):
        message = generate_random_can_message()
        vbus2.send(message)

    time.sleep(5)
    print(controller.model())


def test_app_controller_must_apply_settings_before_running(controller):
    dpg.set_value(Tag.SETTINGS_INTERFACE, None)
    with pytest.raises(RuntimeError):
        controller.start_stop_button_callback(*NONE)


def test_app_controller_must_be_inactive_to_apply_settings(controller):
    dpg.set_value(Tag.SETTINGS_INTERFACE, "virtual")
    controller.settings_apply_button_callback(*NONE)

    controller.start_stop_button_callback(*NONE)
    assert controller.is_active()

    dpg.set_value(Tag.SETTINGS_INTERFACE, None)
    with pytest.raises(RuntimeError):
        controller.settings_apply_button_callback(*NONE)
