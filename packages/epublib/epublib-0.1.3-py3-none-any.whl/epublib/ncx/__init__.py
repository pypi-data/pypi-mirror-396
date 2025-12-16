from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Annotated, ClassVar, Literal, Protocol, Self, override

import bs4

from epublib.exceptions import EPUBError
from epublib.nav.util import PageBreakData, TOCEntryData
from epublib.soup import NCXSoup
from epublib.util import parse_int
from epublib.xml_element import (
    HrefElement,
    HrefRecursiveElement,
    HrefRoot,
    ParentOfHref,
    SyncType,
    XMLAttribute,
    XMLElement,
    XMLParent,
)


@dataclass(kw_only=True)
class NCXMeta(XMLElement[NCXSoup]):
    """A metadata item in the NCX head section.

    Args:
        soup: The NCX soup this element belongs to.
        name: The name of the meta item.
        content: The content of the meta item.
    """

    name: Annotated[str, XMLAttribute()]
    content: Annotated[str, XMLAttribute()]

    tag_name: ClassVar[str] = "meta"

    @property
    def pk(self) -> str:
        return self.name


class NCXHead(XMLParent[NCXMeta, NCXSoup]):
    """The head section of the NCX file, a container of NCXMeta items.

    Args:
        soup: The NCX soup this element belongs to.
    """

    def __post_init__(self) -> None:
        if not self.tag.name == "head":
            raise EPUBError("NCXHead tag must be a <head> element")

        super().__post_init__()

    @override
    def add(self, name: str, content: str) -> NCXMeta:  # type: ignore[reportIncompatibleMethodOverride]
        """Add a new meta item to the head section.

        Args:
            name: The name of the meta item.
            content: The content of the meta item.

        Returns:
            The newly created NCXMeta item.
        """

        return super().add(name=name, content=content)

    @property
    def uid(self) -> str:
        """Return the unique identifier of the publication."""

        try:
            meta = self["dtb:uid"]
        except KeyError as error:
            raise EPUBError("Expected 'dtb:uid' in NCX head") from error
        return meta.content

    @uid.setter
    def uid(self, value: str) -> None:
        meta = self.get("dtb:uid")
        if meta:
            meta.content = value
        else:
            __ = self.add(name="dtb:uid", content=value)

    @property
    def depth(self) -> int:
        """Return the depth of the navigation map structure."""
        try:
            meta = self["dtb:depth"]
        except KeyError as error:
            raise EPUBError("Expected 'dtb:depth' in NCX head") from error
        return int(meta.content)

    @depth.setter
    def depth(self, value: int) -> None:
        meta = self.get("dtb:depth")
        if meta:
            meta.content = str(value)
        else:
            __ = self.add(name="dtb:depth", content=str(value))

    @property
    def total_page_count(self) -> int | None:
        """Return the total page count of the publication.

        If there are no navigable pages (represented as 0), return None.
        """

        try:
            meta = self["dtb:totalPageCount"]
        except KeyError as error:
            raise EPUBError("Expected 'dtb:totalPageCount' in NCX head") from error
        int_val = int(meta.content)

        return None if int_val == 0 else int_val

    @total_page_count.setter
    def total_page_count(self, value: int | None) -> None:
        meta = self.get("dtb:totalPageCount")

        str_value = "0" if value is None else str(value)

        if meta:
            meta.content = str_value
        else:
            __ = self.add(name="dtb:totalPageCount", content=str_value)

    @property
    def max_page_number(self) -> int | None:
        """Return the largest value attribute on page targets in the page list.

        If there are no navigable pages (represented as 0), return None.
        """

        meta = self["dtb:maxPageNumber"]
        int_val = int(meta.content)

        return None if int_val == 0 else int_val

    @max_page_number.setter
    def max_page_number(self, value: int | None) -> None:
        meta = self.get("dtb:maxPageNumber")

        str_value = "0" if value is None else str(value)

        if meta:
            meta.content = str_value
        else:
            __ = self.add(name="dtb:maxPageNumber", content=str_value)


