from collections import defaultdict

import can


class Listener(can.Listener):
    def __init__(self, buffer: defaultdict, *args, **kwargs):
        self.buffer = buffer
        super().__init__(*args, **kwargs)

    def on_message_received(self, msg):
        val = int.from_bytes(msg.data, byteorder="big")
        self.buffer[msg.arbitration_id].append(val)
