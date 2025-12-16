from abc import ABC
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated, ClassVar, cast, override

import bs4

from epublib.nav.util import LandmarkEntryData, PageBreakData, TOCEntryData, epub_type
from epublib.xml_element import (
    AttributeValue,
    HrefRecursiveElement,
    HrefRoot,
    SyncType,
    XMLAttribute,
    XMLChildProtocol,
    XMLElement,
    XMLParent,
)


@dataclass(kw_only=True)
class NavElement[I: XMLChildProtocol](XMLParent[I], XMLElement, ABC):
    @property
    @override
    def parent_tag(self) -> bs4.Tag | None:
        return self.tag.select_one("& > ol")

    @override
    def create_parent_tag(self) -> bs4.Tag:
        ol = self.soup.new_tag("ol")
        __ = self.tag.append(ol)
        return ol


def create_href(soup: bs4.BeautifulSoup, tag: bs4.Tag) -> bs4.Tag:
    span = tag.select_one("& > span")
    if span:
        span.name = "a"
        return span

    anchor = soup.new_tag("a")
    __ = tag.insert(0, anchor)
    return anchor


@dataclass(kw_only=True)
class NavItem(
    NavElement["NavItem"],
    HrefRecursiveElement["NavItem"],
):
    """
    A navigation item in the navigation document.

    >>> item = NavItem(
    ...     soup=bs4.BeautifulSoup("", "lxml"),
    ...     text="Chapter 1",
    ...     own_filename="Text/nav.xhtml",
    ... )
    >>> item.tag
    <li><span>Chapter 1</span></li>
    >>> item.href = "chapter1.xhtml#heading1"
    >>> item.tag
    <li><a href="chapter1.xhtml#heading1">Chapter 1</a></li>
    >>> item.filename
    'Text/chapter1.xhtml#heading1'
    >>> item.href
    'chapter1.xhtml#heading1'
    >>> item.add(text="Chapter 2")
    NavItem(...)
    >>> item.tag
    <li><a href="...">...</a><ol><li><span>Chapter 2</span></li></ol></li>

    Args:
        soup: The BeautifulSoup of which this item is part of.
        filename: The filename of the navigation item. If empty, will be
            calculated from href and own_filename. One of filename or href
            must be provided.
        href: The href of the navigation item. If empty, will be calculated
            from filename and own_filename. One of filename or href must be
            provided.
        own_filename: The filename of the document containing this item.
        parent: The parent navigation item (or NavRoot).
        text: The text of the navigation item.
    """

    filename: str = ""
    text: Annotated[
        str,
        XMLAttribute(
            sync=SyncType.STRING,
            get=lambda tag: tag.select_one("& > span, & > a"),
            create=create_href,
        ),
    ]
    href: Annotated[str, XMLAttribute(get="a", create=create_href)] = ""

    tag_name: ClassVar[str] = "li"

    @override
    def create_tag(self) -> None:
        super().create_tag()
        self.href = self.href

    @override
    def __setattr__(self, name: str, value: AttributeValue | None) -> None:
        super().__setattr__(name, value)
        if name == "href" or name == "filename":
            text_tag = self.tag.select_one("& > span, & > a")
            if text_tag and text_tag.name == "a" and not text_tag.get("href"):
                text_tag.name = "span"
                if "href" in text_tag.attrs:
                    del text_tag["href"]

    @override
    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        text: str,
        filename: str = "",
        href: str = "",
    ) -> "NavItem":
        """
        Add a new navigation item as a child of this item.

        Args:
            text: The text of the new navigation item.
            filename: The filename of the new navigation item. If empty, will be
                calculated from href and self.own_filename. One of filename or
                href must be provided.
            href: The href of the new navigation item. If empty, will be
                calculated from filename and self.own_filename. One of filename or
                href must be provided.

        Returns:
            The newly created navigation item.
        """
        return super().add(text=text, filename=filename, href=href)

    @override
    def insert(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        position: int | None,
        text: str,
        filename: str = "",
        href: str = "",
    ) -> "NavItem":
        """
        Insert a new navigation item as a child of this item at the given
        position.

        Args:
            position: The position to insert the new navigation item at. If
                None, the item will be added at the end.
            text: The text of the new navigation item.
            filename: The filename of the new navigation item. If empty, will be
                calculated from href and self.own_filename. One of filename or
                href must be provided.
            href: The href of the new navigation item. If empty, will be
                calculated from filename and self.own_filename. One of filename or
                href must be provided.
        """
        return super().insert(position, text=text, filename=filename, href=href)

    @override
    def add_after_self(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        text: str,
        filename: str = "",
        href: str = "",
    ) -> "NavItem":
        """
        Add a new navigation item after this item in the parent's list of items.

        Args:
            text: The text of the new navigation item.
            filename: The filename of the new navigation item. If empty, will be
                calculated from href and self.own_filename. One of filename or
                href must be provided.
            href: The href of the new navigation item. If empty, will be
                calculated from filename and self.own_filename. One of filename or
                href must be provided.

        Raises:
            EPUBError: If this element has no parent.
        """
        return super().add_after_self(text=text, filename=filename, href=href)


