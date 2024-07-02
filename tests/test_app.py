import dearpygui.dearpygui as dpg
import pytest


def test_app_must_apply_settings_before_running(tag, controller):
    dpg.set_value(tag.settings_interface, None)
    with pytest.raises(RuntimeError):
        controller.start_stop_button_callback()


def test_app_must_be_inactive_to_apply_settings(tag, controller):
    dpg.set_value(tag.settings_interface, "virtual")
    controller.settings_apply_button_callback()

    controller.start_stop_button_callback()
    assert controller.is_active()

    dpg.set_value(tag.settings_interface, None)
    with pytest.raises(RuntimeError):
        controller.settings_apply_button_callback()
