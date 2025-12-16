from collections.abc import Sequence
from dataclasses import dataclass
from typing import Annotated, ClassVar, override

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.package.properties import WithProperties
from epublib.xml_element import XMLAttribute, XMLElement, XMLParent


@dataclass(kw_only=True)
class SpineItemRef(WithProperties, XMLElement):
    """
    An item reference in the EPUB spine.

    Example:

    >>> import bs4
    >>> soup = bs4.BeautifulSoup("", "xml")
    >>> item = SpineItemRef(
    ...     soup=soup,
    ...     idref="chapter15",
    ... )
    >>> item.tag
    <itemref idref="chapter15"/>

    Create from existing tag:

    >>> soup = bs4.BeautifulSoup("<itemref idref='chapter15' id='chapter15' />", "xml")
    >>> tag = soup.find("itemref")
    >>> item = SpineItemRef.from_tag(soup, tag)
    >>> item.tag is tag
    True
    >>> item.idref
    'chapter15'

    Args:
        soup: The BeautifulSoup object to use for creating XML tags.
        idref: The ID of the item in the manifest.
        id: The ID of the itemref element. Defaults to None.
        linear: Whether the item is part of the linear reading order. Defaults
            to None, which means it is linear (set to false to make it
            non-linear).
        properties: A space-separated list of properties for the itemref.
    """

    idref: Annotated[EPUBId, XMLAttribute()]
    id: Annotated[str | None, XMLAttribute()] = None
    linear: Annotated[bool | None, XMLAttribute()] = None

    tag_name: ClassVar[str] = "itemref"

    @property
    def pk(self) -> EPUBId:
        return self.idref

    @override
    def create_tag(self) -> None:
        super().create_tag()
        if self.linear:
            del self.tag["linear"]

    @override
    def __post_init__(self) -> None:
        super().__post_init__()
        self.idref = EPUBId(self.idref)


class BookSpine(XMLParent[SpineItemRef]):
    """
    The EPUB spine, which defines the linear reading order of the book.

    Typical usage is from an EPUB object:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     print(book.spine[0].idref)
    chapter1

    Args:
        soup: The BeautifulSoup object of which this spine is part of.
        tag: The BeautifulSoup Tag object representing the spine. If not given,
            a new tag will be created.
    """

    tag_name: ClassVar[str] = "spine"
    default_item_type: type[SpineItemRef] = SpineItemRef

    @override
    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        idref: str | EPUBId,
        id: str | None = None,
        linear: bool | None = None,
        properties: str | None = None,
    ):
        """
        Add a new item to the spine.

        Args:
            idref: The ID of the item in the manifest.
            id: The ID of the itemref element. Defaults to None.
            linear: Whether the item is part of the linear reading order. Defaults
                to None, which means it is linear (set to false to make it
                non-linear).
            properties: A space-separated list of properties for the itemref.
        """
        __ = self.add(idref=idref, id=id, linear=linear, properties=properties)

    @override
    def insert(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        position: int,
        idref: str | EPUBId,
        id: str | None = None,
        linear: bool | None = None,
        properties: str | None = None,
    ):
        """
        Insert a new item at the given position in the spine.

        Args:
            position: The position to insert the item at.
            idref: The ID of the item in the manifest.
            id: The ID of the itemref element. Defaults to None.
            linear: Whether the item is part of the linear reading order. Defaults
                to None, which means it is linear (set to false to make it
                non-linear).
            properties: A space-separated list of properties for the itemref.
        """
        __ = self.insert(position, idref, id, linear, properties)

    def get_position(self, idref: str | EPUBId) -> int | None:
        """
        Get the position of the item with the given ID in the spine.

        Args:
            idref: The ID of the item to be searched for in the manifest.

        Returns:
            The position of the item in the spine, or None if not found.
        """
        return next(
            (i for i, item in enumerate(self.items) if item.idref == idref), None
        )

    @override
    def remove(self, idref: str | EPUBId) -> None:  # type: ignore[reportIncompatibleMethodOverride]
        """
        Remove the item with the given ID from the spine, if it exists.

        Args:
            idref: The ID of the item to be removed from the manifest.
        """
        self.remove_item(self[idref])

    def _move_tag(self, item: SpineItemRef, new_position: int) -> None:
        tags = list(self.tag.find_all("itemref"))
        successor = tags[new_position]
        actual_new_position = self.tag.index(successor)

        __ = item.tag.extract()
        __ = self.tag.insert(actual_new_position, item.tag)

    def move_item(
        self,
        item: int | str | EPUBId | SpineItemRef,
        new_position: int,
    ) -> None:
        """
        Move the given item to a new position in the spine.

        Args:
            item: The item to be moved, specified by its index, ID, or SpineItemRef.
            new_position: The new position for the item.

        Raises:
            EPUBError: If the item is not found in the spine.
        """

        try:
            if isinstance(item, (str, int)):
                item = self[item]
            elif item not in self.items:
                raise KeyError
        except KeyError as error:
            raise EPUBError(f"Item {item} not in spine") from error

        self._items.remove(item)
        self._items.insert(new_position, item)
        self._move_tag(item, new_position)

    def reorder(self, items: Sequence[SpineItemRef]) -> None:
        """
        Reorder the spine items to match the given list.

        Args:
            items: The new order of spine items.

        Raises:
            EPUBError: If the new items do not match the current spine items,
                or if there are duplicates in the new items.
        """
        new_items_set = {item.idref for item in items}
        curr_items_set = {item.idref for item in self.items}

        if len(new_items_set) != len(items):
            raise EPUBError("Duplicate items in new order")

        if new_items_set != curr_items_set:
            raise EPUBError("Items do not match current spine items")

        self._items: list[SpineItemRef] = list(items)

        self.tag.clear()
        for item in items:
            __ = self.tag.append(item.tag)
