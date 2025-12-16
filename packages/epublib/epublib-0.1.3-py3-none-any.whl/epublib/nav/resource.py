from pathlib import Path
from typing import IO, override
from zipfile import ZipInfo

from epublib.exceptions import EPUBError
from epublib.media_type import MediaType
from epublib.nav import LandmarksRoot, PageListRoot, TocRoot
from epublib.nav.util import LandmarkEntryData, PageBreakData, TOCEntryData
from epublib.resources import ContentDocument, SoupChanging


class NavigationDocument(ContentDocument, SoupChanging):
    """
    A specialization of the XHTML content document that contains human- and
    machine-readable global navigation information.

    Typical usage is from an `EPUB` instance:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     book.reset_toc()
    ...     toc_title = book.nav.toc.title
    ...     refs = book.nav.toc.items_referencing("Text/chapter1.xhtml")
    >>> toc_title
    'Table of Contents'
    >>> len(list(refs))
    2

    Args:
        file: A file-like object or bytes containing the navigation document.
        info: The `ZipInfo` or filename of the navigation document in the EPUB
            archive.
        media_type: The media type of the navigation document, typically
            `application/xhtml+xml`.
    """

    def __init__(
        self,
        file: IO[bytes] | bytes,
        info: ZipInfo | str | Path,
        media_type: MediaType,
    ) -> None:
        super().__init__(file, info, media_type)
        self._toc: TocRoot | None = None
        self._page_list: PageListRoot | None = None
        self._landmarks: LandmarksRoot | None = None

    @property
    def toc(self) -> TocRoot:
        """The table of contents in the navigation document."""
        if self._toc is None:
            tag = self.soup.select_one('nav[epub|type="toc"]')
            if tag:
                self._toc = TocRoot.from_tag(self.soup, tag, own_filename=self.filename)
        if not self._toc:
            raise EPUBError("No TOC found in navigation document")
        return self._toc

    @property
    def page_list(self) -> PageListRoot | None:
        """The page list in the navigation document, if any."""
        if self._page_list is None:
            tag = self.soup.select_one('nav[epub|type="page-list"]')
            if tag:
                self._page_list = PageListRoot.from_tag(
                    self.soup,
                    tag,
                    own_filename=self.filename,
                )
        return self._page_list

    @property
    def landmarks(self) -> LandmarksRoot | None:
        """The landmarks in the navigation document, if any."""
        if self._landmarks is None:
            tag = self.soup.select_one('nav[epub|type="landmarks"]')
            if tag:
                self._landmarks = LandmarksRoot.from_tag(
                    self.soup,
                    tag,
                    own_filename=self.filename,
                )
        return self._landmarks

    def reset_toc(self, entries: list[TOCEntryData]) -> None:
        """
        Reset the table of contents in the navigation document to the given
        entries. Will replace any existing table of contents.

        Typically used indirectly from an EPUB instance with the `reset_toc` or
        `create_toc` methods.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     book.reset_toc(title = "New table of Contents")
        ...     toc_title = book.nav.toc.title
        >>> toc_title
        'New table of Contents'

        Args:
            entries: A list of `TOCEntryData` instances representing the
                entries to include in the table of contents.
        """
        try:
            _ = self.toc
        except EPUBError:
            self._toc = TocRoot(self.soup, own_filename=self.filename)
            self._toc.insert_self_in_soup()

        self.toc.reset(entries)

    def reset_page_list(self, pagebreaks: list[PageBreakData]) -> None:
        """
        Reset the page list in the navigation document to the given pagebreaks.
        Will replace any existing page list.

        Typically used indirectly from an EPUB instance with the
        `reset_page_list` or `create_page_list` methods.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     book.reset_page_list()
        ...     tag = book.nav.page_list.tag
        >>> tag
        <nav epub:type="page-list" ...


        Args:
            pagebreaks: A list of `PageBreakData` instances representing the
                pagebreaks to include in the page list.
        """

        if self.page_list is None:
            self._page_list = PageListRoot(
                self.soup,
                own_filename=self.filename,
            )
            self._page_list.insert_self_in_soup()

        assert self.page_list
        self.page_list.reset(pagebreaks)

    def reset_landmarks(self, entries: list[LandmarkEntryData]) -> None:
        """
        Reset the landmarks in the navigation document to the given entries.
        Will replace any existing landmarks.

        Typically used indirectly from an EPUB instance with the
        `reset_landmarks` or `create_landmarks` methods.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     book.reset_landmarks(targets_selector='#cover, #toc')
        ...     tag = book.nav.landmarks.tag
        >>> tag
        <nav epub:type="landmarks" ...

        Args:
            entries: A list of `LandmarkEntryData` instances representing the
                landmarks to include in the landmarks.
        """
        if self.landmarks is None:
            self._landmarks = LandmarksRoot(
                self.soup,
                own_filename=self.filename,
            )
            self._landmarks.insert_self_in_soup()

        assert self.landmarks
        self.landmarks.reset(entries)

    def remove(self, filename: str | Path) -> None:
        """
        Remove all references to the given filename from the navigation document

        Args:
            filename: The filename to remove references to.
        """
        if self.toc:
            self.toc.remove_nodes(str(filename))
        if self.landmarks:
            self.landmarks.remove_all(filename)
        if self.page_list:
            self.page_list.remove_all(filename)

    @override
    def on_soup_change(self) -> None:
        del self._toc
        del self._page_list
        del self._landmarks
        self._toc = None
        self._page_list = None
        self._landmarks = None

    @override
    def on_content_change(self) -> None:
        super().on_content_change()
        self.on_soup_change()
