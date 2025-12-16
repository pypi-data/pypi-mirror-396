# type: ignore

from typing import Annotated, Any, Protocol, runtime_checkable

import bs4

from epublib.exceptions import EPUBError

# Reproducing the behavior of typing.Required
type Required[T] = Annotated[T, "required"]


class EnforcingSoup(bs4.BeautifulSoup):
    def __init__(
        self,
        markup: str | bytes,
        features: str | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(
            markup,
            features,
            *args,
            **kwargs,
        )

        required = (
            field
            for field, annotation in self.__class__.__annotations__.items()
            if annotation.__origin__ is Required
        )

        for tag in required:
            if not getattr(self, tag):
                raise EPUBError(f"Package document missing {tag}")


class PackageDocumentSoup(EnforcingSoup):
    """A BeautifulSoup subclass for the package document."""

    manifest: Required[bs4.Tag]
    metadata: Required[bs4.Tag]
    spine: Required[bs4.Tag]


class NCXSoup(EnforcingSoup):
    """A BeautifulSoup subclass for the NCX file."""

    ncx: Required[bs4.Tag]
    docTitle: Required[bs4.Tag]
    head: Required[bs4.Tag]
    navMap: Required[bs4.Tag]


@runtime_checkable
class WithSoupProtocol(Protocol):
    """A protocol for classes that have a BeautifulSoup attribute."""

    soup: bs4.BeautifulSoup
