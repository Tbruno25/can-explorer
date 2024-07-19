import pathlib
import platform
import threading
from random import randint
from typing import Any, Final

from can import Message

DIR_PATH: Final = pathlib.Path(__file__).parent

HOST_OS: Final = platform.system().lower()


def generate_random_can_message() -> Message:
    """
    Generate a random CAN message.
    """
    message_id = randint(1, 25)
    data_length = randint(1, 8)
    data = (randint(0, 255) for _ in range(data_length))
    return Message(arbitration_id=message_id, data=data)


class Percentage:
    @staticmethod
    def get(n1: float, n2: float) -> int:
        """
        Calculate the percentage n1 is of n2.

        Args:
            n1 (float)
            maximum (float)

        Returns:
            int: Percentage
        """
        return int(100 * n1 / n2)

    @staticmethod
    def reverse(percentage: float, total: float) -> int:
        """
        Calculate the original value from a percentage.

        Args:
            percentage (float)
            total (float):

        Returns:
            int: Original value
        """
        return int((percentage * total) / 100.0)
