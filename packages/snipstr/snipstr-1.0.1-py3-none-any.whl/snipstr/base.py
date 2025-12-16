import sys
from abc import ABC, abstractmethod

from snipstr.enums import Sides
from snipstr.types import PositiveInt

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class AbstractSnipStr(ABC):
    """Abstract base class for string snipping operations.

    This class defines the contract that all SnipStr implementations
    must follow. It provides abstract methods for configuring and
    executing string truncation.
    """

    @abstractmethod
    def snip_to(self, size: PositiveInt, /) -> Self:
        """Set the target size for the snipped string.

        Args:
            size: The maximum length of the resulting string.
                  Must be a positive integer.

        Returns:
            Self: The instance for method chaining.
        """

    @abstractmethod
    def by_side(self, side: Sides | str, /) -> Self:
        """Set the side from which the string will be truncated.

        Args:
            side: The side to truncate from.
                  Can be a Sides enum value or string.

        Returns:
            Self: The instance for method chaining.
        """

    @abstractmethod
    def with_replacement_symbol(
        self,
        symbol: str | None = None,
        /,
    ) -> Self:
        """Set the replacement symbol to indicate truncation.

        Args:
            symbol: The symbol to append/prepend at the truncation point.
                    Defaults to None (no replacement symbol).

        Returns:
            Self: The instance for method chaining.
        """

    @property
    @abstractmethod
    def source(self) -> object:
        """Return the original source object.

        Returns:
            object: The original object that was passed for snipping.
        """


class BaseSnipStr(AbstractSnipStr):
    """Base implementation of the string snipping functionality.

    This class provides the foundational implementation for storing and managing
    the source object, length, side, and replacement symbol settings.

    Attributes:
        _source: The original source object to be snipped.
        _lenght: The target length for the snipped string.
        _side: The side from which to truncate (left or right).
        _replacement_symbol: The symbol to indicate truncation.
    """

    def __init__(self, source: object) -> None:
        self._source = source
        self._lenght = len(str(source))
        self._side = Sides.RIGHT.value
        self._replacement_symbol = ''

    @property
    def source(self) -> object:
        """Return the original source object.

        Returns:
            object: The original object that was passed for snipping.
        """
        return self._source

    def __repr__(self) -> str:
        maximum_text_length = 30
        if (
            isinstance(self._source, str)
            and len(self._source) > maximum_text_length
        ):
            beginning_of_source = self._source[:10]
            end_of_source = self._source[-10:]
            source = f'{beginning_of_source} <...> {end_of_source}'
        else:
            source = str(self._source)

        msg = (
            '{name}(source={source}, '
            'length={length}, '
            'side={side}, '
            'replacement_symbol={symbol})'
        )

        return msg.format(
            source=source,
            name=self.__class__.__name__,
            length=self._lenght,
            side=self._side,
            symbol=(
                self._replacement_symbol if self._replacement_symbol else None,
            ),
        )


class ComparableSnipStr(BaseSnipStr):
    """SnipStr with comparison operations based on length.

    This class extends BaseSnipStr with rich comparison methods that compare
    instances based on their target length values.
    """

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self._lenght < other._lenght

    def __le__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self._lenght <= other._lenght

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self._lenght > other._lenght

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self._lenght >= other._lenght


class HashedSnipStr(BaseSnipStr):
    """SnipStr with hashing and equality support.

    This class extends BaseSnipStr with hash and equality implementations,
    making instances usable as dictionary keys and in sets. Hash and equality
    are computed based on all attributes defined in __slots__.
    """

    def __hash__(self) -> int:
        attrs = tuple(  # type: ignore[var-annotated]
            getattr(self, attr) for attr in self.__slots__
        )

        return hash(attrs)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return all(  # type: ignore[var-annotated]
            getattr(self, attr) == getattr(other, attr)
            for attr in self.__slots__
        )


class BuilderSnipStr(BaseSnipStr):
    """SnipStr with string building capabilities.

    This class extends BaseSnipStr with methods to build the final snipped
    string by applying truncation and replacement symbol operations.
    """

    def _build(self, current: str) -> str:
        current = str(current)
        current = self._cut_back(current)

        return self._add_replacement_symbol(current)

    def _cut_back(self, current: str) -> str:
        if self._side == Sides.RIGHT.value:
            current = current[: self._lenght]
        elif self._side == Sides.LEFT.value:
            current = current[-self._lenght :]

        return current

    def _add_replacement_symbol(self, current: str) -> str:
        if self._replacement_symbol:
            symbol_lenght = len(self._replacement_symbol)
            if self._side == Sides.RIGHT.value:
                current = current[:-symbol_lenght] + self._replacement_symbol
            elif self._side == Sides.LEFT.value:
                current = self._replacement_symbol + current[symbol_lenght:]

        return current
