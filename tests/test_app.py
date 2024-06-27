from random import sample
from time import sleep

import pytest

DELAY = 0.1


def test_set_app_state_starts_worker(fake_app):
    fake_app.set_state(True)
    assert fake_app._worker.is_alive()


def test_set_app_state_stops_worker(fake_app):
    fake_app.set_state(True)
    assert fake_app._worker.is_alive()
    fake_app.set_state(False)
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


def test_gui_must_apply_settings_before_running(app):
    with pytest.raises(RuntimeError):
        app.start()


def test_gui_must_be_inactive_to_apply_settings(app):
    pass  # Todo
