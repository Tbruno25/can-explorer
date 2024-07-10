import pathlib
import platform
import threading
from typing import Any, Final

import can

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


class StoppableThread(threading.Thread):
    """
    Basic thread that can be stopped during long running loops.

    StoppableThread.cancel should be used as the while loop flag.

    threading.current_thread can be used to access the thread from
    within the target function.

    Excample:

        while not current_thread().cancel.wait(1):
            ...

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancel = threading.Event()

    def stop(self):
        self.cancel.set()
        self.join()
