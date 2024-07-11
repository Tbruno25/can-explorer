import time

import pytest
from can_explorer.can_bus import generate_random_can_message


def test_controller_starts_worker(fake_controller):
    fake_controller.start()
    assert fake_controller.is_active()
    assert fake_controller.worker.is_alive()


def test_controller_stops_worker(fake_controller):
    fake_controller.start()
    assert fake_controller.is_active()
    assert fake_controller.worker.is_alive()
    fake_controller.stop()
    assert not fake_controller.is_active()
    assert not fake_controller.worker.is_alive()


def test_controller_populates_data_in_ascending_order(app, controller, view, vbus):
    controller.start()

    for _ in range(100):
        message = generate_random_can_message()
        vbus.send(message)

    time.sleep(0.1)
    plots = view.plot.get_rows()
    assert plots and list(plots) == sorted(plots)


def test_controller_must_have_bus_set_before_starting(app, tag, controller):
    controller.set_bus(None)
    with pytest.raises(RuntimeError):
        controller.start()


def test_controller_cannot_start_without_stopping(app, tag, controller):
    controller.start()
    assert controller.is_active()
    with pytest.raises(RuntimeError):
        controller.start()
