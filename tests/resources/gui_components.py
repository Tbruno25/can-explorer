import pathlib

GUI_IMAGES = pathlib.Path(__file__).parent / "images"


class Gui:
    class Acceptance:
        VISUALIZES_TRAFFIC = str(GUI_IMAGES / "acceptance_visualizes_traffic.png")

    class Tab:
        SETTINGS = str(GUI_IMAGES / "settings_tab.png")
        VIEWER = str(GUI_IMAGES / "viewer_tab.png")

    class Button:
        APPLY = str(GUI_IMAGES / "apply_button.png")
        CLEAR = str(GUI_IMAGES / "clear_button.png")
        START = str(GUI_IMAGES / "start_button.png")

    class Input:
        CHANNEL = str(GUI_IMAGES / "channel_box.png")
        INTERFACE = str(GUI_IMAGES / "interface_box.png")
        UDP_MULTICAST = str(GUI_IMAGES / "udp_multicast.png")
        VIRTUAL = str(GUI_IMAGES / "virtual.png")
