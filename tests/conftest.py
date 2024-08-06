from unittest.mock import MagicMock

import can
import pytest
from can_explorer import CanExplorer, Controller, MainView, PlotModel
from can_explorer.resources.demo import demo_config
from can_explorer.tags import Tag


@pytest.fixture
def vbus():
    bus = can.interface.Bus(interface="virtual", channel="pytest")
    yield bus
    bus.shutdown()


@pytest.fixture
def vbus2():
    bus = can.interface.Bus(interface="virtual", channel="pytest")
    yield bus
    bus.shutdown()


@pytest.fixture
def model():
    yield PlotModel()


@pytest.fixture
def view():
    yield MainView()


@pytest.fixture
def controller(model, view, vbus2):
    yield Controller(model, view, vbus2)


@pytest.fixture
def tag():
    yield Tag()


@pytest.fixture
def app(controller, tag):
    _app = CanExplorer(controller=controller, tags=tag)
    _app.setup()
    yield _app
    _app.teardown()


@pytest.fixture(autouse=True)
def set_dpgtester_target(app, dpgtester):
    def func():
        demo_config(app)
        app.run()

    dpgtester.set_target(func)
    yield


@pytest.fixture
def fake_controller(model):
    yield Controller(
        model=model, recorder=MagicMock(), bus=MagicMock(), view=MagicMock()
    )