@dataclass(kw_only=True)
class NavRoot(
    NavElement[NavItem],
    HrefRoot[NavItem],
    ABC,
):
    title: Annotated[
        str | None,
        XMLAttribute(
            sync=SyncType.STRING,
            get=lambda tag: tag.select_one(
                "& > h1, & > h2, & > h3, & > h4, & > h5, & > h6"
            ),
            create=lambda soup, tag: cast(
                bs4.Tag,
                tag.insert(0, soup.new_tag("h2" if soup.find("h1") else "h1"))[0],
            ),
        ),
    ] = None

    tag_name: ClassVar[str] = "nav"
    new_attrs: ClassVar[dict[str, str]] = {}

    @override
    def create_tag(self) -> None:
        super().create_tag()
        for key, val in self.new_attrs.items():
            self.tag[key] = val

    def reset_tag(self) -> None:
        old_title_tag = cast(
            bs4.Tag,
            self._get_attributes()["title"].get(self.tag),  # type: ignore[reportOptionalCall]
        )
        old_tag = self.tag
        # put temporary in place to detect accurately which heading to
        # use for the new title
        temporary = self.soup.new_tag("span")
        __ = old_tag.replace_with(temporary)

        self.create_tag()

        __ = temporary.replace_with(self.tag)

        if old_tag.get("id"):
            self.tag["id"] = old_tag["id"]

        new_title_tag = self._get_attributes()["title"].get(self.tag)  # type: ignore[reportOptionalCall]

        if old_title_tag and new_title_tag and old_title_tag.get("id"):
            new_title_tag["id"] = old_title_tag["id"]

    def insert_self_in_soup(self) -> None:
        if self.soup.main:
            __ = self.soup.main.insert(0, self.tag)

        elif self.soup.body:
            __ = self.soup.body.insert(0, self.tag)

        else:
            __ = self.soup.insert(0, self.tag)

    @property
    def text(self) -> str | None:
        """
        The text of this navigation root's title.
        """
        return self.title

    @text.setter
    def text(self, value: str | None) -> None:
        self.title = value

    @override
    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        text: str,
        filename: str = "",
        href: str = "",
    ) -> NavItem:
        """
        Insert a new navigation item as a child of this element.

        Args:
            text: The text of the new navigation item.
            filename: The filename of the new navigation item. If empty, will be
                calculated from href and self.own_filename. One of filename or
                href must be provided.
            href: The href of the new navigation item. If empty, will be
                calculated from filename and self.own_filename. One of filename or
                href must be provided.
        """
        return super().add(text=text, filename=filename, href=href)

    @override
    def insert(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        position: int | None,
        text: str,
        filename: str = "",
        href: str = "",
    ) -> NavItem:
        """
        Insert a new navigation item as a child of this element at the given
        position

        Args:
            position: The position to insert the new navigation item at. If
                None, the item will be added at the end.
            text: The text of the new navigation item.
            filename: The filename of the new navigation item. If empty, will be
                calculated from href and self.own_filename. One of filename or
                href must be provided.
            href: The href of the new navigation item. If empty, will be
                calculated from filename and self.own_filename. One of filename or
                href must be provided.
        """
        return super().insert(position, text=text, filename=filename, href=href)


