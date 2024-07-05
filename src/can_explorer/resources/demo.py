import sys
import threading
from pathlib import Path

import can.player

from can_explorer import CanExplorer

DEMO_FILE = Path(__file__).parent / "ic_sim.log"


def demo_config(app: CanExplorer) -> None:
    # Use the virtual interface as default
    app.controller.view.settings.set_interface_options(iterable=[""], default="virtual")

    # Simulate the apply button press
    app.controller.settings_apply_button_callback(None, None, None)

    # Play simulated logfile
    sys.argv = [sys.argv[0], "-i", "virtual", str(DEMO_FILE)]
    threading.Thread(target=can.player.main, daemon=True).start()
