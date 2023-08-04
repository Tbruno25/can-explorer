import pathlib

from can_explorer.resources import HOST_OS

IMG_PATH = pathlib.Path(__file__).parent / "images" / HOST_OS


class Gui:
    class Acceptance:
        VISUALIZES_TRAFFIC = str(IMG_PATH / "acceptance_visualizes_traffic.png")

    class Tab:
        SETTINGS = str(IMG_PATH / "settings_tab.png")
        VIEWER = str(IMG_PATH / "viewer_tab.png")

    class Button:
        APPLY = str(IMG_PATH / "apply_button.png")
        CLEAR = str(IMG_PATH / "clear_button.png")
        START = str(IMG_PATH / "start_button.png")

    class Input:
        CHANNEL = str(IMG_PATH / "channel_box.png")
        INTERFACE = str(IMG_PATH / "interface_box.png")
        UDP_MULTICAST = str(IMG_PATH / "udp_multicast.png")
        VIRTUAL = str(IMG_PATH / "virtual.png")
