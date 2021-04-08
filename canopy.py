from PyQt5.QtWidgets import QApplication, QScrollArea
from pyqtgraph.Qt import QtCore, QtGui
from collections import defaultdict, deque
from random import randint
import pyqtgraph as pg
import can


bus_type = "socketcan"
channel = "vcan0"
baud = 500_000
buffer_len = 250


class Listener(can.Listener):
    recorded = defaultdict(lambda: deque([0] * buffer_len, maxlen=buffer_len))

    def on_message_received(self, msg):
        val = int.from_bytes(msg.data, byteorder="big")
        self.recorded[msg.arbitration_id].append(val)


class CanoPy:
    def __init__(self, rate=0.05):
        # CAN
        self.bus = can.interface.Bus(bustype=bus_type, channel=channel, bitrate=baud)
        self.listener = Listener()
        self.notifier = can.Notifier(self.bus, [self.listener])
        self.messages = self.listener.recorded

        # Application
        self.app = QApplication([])
        self.layout = pg.GraphicsLayoutWidget()
        self.layout.keyPressEvent = self.key_pressed
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.layout)
        self.scroll.setWindowTitle("CanoPy")
        self.scroll.show()

        # Plotting
        self.x = list(range(buffer_len))
        self.plots = {}
        self.obj = []
        self.ignore = []
        self.plt_height = 75

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(int(rate * 1000))

    def rand_pen(self):
        r, g, b = [randint(0, 255) for _ in range(3)]
        return pg.mkPen(color=(r, g, b), width=2)

    def key_pressed(self, event):
        if event.key() == ord("I"):
            self.ignore_current()

    def add_plot(self, id_):
        plt = self.layout.addPlot(row=len(self.plots), col=0, height=self.plt_height)
        plt.addLegend()
        plt.hideAxis("left")
        plt.hideAxis("bottom")
        self.obj.append(plt)
        self.plots[id_] = plt.plot(name=hex(id_), pen=self.rand_pen())
        # adjusts scrollwheel
        self.layout.setFixedHeight(self.plt_height * (len(self.obj) + 1))

    def update(self):
        current = dict(self.messages)
        for id_, data in current.items():
            if id_ in self.ignore:
                continue
            if id_ not in self.plots:
                self.add_plot(id_)
            self.plots[id_].setData(self.x, data)

    def ignore_current(self):
        self.ignore += list(self.messages)
        for plt in self.obj:
            self.layout.removeItem(plt)
        self.obj.clear()

    def run(self):
        self.app.exec_()


if __name__ == "__main__":
    canopy = CanoPy()
    canopy.run()