@dataclass(kw_only=True)
class NCXDocData(XMLElement[NCXSoup], ABC):
    text: Annotated[str, XMLAttribute(sync=SyncType.STRING, get="text", create="text")]
    id: Annotated[str | None, XMLAttribute()] = None

    @abstractmethod
    def insert_self_in_soup(self, soup: NCXSoup) -> None: ...


class NCXAuthor(NCXDocData):
    """An authorship in the NCX file.

    Args:
        soup: The NCX soup this element belongs to.
        text: The name of the author.
        id: An optional identifier for the author.
    """

    tag_name: ClassVar[str] = "docAuthor"

    @override
    def insert_self_in_soup(self, soup: NCXSoup) -> None:
        previous_tag = soup.find_all(["docAuthor", "docTitle"])[-1]
        __ = previous_tag.insert_after(self.tag)


class NCXTitle(NCXDocData):
    """The title of the publication in the NCX file.

    Args:
        soup: The NCX soup this element belongs to.
        text: The title of the publication.
        id: An optional identifier for the title.
    """

    tag_name: ClassVar[str] = "docTitle"

    @override
    def insert_self_in_soup(self, soup: NCXSoup) -> None:
        previous_tag = soup.head
        __ = previous_tag.insert_after(self.tag)


def create_ncx_text_tag(parent: str, soup: bs4.BeautifulSoup, tag: bs4.Tag) -> bs4.Tag:
    new_tag = soup.new_tag("text")
    parent_tag = tag.select_one(f"& > {parent}")

    if not parent_tag:
        parent_tag = soup.new_tag(parent)
        info_tag = tag.select_one("& > navInfo")
        if parent != "navInfo" and info_tag:
            __ = info_tag.insert_after(parent_tag)
        else:
            __ = tag.insert(0, parent_tag)

    __ = parent_tag.insert(0, new_tag)
    return new_tag


@dataclass(kw_only=True)
class NCXHrefElement(HrefElement[NCXSoup], ABC):
    @staticmethod
    def create_href_tag(soup: bs4.BeautifulSoup, tag: bs4.Tag) -> bs4.Tag:
        new_tag = soup.new_tag("content")
        if tag.select_one("& > navLabel"):
            __ = tag.insert(1, new_tag)
        else:
            __ = tag.insert(0, new_tag)

        return new_tag

    id: Annotated[str, XMLAttribute()]
    href: Annotated[str, XMLAttribute("src", get="content", create=create_href_tag)] = (
        ""
    )
    text: Annotated[
        str,
        XMLAttribute(
            sync=SyncType.STRING,
            get=lambda tag: tag.select_one("& > navLabel > text"),
            create=partial(create_ncx_text_tag, "navLabel"),
        ),
    ]


@dataclass(kw_only=True)
class NCXWithInfo:
    info: Annotated[
        str | None,
        XMLAttribute(
            sync=SyncType.STRING,
            get=lambda tag: tag.select_one("& > navInfo > text"),
            create=partial(create_ncx_text_tag, "navInfo"),
        ),
    ] = None


