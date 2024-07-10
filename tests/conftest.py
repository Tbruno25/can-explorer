from unittest.mock import MagicMock

import can
import pytest
from can_explorer.app import CanExplorer
from can_explorer.controllers import Controller


@pytest.fixture
def vbus1():
    yield can.interface.Bus(interface="virtual", channel="pytest")


@pytest.fixture
def vbus2():
    yield can.interface.Bus(interface="virtual", channel="pytest")


@pytest.fixture
def app():
    ce = CanExplorer()
    ce.setup()
    yield ce
    ce.teardown()


@pytest.fixture
def controller(app):
    yield app.controller


@pytest.fixture
def view(app):
    yield app.view


@pytest.fixture
def tag(view):
    yield view.tag


@pytest.fixture
def model(app):
    yield app.model


@pytest.fixture
def fake_controller(model):
    yield Controller(
        model=model, recorder=MagicMock(), bus=MagicMock(), view=MagicMock()
    )
