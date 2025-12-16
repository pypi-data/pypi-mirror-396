import sys
from typing import final

from snipstr.base import (
    BuilderSnipStr,
    ComparableSnipStr,
    HashedSnipStr,
)
from snipstr.enums import Sides
from snipstr.errors import (
    SnipSideError,
    SnipSizeIsNotIntError,
    SnipSizeIsNotPositiveIntError,
)
from snipstr.types import PositiveInt

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@final
class SnipStr(ComparableSnipStr, HashedSnipStr, BuilderSnipStr):
    """String truncation class with fluent interface.

    Example:
        >>> from snipstr import SnipStr
        >>> text = 'Python is an interpreted programming language.'
        >>> s = SnipStr(text)
        >>> s.snip_to(16).by_side('right').with_replacement_symbol()
        >>> str(s)  # 'Python is an ...'
    """

    __slots__ = (
        '_lenght',
        '_replacement_symbol',
        '_side',
        '_source',
    )

    def snip_to(self, size: PositiveInt, /) -> Self:
        """Set the target size for the snipped string.

        Args:
            size: The maximum length of the resulting string.

        Returns:
            Self: The instance for method chaining.

        Raises:
            SnipSizeIsNotIntError: If size is not an integer.
            SnipSizeIsNotPositiveIntError: If size is not positive.
        """
        if not isinstance(size, int):
            raise SnipSizeIsNotIntError(size)
        if size <= 0:
            raise SnipSizeIsNotPositiveIntError(size)

        self._lenght = size

        return self

    def by_side(self, side: Sides | str, /) -> Self:
        """Set the side from which the string will be truncated.

        Args:
            side: The side to truncate from.

        Returns:
            Self: The instance for method chaining.

        Raises:
            SnipSideError: If side is not a valid Sides value.
        """
        if isinstance(side, str) and side in Sides.get_values():
            self._side = side
        elif isinstance(side, Sides) and side in Sides:
            self._side = side.value
        else:
            raise SnipSideError(side)

        return self

    def with_replacement_symbol(
        self,
        symbol: str | None = None,
        /,
    ) -> Self:
        """Set the replacement symbol to indicate truncation.

        Args:
            symbol: The symbol to use. Defaults to '...' if None.

        Returns:
            Self: The instance for method chaining.
        """
        default = '...'
        symbol = default if symbol is None else str(symbol)

        self._replacement_symbol = symbol

        return self

    def __len__(self) -> int:
        return self._lenght

    def __str__(self) -> str:
        return self._build(str(self._source))
