from enum import Enum, auto, unique
from typing import Final

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
    TABLE_COLUMN_1_WIDTH: Final = 15
    TABLE_COLUMN_2_WIDTH: Final = 85
    TITLE: Final = "CAN Explorer"
    FONT: Final = RESOURCES_DIR / "Inter-Medium.ttf"
    FOOTER_OFFSET: Final = 50 if HOST_OS == "linux" else 85


class Font:
    DEFAULT: int
    LABEL: int


class Theme:
    DEFAULT: int
    LIGHT: int


@unique
class Tag(str, Enum):
    HEADER = auto()
    BODY = auto()
    FOOTER = auto()
    MAIN_BUTTON = auto()
    CLEAR_BUTTON = auto()
    TAB_VIEWER = auto()
    TAB_SETTINGS = auto()
    SETTINGS_PLOT_BUFFER = auto()
    SETTINGS_PLOT_HEIGHT = auto()
    SETTINGS_INTERFACE = auto()
    SETTINGS_CHANNEL = auto()
    SETTINGS_BAUDRATE = auto()
    SETTINGS_APPLY = auto()
    SETTINGS_ID_FORMAT = auto()
