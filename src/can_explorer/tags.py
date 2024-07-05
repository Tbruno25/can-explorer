import uuid
from dataclasses import dataclass


def generate_tag() -> int:
    """
    Generate a random, unique tag.
    """
    return hash(uuid.uuid4())


@dataclass(frozen=True, slots=True)
class Tag:
    """
    Creates tag reference instances for the view to utilize.

    Once instantiated the tag values cannot be modified.
    """

    header: int
    body: int
    footer: int
    main_button: int
    clear_button: int
    plot_buffer_slider: int
    plot_height_slider: int
    plot_tab: int
    settings_tab: int
    settings_interface: int
    settings_channel: int
    settings_baudrate: int
    settings_apply: int
    settings_id_format: int

    def __init__(self) -> None:
        for tag_name in self.__slots__:
            object.__setattr__(self, tag_name, generate_tag())
