from unittest.mock import Mock

import can
import pytest
from can_explorer.can_bus import Recorder
from can_explorer.controller import AppController
from can_explorer.model import PlotModel
from can_explorer.view import AppView


@pytest.fixture
def vbus1():
    yield can.interface.Bus(interface="virtual", channel="pytest")


@pytest.fixture
def vbus2():
    yield can.interface.Bus(interface="virtual", channel="pytest")


@pytest.fixture
def recorder():
    yield Recorder()


@pytest.fixture
def model():
    yield PlotModel()


@pytest.fixture
def view():
    yield AppView()


@pytest.fixture
def fake_controller(recorder, model):
    yield AppController(model=model, recorder=recorder, bus=Mock(), view=Mock())


@pytest.fixture
def controller(model, view):
    controller = AppController(model, view)
    controller.setup()
    yield controller
    controller.teardown()
