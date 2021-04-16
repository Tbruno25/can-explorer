from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QMainWindow,
)
from pyqtgraph.Qt import QtCore, QtGui
from collections import defaultdict, deque
from functools import partial
from random import randint
import pyqtgraph as pg
import can

import config as cf


class Listener(can.Listener):
    def __init__(self, buffer: defaultdict, *args, **kwargs):
        self.buffer = buffer
        super().__init__()

    def on_message_received(self, msg):
        val = int.from_bytes(msg.data, byteorder="big")
        self.buffer[msg.arbitration_id].append(val)


class PlotWidget(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setMenuEnabled(False)
        self.setMouseEnabled(x=False, y=False)
        self.hideAxis("left")
        self.hideAxis("bottom")
        self.addLegend()
        self.setFixedHeight(75)


class CanoPy:
    def __init__(self, rate=0.05, buffer_length=200):
        # Buffer
        self.buf_len = buffer_length
        self.buf_int = 0.1
        self.buf_max = 2500
        self.buffer = defaultdict(
            lambda: deque([0] * self.buf_len, maxlen=self.buf_len)
        )

        # CAN
        self.bus = can.interface.Bus(
            interface=cf.interface,
            channel=cf.channel,
            bitrate=cf.bitrate,
        )
        self.listener = Listener(self.buffer)
        self.notifier = can.Notifier(self.bus, [self.listener])

        # Application
        self.app = QApplication([])
        self.window = QWidget()
        self.layout = QGridLayout()
        self.window.setLayout(self.layout)
        self.layout.keyPressEvent = self.key_pressed
        # self.scroll = QScrollArea()
        # self.scroll.setWidgetResizable(True)
        # self.scroll.setWidget(self.window)
        # self.scroll.setWindowTitle("CanoPy")
        self.window.show()

        # Key Actions
        self.key_actions = {
            ord("I"): self.ignore_current,
            QtCore.Qt.Key_Up: partial(self.scale_buffer_size, True),
            QtCore.Qt.Key_Down: partial(self.scale_buffer_size, False),
        }

        # Plotting
        self.set_x_axis()
        self.plots = {}
        self.obj = []
        self.ignore = []
        self.plt_height = 75

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(int(rate * 1000))

    def key_pressed(self, event):
        key = event.key()
        try:
            self.key_actions.get(key)()
        except TypeError:
            pass

    def set_x_axis(self):
        self.x = list(range(self.buf_len))
        return

    def add_plot(self, id_):
        plt = PlotWidget()
        self.obj.append(plt)
        self.plots[id_] = plt.plot(name=hex(id_), pen=self.rand_pen())
        self.layout.addWidget(plt, len(self.plots), 1)
        # adjusts scrollwheel
        # self.layout.setFixedHeight(self.plt_height * (len(self.obj) + 1))
        return

    def update_plots(self):
        current = dict(self.buffer)
        for id_, data in current.items():
            if id_ in self.ignore:
                continue
            if id_ not in self.plots:
                self.add_plot(id_)
            self.plots[id_].setData(self.x, data)
        return

    def rand_pen(self):
        r, g, b = [randint(0, 255) for _ in range(3)]
        return pg.mkPen(color=(r, g, b), width=2)

    def ignore_current(self):
        self.ignore += list(self.buffer)
        for plt in self.obj:
            self.layout.removeItem(plt)
        self.obj.clear()
        return

    def scale_buffer_size(self, increase: bool):
        prod = int(self.buf_len * self.buf_int)
        val = prod if increase else -prod
        new_len = self.buf_len + val
        if 10 < new_len < self.buf_max:
            self.buf_len = new_len
            self.update_buffer()
        return

    def update_buffer(self):
        if len(self.x) != self.buf_len:
            self.set_x_axis()
            for id_, data in self.buffer.items():
                if data.maxlen != self.buf_len:
                    new_buf = deque(data, maxlen=self.buf_len)
                    current_len = len(new_buf)
                    if current_len != self.buf_len:
                        difference = [new_buf[0]] * (self.buf_len - current_len)
                        new_buf.extendleft(difference)
                    self.buffer[id_] = new_buf
        return

    def run(self):
        self.app.exec_()


if __name__ == "__main__":
    canopy = CanoPy()
    canopy.run()