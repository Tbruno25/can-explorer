import time

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


def test_controller_populates_data_in_ascending_order(controller, view, vbus1, vbus2):
    controller.set_bus(vbus1)
    controller.start()

    for _ in range(100):
        message = generate_random_can_message()
        vbus2.send(message)

    time.sleep(0.1)
    plots = view.plot.get_rows()
    assert plots and list(plots) == sorted(plots)
