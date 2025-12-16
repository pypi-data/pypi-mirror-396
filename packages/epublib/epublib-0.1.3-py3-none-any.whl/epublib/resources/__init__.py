import io
from pathlib import Path
from typing import IO, Protocol, Self, override, runtime_checkable
from zipfile import ZipInfo

import bs4

from epublib.exceptions import ClosedEPUBError, EPUBError
from epublib.media_type import Category, MediaType
from epublib.source import zip_info_now
from epublib.util import strip_fragment


def info_to_zipinfo(info: ZipInfo | str | Path) -> ZipInfo:
    if isinstance(info, ZipInfo):
        return info

    return ZipInfo(filename=str(strip_fragment(info)), date_time=zip_info_now())


@runtime_checkable
class SoupChanging(Protocol):
    @property
    def soup(self) -> bs4.BeautifulSoup: ...

    def on_soup_change(self) -> None:
        """
        Trigger reparsing of the internal representations of the resource. Used
        after the soup is modified directly.
        """


class Resource:
    """
    Base class for all resources (i.e. files) in an EPUB file.

    >>> resource = Resource(b"Hello, world!", "misc/hello.txt")
    >>> resource.filename
    'misc/hello.txt'
    >>> resource.content
    b'Hello, world!'

    Args:
        file: A file-like object or bytes containing the resource data.
        info: A ZipInfo object or a string/Path representing the location
            of the resource in the EPUB archive.
    """

    def __init__(self, file: IO[bytes] | bytes, info: ZipInfo | str | Path) -> None:
        self.zipinfo: ZipInfo = info_to_zipinfo(info)
        self._file: IO[bytes] = io.BytesIO(file) if isinstance(file, bytes) else file
        self._content: bytes | None = None

    @classmethod
    def from_path(cls, filename: str | Path, info: str | Path | ZipInfo) -> Self:
        """
        Create a Resource from a file on disk.

        Args:
            filename: The path to the file on disk.
            info: A ZipInfo object or a string/Path representing the location
                of the resource in the EPUB archive.
        """
        file = open(filename, "rb")
        if not isinstance(info, ZipInfo):
            info = ZipInfo.from_file(filename, info, strict_timestamps=False)
        return cls(file, info)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.filename})"

    def on_content_change(self) -> None:
        """Hook called when the content of this resource changes."""

    @property
    def filename(self) -> str:
        """
        The absolute path to this resource in the EPUB archive. When setting,
        any fragment will be removed.
        """
        return self.zipinfo.filename

    @filename.setter
    def filename(self, value: str) -> None:
        self._set_filename(value)

    def _set_filename(self, value: str) -> None:
        self.zipinfo.filename = strip_fragment(value)

    def get_content(self, cache: bool = True) -> bytes:
        """
        Get the content of this resource. If this content hasn't been
        cached yet and `cache` is False, the content will be read
        directly from the underlying file without storing it in memory.

        Args:
            cache: Whether to cache the content in memory for future access.
            Defaults to True.

        Raises:
            ClosedEPUBError: If this resource has been closed.
        """

        self.check_closed()
        content = self._content
        if content is None:
            content = self._file.read()
            __ = self._file.seek(0)
            if cache:
                self._content = content

        return content

    @property
    def content(self) -> bytes:
        """
        The contents of this resource.

        Raises:
            ClosedEPUBError: When getting the content, if this resource has been
                closed.
        """

        return self.get_content()

    @content.setter
    def content(self, value: bytes) -> None:
        self.check_closed()
        self._set_content(value)

    def _set_content(self, value: bytes, content_change: bool = True) -> None:
        self._content = value
        if content_change:
            self.on_content_change()

    def get_title(self) -> str:
        """
        Get a human-readable title for this resource.
        """
        return self.filename

    @property
    def closed(self) -> bool:
        """Whether this resource has been closed."""
        return self._file.closed

    def check_closed(self) -> None:
        """
        Raise an error if this resource has been closed.

        Raises:
            ClosedEPUBError: If this resource has been closed.
        """
        if self.closed:
            raise ClosedEPUBError(f"Using resource {self.filename} after closing")

    def close(self) -> None:
        """Close this resource and free any associated resources."""
        del self._content
        self._content = None
        self._file.close()


