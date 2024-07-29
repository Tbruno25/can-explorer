import sys
from pathlib import Path
from threading import Thread
from unittest.mock import MagicMock

import can
import pytest
from can_explorer import CanExplorer, Controller, MainView, PlotModel
from can_explorer.tags import Tag

from .resources import CanExplorerTestWrapper, TestCommander


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
def sim_log():
    log_file = (
        Path(__file__).parents[1] / "src" / "can_explorer" / "resources" / "ic_sim.log"
    )
    # Play simulated logfile
    sys.argv = [sys.argv[0], "-i", "virtual", "-c", "pytest", str(log_file)]
    Thread(target=can.player.main, daemon=True).start()


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

    yield _app

    _app.teardown()


@pytest.fixture
def tester(app):
    wrapper = CanExplorerTestWrapper(app)
    commander = TestCommander(wrapper)

    yield commander

    commander.stop_gui()


@pytest.fixture
def fake_controller(model):
    yield Controller(
        model=model, recorder=MagicMock(), bus=MagicMock(), view=MagicMock()
    )
