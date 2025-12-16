import enum


@enum.unique
class Sides(enum.Enum):
    """Enum representing the side from which to truncate a string."""

    LEFT = 'left'
    RIGHT = 'right'

    @classmethod
    def get_values(cls: type['Sides']) -> tuple[str, ...]:
        """Return all possible side values.

        Returns:
            tuple[str, ...]: A tuple of all side values as strings.
        """
        return tuple(side.value for side in cls)
