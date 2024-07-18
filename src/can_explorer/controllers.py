from __future__ import annotations

import enum
from threading import current_thread
from typing import cast

import can
from can.bus import BusABC

from can_explorer.can_bus import Recorder
from can_explorer.configs import Default
from can_explorer.models import PlotModel
from can_explorer.resources import StoppableThread
from can_explorer.views import MainView


class State(enum.Flag):
    RUNNING = True
    STOPPED = False


class Controller:
    def __init__(
        self,
        model: PlotModel,
        view: MainView,
        bus: BusABC | None = None,
        recorder: Recorder | None = None,
        refresh_rate: float | None = Default.REFRESH_RATE,
    ) -> None:
        self.model = model
        self.view = view
        self.recorder = recorder or Recorder()

        self._bus = bus
        self._rate = refresh_rate
        self._state = State.STOPPED
        self._worker: StoppableThread | None = None

    @property
    def state(self) -> State:
        return self._state

    @property
    def bus(self) -> BusABC | None:
        if self._bus is None:
            raise RuntimeError("Must apply settings before starting")
        return self._bus

    @property
    def worker(self) -> StoppableThread:
        if self._worker is None:
            raise RuntimeError("Worker not set.")
        return self._worker

    def is_active(self) -> bool:
        return bool(self.state)

    def set_bus(self, bus: can.BusABC) -> None:
        """
        Set CAN bus to use during controller loop.
        """
        self._bus = bus

    def start(self) -> None:
        """
        Initialize and start the controller loop.

        Raises:
            Exception: If CAN bus does not exist.
        """

        if self.state == State.RUNNING:
            raise RuntimeError("App is already running")

        self.recorder.set_bus(self.bus)
        self.recorder.start()

        self.create_worker_thread()
        self.worker.start()

        self.view.set_main_button_label(True)

        self._state = State.RUNNING

    def stop(self) -> None:
        """
        Stop the controller loop.
        """
        if self.state == State.STOPPED:
            return

        self.recorder.stop()
        self.worker.stop()

        self.view.set_main_button_label(False)

        self._state = State.STOPPED

    def _worker_loop(self) -> None:
        thread = cast(StoppableThread, current_thread())
        while not thread.cancel.wait(self._rate):
            current_data = self.recorder.get_data()

            for can_id, payloads in current_data.items():
                self.model.update(can_id, payloads)
                plot_data = self.model.get_plot_data(can_id)
                self.view.plot.update(can_id, plot_data)

    def create_worker_thread(self) -> None:
        self._worker = StoppableThread(target=self._worker_loop, daemon=True)

    def start_stop_button_callback(self, *args, **kwargs) -> None:
        self.stop() if self.is_active() else self.start()

    def clear_button_callback(self, *args, **kwargs) -> None:
        self.model.clear()
        self.view.plot.clear()

    def plot_buffer_slider_callback(self, *args, **kwargs) -> None:
        self.model.set_limit(self.view.get_plot_buffer())
        for can_id, payloads in self.recorder.get_data().items():
            self.model.update(can_id, payloads)
            plot_data = self.model.get_plot_data(can_id)
            self.view.plot.update(can_id, plot_data)

    def plot_height_slider_callback(self, *args, **kwargs) -> None:
        self.view.plot.set_height(self.view.get_plot_height())

    def settings_apply_button_callback(self, *args, **kwargs) -> None:
        if self.is_active():
            raise RuntimeError("App must be stopped before applying new settings")

        user_settings = dict(
            interface=self.view.settings.get_interface(),
            channel=self.view.settings.get_channel(),
            baudrate=self.view.settings.get_baudrate(),
        )

        bus = can.Bus(**{k: v for k, v in user_settings.items() if v})  # type: ignore [arg-type]
        self.set_bus(bus)

    def settings_can_id_format_callback(self, *args, **kwargs) -> None:
        self.view.plot.set_format(self.view.settings.get_id_format())
