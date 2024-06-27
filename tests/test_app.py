from random import sample
from time import sleep

import dearpygui.dearpygui as dpg
import pytest
from can_explorer.app import settings_apply_button_callback
from can_explorer.layout import Tag

DELAY = 0.1


def test_app_starts_worker(fake_app):
    fake_app.start()
    assert fake_app._worker.is_alive()


def test_app_stops_worker(fake_app):
    fake_app.start()
    assert fake_app.is_active()
    assert fake_app._worker.is_alive()
    fake_app.stop()
    assert not fake_app._worker.is_alive()


def test_app_populates_data_in_ascending_order(fake_app, fake_manager, fake_recorder):
    data = sample(range(250), 25)

    fake_app.start()

    for i in data:
        fake_recorder[i] = [0]

    sleep(DELAY)
    sorted_data = list(sorted(data))
    sorted_keys = list(fake_manager.row.keys())

    assert sorted_data == sorted_keys


def test_app_must_apply_settings_before_running(app):
    dpg.set_value(Tag.SETTINGS_INTERFACE, None)
    with pytest.raises(RuntimeError):
        app.start()


def test_app_must_be_inactive_to_apply_settings(app):
    dpg.set_value(Tag.SETTINGS_INTERFACE, "virtual")
    settings_apply_button_callback(None, None, None)

    app.start()
    assert app.is_active()

    dpg.set_value(Tag.SETTINGS_INTERFACE, None)
    with pytest.raises(RuntimeError):
        settings_apply_button_callback(None, None, None)
