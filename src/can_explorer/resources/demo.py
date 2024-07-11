import contextlib
import sys
import threading
import time
from pathlib import Path

import can.player

from can_explorer import CanExplorer

LOG_FILE = Path(__file__).parent / "ic_sim.log"
INTERFACE = "virtual"
CHANNEL = "demo"


def demo_config(app: CanExplorer) -> None:
    app.controller.view.settings.set_interface_options(iterable=[""], default=INTERFACE)
    app.controller.view.settings.set_channel(channel=CHANNEL)
    app.controller.settings_apply_button_callback()

    # Play simulated logfile
    sys.argv = [sys.argv[0], "-i", INTERFACE, "-c", CHANNEL, str(LOG_FILE)]
    with contextlib.redirect_stdout(None):
        threading.Thread(target=can.player.main, daemon=True).start()
        time.sleep(0.1)  # Allow time for thread to start and stdout to be swallowed