@dataclass(kw_only=True)
class NCXNavPoint(
    NCXHrefElement,
    HrefRecursiveElement["NCXNavPoint", NCXSoup],
    NCXWithInfo,
):
    """A navigation point in NCX table of contents.

    Args:
        soup: The NCX soup this element belongs to.
        href: The href of the navPoint. May include a fragment. If empty, will
            be calculated from `filename` and `own_filename`. One of `href` or
            `filename` must be given.
        filename: The filename the navPoint points to. May include a fragment.
            If empty, will be calculated from `href` and `own_filename`. One of
            `href` or `filename` must be given.
        own_filename: The filename of the NCX file this element belongs to.
        id: The identifier of the navPoint.
        text: The label of the navPoint.
        play_order: The play order of the navPoint.
        info: An optional info text for the navPoint.
    """

    play_order: Annotated[int | None, XMLAttribute("playOrder")] = None

    tag_name: ClassVar[str] = "navPoint"

    @override
    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        text: str,
        filename: str | Path,
        id: str | None = None,
        info: str | None = None,
    ) -> "NCXNavPoint":
        """Add a new navPoint to this element.

        Args:
            text: The label of the new navPoint.
            filename: The filename the new navPoint points to. May include a
                fragment.
            id: The identifier of the new navPoint. If None, a new identifier
                will be generated.
            info: An optional info text for the new navPoint.

        Returns:
            The newly created NCXNavPoint item.
        """

        return super().add(
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
            info=info,
        )

    @override
    def insert(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        position: int | None,
        text: str,
        filename: str | Path,
        id: str | None = None,
        info: str | None = None,
    ) -> "NCXNavPoint":
        """Insert a new navPoint in a specific position of this element.

        Args:
            position: The position to insert the new navPoint at. If None, the
                new navPoint will be added at the end.
            text: The label of the new navPoint.
            filename: The filename the new navPoint points to. May include a
                fragment.
            id: The identifier of the new navPoint. If None, a new identifier
                will be generated.
            info: An optional info text for the new navPoint.
        """
        return super().insert(
            position,
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
            info=info,
        )

    @override
    def add_after_self(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        text: str,
        filename: str | Path,
        id: str | None = None,
        info: str | None = None,
    ) -> "NCXNavPoint":
        """Add a new navPoint in this element's parent, after this one.

        Args:
            text: The label of the new navPoint.
            filename: The filename the new navPoint points to. May include a
                fragment.
            id: The identifier of the new navPoint. If None, a new identifier
                will be generated.
            info: An optional info text for the new navPoint.

        Raises:
            EPUBError: If this element has no parent.
        """

        return super().add_after_self(
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
            info=info,
        )


