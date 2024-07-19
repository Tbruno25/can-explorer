from typing import Final

from can.interfaces import VALID_INTERFACES

from can_explorer.resources import DIR_PATH as RESOURCES_DIR
from can_explorer.resources import HOST_OS


class Default:
    WIDTH: Final = 600
    HEIGHT: Final = 600
    REFRESH_RATE: Final = 0.05
    BACKGROUND: Final = (50, 50, 50, 255)
    FONT_HEIGHT: Final = 14
    PLOT_HEIGHT: Final = 100
    PLOT_HEIGHT_MAX: Final = 500
    BUFFER_MIN: Final = 50
    BUFFER_MAX: Final = 2500
    BUFFER_SIZE: Final = 100
    ID_FORMAT: Final = hex
    LABEL_COLUMN_WIDTH: Final = 15
    PLOT_COLUMN_WIDTH: Final = 85
    TITLE: Final = "CAN Explorer"
    FONT: Final = RESOURCES_DIR / "Inter-Medium.ttf"
    FOOTER_OFFSET: Final = 50 if HOST_OS == "linux" else 85


class CANBus:
    INTERFACES: Final = sorted(list(VALID_INTERFACES))
    _BAUDRATES = [33_333, 125_000, 250_000, 500_000, 1_000_000]
    BAUDRATES: Final = [format(i, "_d") for i in _BAUDRATES]
