class SnipSizeIsNotIntError(TypeError):
    """Raised when the snip size parameter is not an integer.

    This exception is raised when a value passed as the size parameter
    for string snipping is not of type int.

    Args:
        size: The value that was provided instead of an integer.
    """

    def __init__(self, size: object, /) -> None:
        msg = (
            'You must specify int for snip size. Value of `{0}` is not suitable'
        )
        super().__init__(msg.format(size))


class SnipSizeIsNotPositiveIntError(ValueError):
    """Raised when the snip size parameter is not a positive integer.

    This exception is raised when an integer value passed as the size
    parameter for string snipping is zero or negative.

    Args:
        size: The non-positive integer value that was provided.
    """

    def __init__(self, size: object, /) -> None:
        msg = (
            'You must specify positive number for snip size. '
            'Value of `{0}` is not suitable'
        )
        super().__init__(msg.format(size))


class SnipSideError(ValueError):
    """Raised when the snip side parameter has an invalid value.

    This exception is raised when a value passed as the side parameter
    for string snipping is not 'left' or 'right'.

    Args:
        side: The invalid value that was provided instead of 'left' or 'right'.
    """

    def __init__(self, side: object, /) -> None:
        msg = (
            'The side can only be the values of `left` or `right`. '
            'Value of `{0}` is not suitable'
        )
        super().__init__(msg.format(side))