class TocRoot(NavRoot):
    """
    The root of the table of contents of the navigation document.

    >>> toc = TocRoot(
    ...     soup=bs4.BeautifulSoup("", "lxml"),
    ...     title="Table of Contents",
    ...     own_filename="Text/nav.xhtml",
    ... )

    >>> toc.tag
    <nav epub:type="toc" id="toc" role="doc-toc"><h1>Table of Contents</h1></nav>
    >>> toc.add("Chapter 1", href="chapter1.xhtml#heading1")
    NavItem(...)
    >>> toc.tag.ol
    <ol><li><a href="chapter1.xhtml#heading1">Chapter 1</a></li></ol>

    Args:
        soup: The BeautifulSoup of which this TOC is part of.
        own_filename: The filename of the document containing this TOC.
        title: The title of the TOC.
    """

    new_attrs: ClassVar[dict[str, str]] = {
        epub_type: "toc",
        "role": "doc-toc",
        "id": "toc",
    }

    def reset(self, entries: Sequence[TOCEntryData]) -> None:
        self.reset_tag()

        self._items: list[NavItem] = []

        def add_items(
            item: NavItem | NavRoot,
            children: Sequence[TOCEntryData],
        ) -> None:
            for entry in children:
                if not entry.label.strip():
                    continue
                filename = entry.filename
                if entry.id is not None:
                    filename += f"#{entry.id}"
                added_item = item.add(text=entry.label, filename=filename)
                add_items(added_item, entry.children)

        add_items(self, entries)


class PageListRoot(NavRoot):
    """
    The page list in the navigation document.

    >>> pl = PageListRoot(
    ...     soup=bs4.BeautifulSoup("", "lxml"),
    ...     own_filename="Text/nav.xhtml",
    ... )

    >>> pl.tag
    <nav epub:type="page-list" hidden="" id="page-list"></nav>
    >>> pl.add("Chapter 1", href="chapter1.xhtml#heading1")
    NavItem(...)
    >>> pl.tag.ol
    <ol><li><a href="chapter1.xhtml#heading1">Chapter 1</a></li></ol>

    Args:
        soup: The BeautifulSoup of which this page list is part of.
        own_filename: The filename of the document containing this page list.
        title: The title of the page list.
    """

    new_attrs: ClassVar[dict[str, str]] = {
        epub_type: "page-list",
        "id": "page-list",
        "hidden": "",
    }

    @override
    def insert_self_in_soup(self) -> None:
        assert not self.soup.select_one('nav[epub|type="page-list"]'), (
            "page list already existent!"
        )

        toc = self.soup.select_one('nav[epub|type="toc"]')
        if toc:
            __ = toc.insert_after(self.tag)
            return

        landmarks = self.soup.select_one('nav[epub|type="landmarks"]')
        if landmarks:
            __ = landmarks.insert_before(self.tag)
            return

        super().insert_self_in_soup()

    def reset(self, entries: Sequence[PageBreakData]) -> None:
        self.reset_tag()

        self._items: list[NavItem] = []

        for pagebreak in entries:
            __ = self.add(text=pagebreak.label, filename=pagebreak.filename)


class LandmarksRoot(NavRoot):
    """
    The page list in the navigation document.

    >>> lm = LandmarksRoot(
    ...     soup=bs4.BeautifulSoup("", "lxml"),
    ...     own_filename="Text/nav.xhtml",
    ... )

    >>> lm.tag
    <nav epub:type="landmarks" hidden="" id="landmarks"></nav>
    >>> lm.add("Chapter 1", href="chapter1.xhtml#heading1")
    NavItem(...)
    >>> lm.tag.ol
    <ol><li><a href="chapter1.xhtml#heading1">Chapter 1</a></li></ol>

    Args:
        soup: The BeautifulSoup of which these landmarks are part of.
        own_filename: The filename of the document containing these landmarks.
        title: The title of the landmarks.
    """

    new_attrs: ClassVar[dict[str, str]] = {
        epub_type: "landmarks",
        "id": "landmarks",
        "hidden": "",
    }

    @override
    def insert_self_in_soup(self) -> None:
        assert not self.soup.select_one('nav[epub|type="landmarks"]'), (
            "landmarks already existent!"
        )

        page_list = self.soup.select_one('nav[epub|type="page-list"]')
        if page_list:
            __ = page_list.insert_after(self.tag)
            return

        toc = self.soup.select_one('nav[epub|type="toc"]')
        if toc:
            __ = toc.insert_after(self.tag)
            return

        super().insert_self_in_soup()

    def reset(self, entries: Sequence[LandmarkEntryData]) -> None:
        self.reset_tag()

        self._items: list[NavItem] = []

        for entry in entries:
            filename = entry.filename

            item = self.add(text=entry.label, filename=filename)

            if entry.epub_type:
                anchor = item.tag.select_one("& > a")
                if anchor:
                    anchor[epub_type] = entry.epub_type
