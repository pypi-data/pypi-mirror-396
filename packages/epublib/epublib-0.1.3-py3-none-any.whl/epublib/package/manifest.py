import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, ClassVar, Literal, SupportsIndex, overload, override

import bs4

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.media_type import MediaType
from epublib.package.properties import WithProperties
from epublib.package.spine import SpineItemRef
from epublib.resources import Resource
from epublib.util import attr_to_str, strip_fragment
from epublib.xml_element import (
    HrefElement,
    ParentOfHref,
    XMLAttribute,
)


def detect_remote_resources(soup: bs4.BeautifulSoup) -> bool:
    for attr in "src", "href":
        for tag in soup.find_all(attrs={attr: True}):
            ref = attr_to_str(tag.get(attr))
            if ref is not None:
                if re.search(r"^\w+://.*$", ref):
                    return True

                if ref.startswith("/"):
                    return True

    return False


def detect_manifest_properties(soup: bs4.BeautifulSoup) -> list[str]:
    properties: list[str] = []

    if soup.find("math"):
        properties.append("mathml")

    if detect_remote_resources(soup):
        properties.append("remote-resources")

    if soup.find("script"):
        properties.append("scripted")

    if soup.find("epub:switch"):
        properties.append("switch")

    return properties


@dataclass(kw_only=True)
class ManifestItem(WithProperties, HrefElement):
    """
    An item in the EPUB manifest. Filename (absolute path) and href (relative
    path) are kept in sync.

    Creating item with specific attributes:

    >>> from epublib.media_type import MediaType
    >>> soup = bs4.BeautifulSoup("", "xml")
    >>> item = ManifestItem(
    ...     soup=soup,
    ...     filename="chapter15.xhtml",
    ...     id="chapter15",
    ...     media_type=MediaType.XHTML,
    ...     own_filename="base/content.opf"
    ... )
    >>> item.tag
    <item href="../chapter15.xhtml" ...>

    Creating item from tag:

    >>> soup = bs4.BeautifulSoup(
    ...     "<item href='chapter15.xhtml' id='chapter15' media-type='application/xhtml+xml'/>",
    ...     "xml"
    ... )
    >>> tag = soup.find("item")
    >>> item = ManifestItem.from_tag(soup, tag, own_filename="base/content.opf")
    >>> item.tag is tag
    True

    Args:
        soup: The BeautifulSoup object of wich this item is part of.
        filename: The filename of the resource this item references. If not
            given, will be derived from `href` and `own_filename`.
        href: The href of the resource this item references. If not given,
            it will be derived from `filename` and `own_filename`. At least one
            of `filename` and `href` should be provided
        id: The unique identifier of this item.
        media_type: The media type of the resource this item references.
        fallback: The id of the item that is the fallback for this item, if any.
            defaults to None.
        media_overlay: The id of the item that is the media overlay for this item,
            if any. defaults to None.
        properties: A list of properties for this item, if any. defaults to None.
    """

    id: Annotated[EPUBId, XMLAttribute()]
    media_type: Annotated[str, XMLAttribute("media-type")]
    fallback: Annotated[str | None, XMLAttribute()] = None
    media_overlay: Annotated[str | None, XMLAttribute("media-overlay")] = None

    tag_name: ClassVar[str] = "item"


type ItemIdentifier = str | Path | Resource | SpineItemRef | EPUBId