class XMLResource[S: bs4.BeautifulSoup = bs4.BeautifulSoup](Resource):
    """
    A resource that is an XML file. Provides a `soup` property that contains a
    BeautifulSoup representation of the XML content.

    Args:
        file: A file-like object or bytes containing the resource data.
        info: A ZipInfo object or a string/Path representing the location
            of the resource in the EPUB archive.
    """

    soup_class: type[S] = bs4.BeautifulSoup  # type: ignore[reportAssignmentType]

    def __init__(self, file: IO[bytes] | bytes, info: ZipInfo | str | Path) -> None:
        super().__init__(file, info)
        self._soup: None | S = None

    @property
    def soup(self) -> S:
        """
        A BeautifulSoup representation of the XML content of this resource.
        """
        if self._soup is None:
            self._soup = self.soup_class(self.content, "xml")
        return self._soup

    @soup.setter
    def soup(self, value: S) -> None:
        self._set_soup(value)

    def _set_soup(self, value: S) -> None:
        self._soup = value

    @override
    def get_content(self, cache: bool = True) -> bytes:
        if self._soup is not None:
            self._set_content(self._soup.encode(), content_change=False)
        return super().get_content()

    @override
    def on_content_change(self) -> None:
        super().on_content_change()
        del self._soup
        self._soup = None

    @override
    def get_title(self) -> str:
        if self.soup.title and self.soup.title.string:
            return self.soup.title.string
        return super().get_title()


class PublicationResource(Resource):
    """
    A resource that contributes to the logic and rendering of the publication.

    This includes resources like the package document, content documents (XHTML),
    CSS stylesheets, audio, video, images, fonts, and scripts.

    This class provides the `media_type` attribute.

    Args:
        file: A file-like object or bytes containing the resource data.
        info: A ZipInfo object or a string/Path representing the location
            of the resource in the EPUB archive.
        media_type: The media type of this resource. If not provided, it will be
            guessed based on the filename.

    Raises:
        EPUBError: If the media type is not provided and cannot be determined
            from the filename.
    """

    def __init__(
        self,
        file: IO[bytes] | bytes,
        info: ZipInfo | str | Path,
        media_type: MediaType | str | None = None,
    ) -> None:
        super().__init__(file, info)
        if media_type is None:
            media_type = MediaType.from_filename(self.zipinfo.filename)
            if media_type is None:
                raise EPUBError(
                    f"Cannot determine media type of {self.zipinfo.filename}"
                )

        self.media_type: MediaType = MediaType(media_type)

    @classmethod
    @override
    def from_path(
        cls,
        filename: str | Path,
        info: str | Path | ZipInfo,
        media_type: MediaType | str | None = None,
    ):
        """
        Create a PublicationResource from a file on disk.

        Args:
            filename: The path to the file on disk.
            info: A ZipInfo object or a string/Path representing the location
                of the resource in the EPUB archive.
            media_type: The media type of this resource. If not provided, it
                will be guessed based on the filename.

        Raises:
            EPUBError: If the media type is not provided and cannot be
                determined from the filename.
        """
        instance = super().from_path(filename, info)

        if media_type is not None:
            instance.media_type = MediaType(media_type)

        return instance

    @property
    def is_foreign(self) -> bool:
        """
        Whether this resource is a foreign resource.
        """
        return self.media_type.category is Category.FOREIGN

    @property
    def category(self) -> Category:
        """
        The category of the media type of this resource.
        """
        return self.media_type.category

    @classmethod
    def from_resource(
        cls,
        other: Resource,
        media_type: MediaType | str | None = None,
    ) -> Self:
        """
        Create a PublicationResource from another Resource.

        Args:
            other: The resource to copy.
            media_type: The media type of the new resource. If not provided, it
                will be guessed based on the filename of the given resource.

        Raises:
            EPUBError: If the media type is not provided and cannot be
                determined from the filename of the given resource.
            ClosedEPUBError: If the given resource has been closed.
        """
        if other.closed:
            raise ClosedEPUBError(f"Using resource {other} after closing")

        return cls(other._file, other.zipinfo, media_type)


class ContentDocument[S: bs4.BeautifulSoup = bs4.BeautifulSoup](  # type: ignore[reportUnsafeMultipleInheritance]
    PublicationResource,
    XMLResource[S],
):
    """
    A publication resource that is either a XHTML or an SVG file.

    Args:
        file: A file-like object or bytes containing the resource data.
        info: A ZipInfo object or a string/Path representing the location
            of the resource in the EPUB archive.
        media_type: The media type of this resource. If not provided, it will be
            guessed based on the filename. Must be either `MediaType.XHTML`
            (`application/xhtml+xml`) or `MediaType.SVG` (`image/svg+xml`).
    """

    @override
    def get_title(self) -> str:
        if self.soup.h1 and self.soup.h1.string:
            return self.soup.h1.string

        if self.soup.title and self.soup.title.string:
            return self.soup.title.string

        if self.soup.body:
            string = self.soup.body.find(string=True)
        else:
            string = self.soup.find(string=True)

        if string:
            return string

        return ""
