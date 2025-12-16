from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import IO, override
from zipfile import ZipInfo

from epublib.exceptions import EPUBError
from epublib.media_type import MediaType
from epublib.nav import NavItem, NavRoot
from epublib.nav.resource import NavigationDocument
from epublib.nav.util import PageBreakData, TOCEntryData
from epublib.ncx import (
    NCXAuthor,
    NCXHead,
    NCXNavList,
    NCXNavMap,
    NCXNavPoint,
    NCXPageList,
    NCXTitle,
)
from epublib.package.metadata import BookMetadata
from epublib.resources import PublicationResource, SoupChanging, XMLResource
from epublib.soup import NCXSoup


class NCXFile(  # type: ignore[reportUnsafeMultipleInheritance]
    PublicationResource,
    XMLResource[NCXSoup],
    SoupChanging,
):
    """
    The NCX document of the EPUB file, sometimes known as the 'toc.ncx' file.
    This is used in EPUB2 files for navigation, and was largely superseded by
    the package document in EPUB3. Support for it in EPUB3 is optional.

    Args:
        file: The file-like object or bytes containing the NCX XML data.
        info: The `ZipInfo` object or filename for this resource in the EPUB
            archive.
        media_type: The media type of this resource. Defaults to
            `MediaType.NCX`.
    """

    soup_class: type[NCXSoup] = NCXSoup

    def __init__(
        self,
        file: IO[bytes] | bytes,
        info: ZipInfo | str | Path,
        media_type: MediaType | str = MediaType.NCX,
    ) -> None:
        super().__init__(file, info, media_type)
        self._head: NCXHead | None = None
        self._title: NCXTitle | None = None
        self._authors: list[NCXAuthor] | None = None
        self._nav_map: NCXNavMap | None = None
        self._page_list: NCXPageList | None = None
        self._nav_lists: Sequence[NCXNavList] | None = None

    @property
    def head(self) -> NCXHead:
        """
        Return the head of the NCX document, containing metadata, as a NCXHead
        object.
        """
        if self._head is None:
            self._head = NCXHead(self.soup, self.soup.head)
        return self._head

    @property
    def title(self) -> NCXTitle:
        """Return the title of the NCX document, as a NCXTitle object."""
        if self._title is None:
            self._title = NCXTitle.from_tag(self.soup, self.soup.docTitle)
        return self._title

    @property
    def authors(self) -> Sequence[NCXAuthor]:
        """
        Return a sequence of authors of the NCX document as NCXAuthor objects.
        """
        if self._authors is None:
            self._authors = list(
                NCXAuthor.from_tag(self.soup, tag)
                for tag in self.soup.find_all("docAuthor")
            )

        return tuple(self._authors)

    @property
    def nav_map(self) -> NCXNavMap:
        """Return the navigation map of the NCX document as a NCXNavMap object."""
        if self._nav_map is None:
            tag = self.soup.select_one("navMap")
            if tag:
                self._nav_map = NCXNavMap.from_tag(
                    soup=self.soup,
                    tag=tag,
                    own_filename=self.filename,
                    parent=self,
                )
            else:
                self._nav_map = NCXNavMap(
                    soup=self.soup,
                    own_filename=self.filename,
                    parent=self,
                )
                self._nav_map.insert_self_in_soup()
        return self._nav_map

    @property
    def page_list(self) -> NCXPageList | None:
        """
        Return the page list of the NCX document as a NCXPageList object, or
        `None` if there is no page list.
        """
        if self._page_list is None:
            tag = self.soup.select_one("pageList")
            if tag:
                self._page_list = NCXPageList.from_tag(
                    soup=self.soup,
                    tag=tag,
                    own_filename=self.filename,
                    parent=self,
                )
        return self._page_list

    @property
    def nav_lists(self) -> Sequence[NCXNavList]:
        """
        Return a sequence of nav lists in the NCX document as NCXNavList
        objects.
        """
        if self._nav_lists is None:
            self._nav_lists = tuple(
                NCXNavList.from_tag(
                    soup=self.soup,
                    tag=tag,
                    own_filename=self.filename,
                )
                for tag in self.soup.find_all("navList")
            )

        return self._nav_lists

    def remove(self, filename: str | Path) -> None:
        """
        Remove all references to the given filename from the NCX document.

        Args:
            filename: The filename to remove references to.
        """
        # Todo: remove references to images and audio as well
        self.nav_map.remove_nodes(filename)
        if self.page_list:
            self.page_list.remove_all(filename)
        for nav_list in self.nav_lists:
            nav_list.remove_nodes(filename)

        self.update_numbers()

    def get_author(self, name: str) -> NCXAuthor | None:
        """
        Return the author with the given name, or `None` if no such author
        exists.

        Args:
            name: The name of the author to find.

        Returns:
            The NCXAuthor object with the given name, or `None` if no such
            author exists.
        """
        for author in self.authors:
            if author.text == name:
                return author

        return None

    def add_author(self, name: str) -> NCXAuthor:
        """
        Add a new author with the given name to the NCX document, and return
        the corresponding NCXAuthor object.

        Args:
            name: The name of the author to add.

        Returns:
            The newly created NCXAuthor object.
        """
        author = NCXAuthor(soup=self.soup, text=name)
        if self._authors is not None:
            self._authors.append(author)
        author.insert_self_in_soup(self.soup)

        return author

    def remove_author(self, author: str | NCXAuthor) -> NCXAuthor | None:
        """
        Remove the given author from the NCX document, and return the removed
        NCXAuthor object, or `None` if no such author exists.

        Args:
            author: The NCXAuthor object or name of the author to remove.

        Returns:
            The removed NCXAuthor object, or `None` if no such author exists.
        """
        if not isinstance(author, NCXAuthor):
            author_or_none = self.get_author(author)
            if author_or_none is None:
                return None
            author = author_or_none

        if self._authors is not None:
            self._authors.remove(author)
        author.tag.decompose()

        return author

    def add_nav_list(self, items: Iterable[TOCEntryData]) -> NCXNavList:
        """
        Add a new nav list with the given items to the NCX document, and return
        the corresponding NCXNavList object.

        Args:
            items: An iterable of TOCEntryData objects representing the items
                to add to the new nav list.

        Returns:
            The newly created NCXNavList object.
        """
        nav_list = NCXNavList(
            self.soup,
            own_filename=self.filename,
        )

        for entry in items:
            __ = nav_list.add(filename=entry.filename, text=entry.label)

        nav_list.insert_self_in_soup()
        return nav_list

    def reset_page_list(self, entries: list[PageBreakData]) -> None:
        """
        Reset the page list of the NCX document to contain the given entries.

        Args:
            entries: A list of PageBreakData objects representing the entries
                to set in the page list.
        """
        if not self.page_list:
            self._page_list = NCXPageList(
                self.soup,
                own_filename=self.filename,
                parent=self,
            )
            self._page_list.insert_self_in_soup()

        assert self.page_list
        self.page_list.reset(entries)

    def update_total_page_count(self) -> None:
        """
        Update the total page count in the head of the NCX document.
        """
        self.head.total_page_count = (
            len(self.page_list.items) if self.page_list else None
        )

    def update_depth(self) -> None:
        """
        Update the depth in the head of the NCX document, based on the maximum
        depth of the nav map.
        """
        self.head.depth = self.nav_map.max_depth()

    def update_max_page_number(self) -> None:
        """
        Update the max page number in the head of the NCX document.
        """
        self.head.max_page_number = (
            self.page_list.largest_page_number if self.page_list else None
        )

    def _update_play_order_recursive(
        self,
        nav_point: NCXNavPoint | NCXNavMap,
        start: int,
    ) -> int:
        for item in nav_point.items:
            item.play_order = start
            start = self._update_play_order_recursive(item, start + 1)

        return start

    def update_play_order(self) -> None:
        """
        Update the play order of all nav points in the nav map, starting from
        1 and incrementing by 1 for each nav point in a depth-first traversal.
        """
        __ = self._update_play_order_recursive(self.nav_map, 1)

    def update_numbers(self) -> None:
        """
        Update required numbers in the head and nav map of the NCX file:
        - max depth;
        - max page number (if there is a page list);
        - total page count (if there is a page list);
        - play order.
        """

        self.update_depth()
        self.update_play_order()
        self.update_max_page_number()
        self.update_total_page_count()

    def sync_head(self, metadata: BookMetadata) -> NCXHead:
        """
        Sync metadata from the package document metadata to the NCX
        document, erasing any existing head > meta items. Should be used
        after populating the navMap and pageList (if there is one), to
        get an accurate page and depth count.

        Args:
            metadata: The BookMetadata object to sync from.

        Returns:
            The NCXHead object after syncing.
        """
        head = NCXHead(
            soup=self.soup,
            tag=self.soup.new_tag("head"),
        )

        if metadata.identifier:
            head.uid = metadata.identifier

        self.head.depth = 0
        head.total_page_count = None
        head.max_page_number = None

        __ = self.soup.head.replace_with(head.tag)
        self._head = head
        self.update_numbers()

        return head

    def sync_toc(self, nav: NavigationDocument) -> NCXNavMap:
        """
        Sync the NCX navMap to match the given TOC structure, erasing
        any existing navMap items.

        Args:
            nav: The NavigationDocument to sync from.

        Returns:
            The NCXNavMap object after syncing.

        Raises:
            EPUBError: If self referential structure is detected in the TOC structure.
        """

        self.nav_map.reset([])

        count = 1
        max_count = len(list(nav.toc.tag.find_all(True))) * 2

        def recurse_items(
            nav_point: NCXNavPoint | NCXNavMap,
            toc_item: NavItem | NavRoot,
        ):
            nonlocal count
            count += 1

            if count > max_count:
                raise EPUBError("Infinite recursion detected in TOC structure")

            for sub_toc_item in toc_item.items:
                sub_nav_point = nav_point.add(sub_toc_item.text, sub_toc_item.filename)
                sub_nav_point.tag["id"] = f"navPoint{count}"
                recurse_items(sub_nav_point, sub_toc_item)

        recurse_items(self.nav_map, nav.toc)
        return self.nav_map

    def sync_page_list(self, nav: NavigationDocument) -> NCXPageList:
        """
        Sync the NCX page list to match the given navigation document page list
        structure, erasing any existing page list items.

        Args:
            nav: The NavigationDocument to sync from.

        Returns:
            The NCXPageList object after syncing.

        Raises:
            EPUBError: If the given navigation document has no page list.
        """

        if not nav.page_list:
            raise EPUBError("No page list in navigation document to sync from")

        self.reset_page_list([])
        assert self.page_list

        for item in nav.page_list.items:
            __ = self.page_list.add(item.text, item.filename)

        return self.page_list

    @override
    def on_soup_change(self) -> None:
        del self._head
        del self._title
        del self._authors
        del self._nav_map
        del self._page_list
        del self._nav_lists
        self._head = None
        self._title = None
        self._authors = None
        self._nav_map = None
        self._page_list = None
        self._nav_lists = None

    @override
    def on_content_change(self) -> None:
        super().on_content_change()
        self.on_soup_change()
