import pathlib
import platform
import uuid
from typing import Any, Final

DIR_PATH: Final = pathlib.Path(__file__).parent

HOST_OS: Final = platform.system().lower()


def frozen(value: Any) -> property:
    """
    Helper function to create an inline property.

    Args:
        value (Any)

    Returns:
        property
    """
    return property(fget=lambda _: value)


def generate_tag() -> int:
    """
    Generate a random, unique tag.
    """
    return hash(uuid.uuid4())


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
