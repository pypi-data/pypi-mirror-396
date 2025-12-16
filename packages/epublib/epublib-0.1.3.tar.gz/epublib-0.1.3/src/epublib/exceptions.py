import warnings
from typing import Self


class EPUBWarning(Warning):
    """Base warning for EPUBLib."""


class EPUBError(Exception):
    """Base error for EPUBLib."""

    @classmethod
    def missing_ncx(cls, calling: object, method: str, arg: str = "reset_ncx") -> Self:
        return cls(
            f"'{calling.__class__.__name__}.{method}' received '{arg}=True' "
            "but there is no NCX file in the book. Create the NCX "
            f"file with '{calling.__class__.__name__}.create_ncx' or use "
            f"a falsy value for the '{arg}' parameter"
        )


class NotEPUBError(EPUBError):
    """The file is not an EPUB file."""

    def __init__(self, msg: str, *args: object) -> None:
        super().__init__(f"File is not epub: {msg}", *args)


class ClosedEPUBError(EPUBError):
    """An operation was attempted on a closed EPUB file."""


def warn(warning: str, cls: type[EPUBWarning] = EPUBWarning) -> None:
    """
    Utility function to issue an EPUBLib warning.

    Args:
        warning: The warning message.
        cls: The warning class to use. Defaults to EPUBWarning.
    """
    warnings.warn(warning, cls)
