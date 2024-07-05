from __future__ import annotations

import enum
from threading import Lock, current_thread
from typing import cast

import can
from can.bus import BusABC

from can_explorer.can_bus import Recorder
from can_explorer.configs import Default
from can_explorer.models import PlotModel
from can_explorer.resources import StoppableThread
from can_explorer.views import MainView


class State(enum.Flag):
    ACTIVE = True
    STOPPED = False


class Controller:
    _lock: Lock

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
        self.recorder = Recorder() if recorder is None else recorder

        self._bus = bus
        self._rate = refresh_rate
        self._state = State.STOPPED
        self._worker: StoppableThread | None = None

    @property
    def state(self) -> State:
        return self._state

    @property
    def bus(self) -> BusABC | None:
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
        Set CAN bus to use during app loop.
        """
        self._bus = bus

    def start(self) -> None:
        """
        Initialize and start app loop.

        Raises:
            Exception: If CAN bus does not exist.
        """

        if self.bus is None:
            raise RuntimeError("Must apply settings before starting")

        self._lock = Lock()

        self.recorder.set_bus(self.bus)
        self.recorder.start()

        self.create_worker_thread()
        self.worker.start()

        self.view.set_main_button_label(True)

        self._state = State.ACTIVE

    def stop(self) -> None:
        """
        Stop the app loop.
        """
        self.recorder.stop()
        self.worker.stop()

        self.view.set_main_button_label(False)

        self._state = State.STOPPED

    def repopulate(self) -> None:
        """
        Repopulate all plots in ascending order.
        """
        with self._lock:
            self.view.plot.clear()
            for can_id, plot_data in sorted(self.model.get_plots().items()):
                self.view.plot.add(can_id, **plot_data)

    def _worker_loop(self) -> None:
        thread = cast(StoppableThread, current_thread())
        while not thread.cancel.wait(self._rate):
            current_data = self.recorder.get_data()
            current_plots = self.model.get_plots()
            refresh = False

            for can_id, payloads in current_data.items():
                self.model.update_plot(can_id, payloads)
                plot_data = self.model.get_plot_data(can_id)

                with self._lock:
                    if can_id not in current_plots:
                        self.view.plot.add(can_id, **plot_data)
                        refresh = True
                    else:
                        self.view.plot.update(can_id, **plot_data)

            if refresh:
                self.repopulate()

    def create_worker_thread(self) -> None:
        self._worker = StoppableThread(target=self._worker_loop, daemon=True)

    def start_stop_button_callback(self, sender, app_data, user_data) -> None:
        self.stop() if self.is_active() else self.start()

    def clear_button_callback(self, sender, app_data, user_data) -> None:
        self.model.clear()
        with self._lock:
            self.view.plot.clear()

    def plot_buffer_slider_callback(self, sender, app_data, user_data) -> None:
        self.model.set_limit(self.view.get_plot_buffer())
        for can_id, payloads in self.recorder.get_data().items():
            self.model.update_plot(can_id, payloads)
            plot_data = self.model.get_plot_data(can_id)
            with self._lock:
                self.view.plot.update(can_id, **plot_data)

    def plot_height_slider_callback(self, sender, app_data, user_data) -> None:
        with self._lock:
            self.view.plot.clear()
            self.view.plot.set_height(self.view.get_plot_height())
        self.repopulate()

    def settings_apply_button_callback(self, sender, app_data, user_data) -> None:
        user_settings = dict(
            interface=self.view.settings.get_interface(),
            channel=self.view.settings.get_baudrate(),
            baudrate=self.view.settings.get_baudrate(),
        )
        if self.is_active():
            raise RuntimeError("App must be stopped before applying new settings")
        bus = can.Bus(**{k: v for k, v in user_settings.items() if v})  # type: ignore
        self.set_bus(bus)

    def settings_can_id_format_callback(self, sender, app_data, user_data) -> None:
        self.view.plot.set_format(self.view.settings.get_id_format())
        self.repopulate()