class BookManifest(ParentOfHref[ManifestItem]):
    """
    The EPUB manifest, which is a container of all resources in the book.

    Typical usage is from an `EPUB` object:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     item = book.manifest.items[0]
    ...     item = book.manifest["Text/chapter1.xhtml"]
    ...     item = book.manifest.get(EPUBId("chapter1"))
    ...     print(item.id, item.filename, item.media_type)
    chapter1 Text/chapter1.xhtml application/xhtml+xml

    But can be created directly as well:

    >>> manifest = BookManifest(soup=bs4.BeautifulSoup("", "xml"), own_filename="content.opf")
    >>> manifest
    BookManifest(0 items)
    >>> manifest.add("chapter15.xhtml", id="chapter15")
    ManifestItem(filename='chapter15.xhtml', ..., id='chapter15', ...)
    >>> manifest[0].media_type
    'application/xhtml+xml'

    Args:
        soup: The BeautifulSoup object of which this manifest is part of.
        tag: The tag representing this manifest. If not given, a new tag
            will be created.
        own_filename: The filename of the package document containing this
            manifest.
    """

    tag_name: ClassVar[str] = "manifest"

    def __post_init__(self) -> None:
        super().__post_init__()
        self._cover_image: ManifestItem | None = None

    @property
    def nav(self) -> ManifestItem:
        """
        Return the navigation document item, i.e. the only item containing the
        "nav" property.

        Raises:
            EPUBError: If no navigation document is found in the manifest.
        """
        try:
            return next(
                (
                    item
                    for item in self.items
                    if item.properties and "nav" in item.properties
                ),
            )
        except StopIteration as error:
            raise EPUBError("No navigation document found in manifest") from error

    @property
    def cover_image(self) -> ManifestItem | None:
        """
        Return the cover image item, i.e. the item containing the "cover-image"
        property, or None if no such item exists.
        """
        return next(
            (
                item
                for item in self.items
                if item.properties and "cover-image" in item.properties
            ),
            None,
        )

    @override
    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        filename: str | Path,
        id: EPUBId | None = None,
        media_type: MediaType | str | None = None,
        fallback: str | None = None,
        media_overlay: str | None = None,
        properties: list[str] | None = None,
    ) -> ManifestItem:
        """
        Create a new manifest item and add it to the manifest.

        Args:
            filename: The filename of the resource to add.
            id: The unique identifier of the item. If not given, it will be
                generated from the filename.
            media_type: The media type of the resource. If not given, it will be
                guessed from the filename.
            fallback: The id of the item that is the fallback for this item, if any.
                defaults to None.
            media_overlay: The id of the item that is the media overlay for this item,
                if any. defaults to None.
            properties: A list of properties for this item, if any. defaults to None.

        Returns:
            The created and added item.

        Raises:
            EPUBError: If the media type could not be detected, or if an item with
                the same id or filename already exists in the manifest.
        """

        media_type = MediaType.from_filename(filename)
        if not media_type:
            raise EPUBError(f"Could not detect media type for {filename}")

        id = self.get_new_id(filename) if not id else id

        item = ManifestItem(
            soup=self.soup,
            filename=str(filename),
            own_filename=self.own_filename,
            media_type=str(media_type),
            id=id,
            fallback=fallback,
            media_overlay=media_overlay,
            properties=properties,
        )
        return self.add_item(item)

    @override
    def add_item(self, item: ManifestItem) -> ManifestItem:
        """
        Add an item to the manifest.

        Args:
            item: The item to add.

        Returns:
            The added item.

        Raises:
            EPUBError: If item itself or another item with the same id or
            filename already exists in the manifest.
        """

        if item in self.items:
            raise EPUBError(f"Item {item} is already in the manifest")

        if any(
            item.id == other.id or item.filename == other.filename
            for other in self.items
        ):
            if any(item.id == other.id for other in self.items):
                raise EPUBError(f"An item with id {item.id} is already in the manifest")

            if any(item.filename == other.filename for other in self.items):
                raise EPUBError(
                    f"An item with filename {item.filename} is already in the manifest"
                )

        return super().add_item(item)

    @overload
    def _get_by_id(self, id: EPUBId, raise_error: Literal[True]) -> ManifestItem: ...

    @overload
    def _get_by_id(
        self,
        id: EPUBId,
        raise_error: bool = False,
    ) -> ManifestItem | None: ...

    def _get_by_id(self, id: EPUBId, raise_error: bool = False) -> ManifestItem | None:
        try:
            return next(item for item in self.items if item.id == id)
        except StopIteration as exception:
            if raise_error:
                raise KeyError(id) from exception
            return None

    @override
    def __getitem__(
        self,
        name: ItemIdentifier | SupportsIndex,
    ):
        if isinstance(name, SupportsIndex):
            return super().__getitem__(name)

        value = self.get(name)
        if value is None:
            raise KeyError(name)
        return value

    @override
    def get(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        name: ItemIdentifier,
        ignore_fragment: bool = True,
    ) -> ManifestItem | None:
        """
        Get an item from the manifest by its filename, id, corresponding spine
        item or corresponding resource.

        Args:
            name: The identifier of the item to get. Can be a filename (str or
                Path), an EPUBId, a SpineItemRef or a Resource.
            ignore_fragment: Whether to ignore URL fragments when looking for
                the item. Defaults to True.

        Returns:
            The found item, or None if no such item exists.
        """
        if isinstance(name, (EPUBId, SpineItemRef)):
            if isinstance(name, SpineItemRef):
                name = name.idref
            item = self._get_by_id(name, raise_error=False)
            if item is None:
                return None
            name = item.filename

        elif isinstance(name, Resource):
            name = name.filename

        if ignore_fragment:
            name = strip_fragment(name)

        return super().get(str(name), ignore_fragment=False)

    @override
    def remove(self, filename: ItemIdentifier, ignore_fragment: bool = True) -> None:
        """
        Remove an item from the manifest, if it exists, looking it up by its
        filename, id, corresponding spine item or corresponding resource.

        Args:
            filename: The identifier of the item to remove. Can be a filename
                (str or Path), an EPUBId, a SpineItemRef or a Resource.
            ignore_fragment: Whether to ignore URL fragments when looking for
                the item. Defaults to True.

        Returns:
            The removed item, or None if no such item existed.
        """
        item = self.get(filename, ignore_fragment=ignore_fragment)
        if item:
            return self.remove_item(item)