@dataclass(kw_only=True)
class NCXNavList(
    HrefRoot[NCXNavPoint, NCXSoup],
    XMLElement[NCXSoup],
    NCXWithInfo,
):
    """A navigation list in the NCX file.

    Args:
        soup: The NCX soup this element belongs to.
        own_filename: The filename of the NCX file this element belongs to.
        text: The label of the navList.
        info: An optional info text for the navList.
    """

    text: Annotated[
        str | None,
        XMLAttribute(
            sync=SyncType.STRING,
            get=lambda tag: tag.select_one("& > navLabel > text"),
            create=partial(create_ncx_text_tag, "navLabel"),
        ),
    ] = None

    tag_name: ClassVar[str] = "navList"

    def insert_self_in_soup(self) -> None:
        ncx = self.soup.ncx
        if not ncx:
            raise EPUBError("Invalid NCX file: couldn't find 'ncx' tag")

        for tag_name in ["navMap", "pageList"]:
            other = ncx.find_all(tag_name)[-1]
            if other:
                __ = other.insert_after(self.tag)
                return

        __ = ncx.insert(0, self.tag)

    @override
    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        text: str,
        filename: str | Path,
        id: str | None = None,
        info: str | None = None,
    ) -> NCXNavPoint:
        """Add a new navPoint to this navList.

        Args:
            text: The label of the new navPoint.
            filename: The filename the new navPoint points to. May include a
                fragment.
            id: The identifier of the new navPoint. If None, a new identifier
                will be generated.
            info: An optional info text for the new navPoint.

        Returns:
            The newly created NCXNavPoint item.
        """

        return super().add(
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
            info=info,
        )

    @override
    def insert(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        position: int | None,
        text: str,
        filename: str | Path,
        id: str | None = None,
        info: str | None = None,
    ) -> NCXNavPoint:
        """Insert a new navPoint to this navList in a specific position.

        Args:
            position: The position to insert the new navPoint at. If None, the
                new navPoint will appended.
            text: The label of the new navPoint.
            filename: The filename the new navPoint points to. May include a
                fragment.
            id: The identifier of the new navPoint. If None, a new identifier
                will be generated.
            info: An optional info text for the new navPoint.

        Returns:
            The newly created NCXNavPoint item.
        """

        return super().insert(
            position,
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
            info=info,
        )

    def reset(self, entries: Sequence[TOCEntryData]) -> None:
        new_tag = self.soup.new_tag(self.tag_name)
        __ = self.tag.replace_with(new_tag)

        self.tag: bs4.Tag = new_tag
        self._items: list[NCXNavPoint] = []

        def add_items(
            item: NCXNavPoint | NCXNavList,
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


class NumberUpdating(Protocol):
    def update_numbers(self) -> None: ...


@dataclass(kw_only=True)
class NCXNavMap(NCXNavList):
    """The navigation map in the NCX file.

    Args:
        soup: The NCX soup this element belongs to.
        own_filename: The filename of the NCX file this element belongs to.
        text: The label of the navMap.
        parent: The parent object that will be notified when the navMap
            changes, so it can update numbers accordingly.
        info: An optional info text for the navMap.
    """

    parent: NumberUpdating

    tag_name: ClassVar[str] = "navMap"

    @classmethod
    @override
    def from_tag(  # type: ignore[reportIncompatibleMethodOverride]
        cls,
        soup: NCXSoup,
        tag: bs4.Tag,
        own_filename: str | Path,
        parent: NumberUpdating,
    ) -> Self:
        return super().from_tag(
            soup,
            tag,
            own_filename=str(own_filename),
            parent=parent,  # type: ignore[reportArgumentType]
        )

    @override
    def insert_self_in_soup(self) -> None:
        ncx = self.soup.ncx
        if not ncx:
            raise EPUBError("Invalid NCX file: couldn't find 'ncx' tag")

        for tag_name in ["head", "docTitle", "docAuthor"]:
            other = ncx.find_all(tag_name)[-1]
            if other:
                __ = other.insert_after(self.tag)
                return

        __ = ncx.insert(0, self.tag)

    @override
    def add(
        self,
        text: str,
        filename: str | Path,
        id: str | None = None,
        info: str | None = None,
    ) -> NCXNavPoint:
        """Add a new navPoint to this navMap.

        Args:
            text: The label of the new navPoint.
            filename: The filename the new navPoint points to. May include a
                fragment.
            id: The identifier of the new navPoint. If None, a new identifier
                will be generated.
            info: An optional info text for the new navPoint.

        Returns:
            The newly created NCXNavPoint item.
        """

        item = super().add(
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
            info=info,
        )
        self.parent.update_numbers()
        return item

    @override
    def insert(
        self,
        position: int | None,
        text: str,
        filename: str | Path,
        id: str | None = None,
        info: str | None = None,
    ) -> NCXNavPoint:
        """Insert a new navPoint to the navMap in a specific position.

        Args:
            position: The position to insert the new navPoint at. If None, the
                new navPoint will appended.
            text: The label of the new navPoint.
            filename: The filename the new navPoint points to. May include a
                fragment.
            id: The identifier of the new navPoint. If None, a new identifier
                will be generated.
            info: An optional info text for the new navPoint.

        Returns:
            The newly created NCXNavPoint item.
        """

        item = super().insert(
            position,
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
            info=info,
        )
        self.parent.update_numbers()
        return item

    @override
    def reset(self, entries: Sequence[TOCEntryData]) -> None:
        super().reset(entries)
        self.parent.update_numbers()


@dataclass(kw_only=True)
class NCXPageTarget(NCXHrefElement):
    """A page target in the NCX page list.

    Args:
        soup: The NCX soup this element belongs to.
        filename: The filename the pageTarget points to. May include a fragment.
            If empty, will be calculated from `href` and `own_filename`. One of
            `href` or `filename` must be given.
        href: The href the pageTarget points to. May include a fragment. If
            empty, will be calculated from `filename` and `own_filename`. One of
            `href` or `filename` must be given.
        own_filename: The filename of the NCX file this element belongs to.
        id: The identifier of the pageTarget.
        text: The label of the pageTarget.
        type: The type of the pageTarget. If None, it will be inferred from
            the text. Can be "front" (for roman numerals), "normal" (for
            arabic numerals) or "special" (for anything else).
    """

    type: Annotated[Literal["front", "normal", "special"] | None, XMLAttribute()] = None

    def __post_init__(self) -> None:
        if self.type is None:
            page_number = parse_int(self.text)
            if page_number is not None and page_number > 0:
                self.type = "normal"
            elif all(char in "ivxlcdm" for char in self.text.lower()):
                self.type = "front"
            else:
                self.type = "special"

        super().__post_init__()

    tag_name: ClassVar[str] = "pageTarget"


@dataclass(kw_only=True)
class NCXPageList(
    ParentOfHref[NCXPageTarget, NCXSoup],
    XMLElement[NCXSoup],
    NCXWithInfo,
):
    """The page list in the NCX file.

    Args:
        soup: The NCX soup this element belongs to.
        info: An optional info text for the pageList.
        own_filename: The filename of the NCX file this element belongs to.
        parent: The parent object that will be notified when the pageList
            changes, so it can update numbers accordingly.
    """

    own_filename: str
    parent: NumberUpdating

    tag_name: ClassVar[str] = "pageList"

    def insert_self_in_soup(self) -> None:
        __ = self.soup.navMap.insert_after(self.tag)

    @property
    def largest_page_number(self) -> int | None:
        """Return the largest page number in the page list."""
        if not self.items:
            return None

        return max(parse_int(item.text) or 0 for item in self.items)

    @classmethod
    @override
    def from_tag(  # type: ignore[reportIncompatibleMethodOverride]
        cls,
        soup: NCXSoup,
        tag: bs4.Tag,
        own_filename: str | Path,
        parent: NumberUpdating,
    ) -> Self:
        return super().from_tag(
            soup,
            tag,
            own_filename=str(own_filename),
            parent=parent,  # type: ignore[reportArgumentType]
        )

    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        text: str,
        filename: str | Path,
        id: str | None = None,
        type: Literal["front", "normal", "special"] | None = None,
    ) -> NCXPageTarget:
        """Add a new pageTarget to the pageList.

        Args:
            text: The label of the new pageTarget.
            filename: The filename the new pageTarget points to. May include a
                fragment.
            id: The identifier of the new pageTarget. If None, a new identifier
                will be generated.
            type: The type of the new pageTarget. If None, it will be inferred
                from the text. Can be "front" (for roman numerals), "normal"
                (for arabic numerals) or "special" (for anything else).

        Returns:
            The newly created NCXPageTarget item.
        """

        item = super().add(
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
        )
        self.parent.update_numbers()
        return item

    def insert(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        position: int,
        text: str,
        filename: str | Path,
        id: str | None = None,
        type: Literal["front", "normal", "special"] | None = None,
    ) -> NCXPageTarget:
        """Insert a new pageTarget to the pageList at a specific position.

        Args:
            position: The position to insert the new pageTarget at.
            text: The label of the new pageTarget.
            filename: The filename the new pageTarget points to. May include a
                fragment.
            id: The identifier of the new pageTarget. If None, a new identifier
                will be generated.
            type: The type of the new pageTarget. If None, it will be inferred
                from the text. Can be "front" (for roman numerals), "normal"
                (for arabic numerals) or "special" (for anything else).

        Returns:
            The newly created NCXPageTarget item.
        """

        item = super().insert(
            position,
            text=text,
            filename=str(filename),
            id=self.get_new_id(filename) if id is None else id,
        )
        self.parent.update_numbers()
        return item

    def reset(self, entries: Sequence[PageBreakData]) -> None:
        new_tag = self.soup.new_tag(self.tag_name)
        __ = self.tag.replace_with(new_tag)
        self.tag: bs4.Tag = new_tag
        self._items: list[NCXPageTarget] = []

        for index, pagebreak in enumerate(entries, start=1):
            __ = self.add_item(
                NCXPageTarget(
                    soup=self.soup,
                    filename=pagebreak.filename,
                    own_filename=self.own_filename,
                    id=f"page-target-{index}",
                    text=pagebreak.label,
                )
            )

        self.parent.update_numbers()
