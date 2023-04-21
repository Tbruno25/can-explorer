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
