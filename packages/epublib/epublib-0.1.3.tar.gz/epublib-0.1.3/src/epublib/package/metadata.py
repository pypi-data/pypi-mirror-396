from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, ClassVar, Self, cast, overload, override

import bs4

from epublib.exceptions import EPUBError, warn
from epublib.media_type import MediaType
from epublib.package.properties import WithProperties
from epublib.util import attr_to_str, datetime_to_str
from epublib.xml_element import (
    AttributeValue,
    SyncType,
    XMLAttribute,
    XMLElement,
    XMLParent,
)


@dataclass(kw_only=True)
class MetadataItem(XMLElement, ABC):
    """Abstract base class for EPUB metadata items."""

    @property
    @abstractmethod
    def pk(self) -> str:
        """
        The primary key of this metadata item, used to identify it within
        the metadata collection.
        """

    @classmethod
    def detect(
        cls, soup: bs4.BeautifulSoup, tag: bs4.Tag
    ) -> "LinkMetadataItem | DublinCoreMetadataItem | OPF2MetadataItem | GenericMetadataItem":
        """
        Detect the type of metadata item represented by the given tag and
        return an instance of the appropriate subclass.

        Args:
            soup: The BeautifulSoup object of which the tag (see below) is part of.
            tag: The tag to detect the type of.

        Returns:
            An instance of the appropriate subclass of MetadataItem.

        Raises:
            EPUBError: If the tag does not represent a valid metadata item.
        """

        if tag.name == "link" and tag.get("href"):
            return LinkMetadataItem.from_tag(soup, tag)
        if tag.prefix == "dc":
            return DublinCoreMetadataItem.from_tag(soup, tag)
        if tag.name == "meta" and tag.get("content"):
            return OPF2MetadataItem.from_tag(soup, tag)
        if tag.name == "meta" and tag.get("property") and tag.string:
            return GenericMetadataItem.from_tag(soup, tag)
        raise EPUBError(f"{tag.name} is not a metadata item")


@dataclass(kw_only=True)
class LinkMetadataItem(WithProperties, MetadataItem):
    """
    A link metadata item, used for linking to resources.

    Example:

    >>> import bs4
    >>> soup = bs4.BeautifulSoup("", "xml")
    >>> item = LinkMetadataItem(
    ...     soup=soup,
    ...     href="https://example.com",
    ...     media_type="text/html",
    ... )
    >>> item.tag
    <link href="https://example.com" media-type="text/html"/>

    Args:
        soup: The BeautifulSoup root
        href: The URL of the linked resource.
        hreflang: The language of the linked resource. Defaults to None.
        media_type: The media type of the linked resource. Defaults to None.
        refines: A URI reference to the metadata item that this link refines.
            Defaults to None.
        rel: The relationship of the linked resource to the current document.
            Defaults to None.
        properties: A space-separated list of properties for the link. Defaults
            to None.
    """

    href: Annotated[str, XMLAttribute()]
    hreflang: Annotated[str | None, XMLAttribute()] = None
    media_type: Annotated[str | None, XMLAttribute("media-type")] = None
    refines: Annotated[str | None, XMLAttribute()] = None
    rel: Annotated[str | None, XMLAttribute()] = None

    tag_name: ClassVar[str] = "link"

    @property
    @override
    def pk(self) -> str:
        """
        The primary key of this metadata item, which is the href attribute.
        """
        return self.href

    @classmethod
    @override
    def from_tag(  # type: ignore[reportIncompatibleMethodOverride]
        cls,
        soup: bs4.BeautifulSoup,
        tag: bs4.Tag,
    ) -> Self:
        """
        Create a LinkMetadataItem from an existing BeautifulSoup tag.

        >>> import bs4
        >>> soup = bs4.BeautifulSoup('<link href="https://example.com" media-type="text/html"/>', "xml")
        >>> tag = soup.find("link")
        >>> item = LinkMetadataItem.from_tag(soup, tag)
        >>> item.href
        'https://example.com'
        """

        if not tag.name == "link" or not tag["href"]:
            raise EPUBError(f"{tag.name} is not generic metadata item")

        return super().from_tag(soup, tag)


@dataclass(kw_only=True)
class ValuedMetadataItem(MetadataItem, ABC):
    """
    Abstract base class for all metadata items that have a value (i.e.,
    all except LinkMetadataItem).

    Typically accessed from an EPUB instance via its `metadata` attribute.

    >>> from epublib import EPUB
    >>> with EPUB() as book:
    ...     book.metadata.title = "My Book"
    ...     valued_item = book.metadata.get_valued("title")
    ...     # Equivalent to the following (but less specific type hints):
    ...     item = book.metadata["title"]
    >>> valued_item.value
    'My Book'
    """

    name: str
    value: str
    id: Annotated[str | None, XMLAttribute()] = None

    @property
    @override
    def pk(self) -> str:
        return self.name


@dataclass(kw_only=True)
class DublinCoreMetadataItem(ValuedMetadataItem):
    """
    A Dublin Core metadata item.

    Typical usage is from an EPUB instance via its `metadata` attribute:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     item = book.metadata.get("title")
    ...     item.value = "A book"
    >>> item.tag
    <dc:title>A book</dc:title>
    >>> item.value
    'A book'
    """

    name: Annotated[str, XMLAttribute(sync=SyncType.NAME, prefix="dc")]
    value: Annotated[str, XMLAttribute(sync=SyncType.STRING)]
    dir: Annotated[str | None, XMLAttribute()] = None
    lang: Annotated[str | None, XMLAttribute("xml:lang")] = None

    @override
    def get_tag_name(self) -> str:
        return f"dc:{self.pk}"

    @classmethod
    @override
    def from_tag(  # type: ignore[reportIncompatibleMethodOverride]
        cls,
        soup: bs4.BeautifulSoup,
        tag: bs4.Tag,
    ) -> Self:
        """
        Create a DublinCoreMetadataItem from an existing BeautifulSoup tag.

        >>> import bs4
        >>> soup = bs4.BeautifulSoup('''
        ...     <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        ...         <dc:publisher>João da Silva</dc:publisher>
        ...     </metadata>''',
        ...     "xml",
        ... )
        >>> tag = soup.find("publisher")
        >>> item = DublinCoreMetadataItem.from_tag(soup, tag)
        >>> item.value
        'João da Silva'
        """
        if not tag.prefix == "dc":
            raise EPUBError(f"{tag.name} is no Dublin Core metadata item")

        return super().from_tag(soup, tag)


@dataclass(kw_only=True)
class OPF2MetadataItem(ValuedMetadataItem):
    """
    An OPF2 metadata item.

    Typical usage is from an EPUB instance via its `metadata` attribute.:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     item = book.metadata.add_opf("cover", "image2")
    >>> item.tag
    <meta content="image2" name="cover"/>
    >>> item.value
    'image2'
    """

    name: Annotated[str, XMLAttribute()]
    value: Annotated[str, XMLAttribute("content")]

    tag_name: ClassVar[str] = "meta"

    @classmethod
    @override
    def from_tag(cls, soup: bs4.BeautifulSoup, tag: bs4.Tag, **kwargs: str) -> Self:
        """
        Create an OPF2MetadataItem from an existing BeautifulSoup tag.

        >>> import bs4
        >>> soup = bs4.BeautifulSoup('<meta content="image2" name="cover"/>', "xml")
        >>> tag = soup.find("meta")
        >>> item = OPF2MetadataItem.from_tag(soup, tag)
        >>> item.value
        'image2'
        """
        if (
            tag.name != "meta"
            or tag.prefix not in [None, "opf"]
            or not (tag.get("content") and tag.get("name"))
        ):
            raise EPUBError(f"{tag.name} is not OPF2 metadata item")

        return super().from_tag(soup, tag, **kwargs)


@dataclass(kw_only=True)
class GenericMetadataItem(ValuedMetadataItem):
    """
    A generic metadata item.

    Typical usage is from an EPUB instance via its `metadata` attribute.:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     item = book.metadata.add("mymetadata", "myvalue")
    >>> item.tag
    <meta property="mymetadata">myvalue</meta>
    >>> item.value
    'myvalue'
    """

    value: Annotated[str, XMLAttribute(sync=SyncType.STRING)]
    name: Annotated[str, XMLAttribute("property")]
    dir: Annotated[str | None, XMLAttribute()] = None
    lang: Annotated[str | None, XMLAttribute("xml:lang")] = None
    refines: Annotated[str | None, XMLAttribute()] = None
    scheme: Annotated[str | None, XMLAttribute()] = None

    tag_name: ClassVar[str] = "meta"

    @override
    def create_tag(self) -> None:
        super().create_tag()
        self.tag.string = self.value

    @classmethod
    @override
    def from_tag(
        cls,
        soup: bs4.BeautifulSoup,
        tag: bs4.Tag,
        **kwargs: AttributeValue,
    ) -> Self:
        """
        Create an GenericMetadataItem from an existing BeautifulSoup tag.

        >>> import bs4
        >>> soup = bs4.BeautifulSoup('<meta property="mymetadata">myvalue</meta>', "xml")
        >>> tag = soup.find("meta")
        >>> item = GenericMetadataItem.from_tag(soup, tag)
        >>> item.value
        'myvalue'
        """
        if not tag.name == "meta" or not tag.get("property"):
            raise EPUBError(f"{tag.name} is not generic metadata item")

        return super().from_tag(soup, tag, **kwargs)


class BookMetadata(XMLParent[MetadataItem]):
    """
    The EPUB metadata, which contains information about the book.

    Typical usage is from an `EPUB` object:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     book.metadata.title = "A book"
    ...     book.metadata.language = "en"
    ...     book.metadata.identifier = "urn:isbn:9780000000000"
    ...     book.metadata.modified = datetime.now()
    ...     item = book.metadata.add("mycustommeta", "myvalue")
    >>> item.tag
    <meta property="mycustommeta">myvalue</meta>

    But can be created directly as well:

    >>> metadata = BookMetadata(soup=bs4.BeautifulSoup("", "xml"))
    >>> metadata
    BookMetadata(0 items)
    >>> metadata.add_dc("publisher", "João da Silva Inc.")
    DublinCoreMetadataItem(name='publisher', value='João da Silva Inc.', ...)

    Args:
        soup: The BeautifulSoup object of which this manifest is part of.
        tag: The tag representing this metadata. If not given, a new tag
            will be created.
    """

    default_item_type: type[MetadataItem] = MetadataItem
    tag_name: ClassVar[str] = "metadata"

    @override
    def parse_items(self) -> list[MetadataItem]:
        items: list[MetadataItem] = []

        for tag in self.tag.find_all(True, recursive=False):
            try:
                items.append(MetadataItem.detect(self.soup, tag))
            except EPUBError:
                warn(f"Couldn't parse metadata item {tag}")

        return items

    @overload
    def add[T: ValuedMetadataItem](self, name: str, value: str, cls: type[T]) -> T: ...

    @overload
    def add(self, name: str, value: str) -> GenericMetadataItem: ...

    def add(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        name: str,
        value: str,
        cls: type[ValuedMetadataItem] = GenericMetadataItem,
    ) -> ValuedMetadataItem:
        """
        Create a new valued metadata item with the given name and value and add
        it to this book metadata.

        Args:
            name: The name of the metadata item to add.
            value: The value of the metadata item to add.
            cls: The class of the metadata item to add. Defaults to
                GenericMetadataItem.

        Returns:
            The newly added metadata item.
        """
        item = cls(soup=self.soup, name=name, value=value)
        __ = self.add_item(item)

        return item

    def add_dc(
        self,
        name: str,
        value: str,
        id: str | None = None,
        dir: str | None = None,
        lang: str | None = None,
    ) -> DublinCoreMetadataItem:
        """
        Create a new Dublin Core metadata item with the given name and value and
        add it to this book metadata.

        Args:
            name: The name of the metadata item to add.
            value: The value of the metadata item to add.
            id: The id of the metadata item to add. Defaults to None.
            dir: The text direction of the metadata item to add. Defaults to None.
            lang: The language of the metadata item to add. Defaults to None.

        Returns:
            The newly added Dublin Core metadata item.
        """
        item = DublinCoreMetadataItem(
            soup=self.soup,
            name=name,
            value=value,
            id=id,
            dir=dir,
            lang=lang,
        )
        __ = self.add_item(item)
        return item

    def add_opf(self, name: str, value: str, id: str | None = None) -> OPF2MetadataItem:
        """
        Create a new OPF2 metadata item with the given name and value and add it
        to this book metadata.

        Args:
            name: The name of the metadata item to add.
            value: The value of the metadata item to add.
            id: The id of the metadata item to add. Defaults to None.

        Returns:
            The newly added OPF2 metadata item.
        """
        item = OPF2MetadataItem(soup=self.soup, name=name, value=value, id=id)
        __ = self.add_item(item)
        return item

    def add_link(
        self,
        href: str,
        hreflang: str | None = None,
        media_type: str | MediaType | None = None,
        properties: list[str] | None = None,
        refines: str | None = None,
        rel: str | None = None,
    ) -> LinkMetadataItem:
        """
        Create a new link metadata item with the given attributes and add it to
        this book metadata.

        Args:
            href: The URL of the linked resource.
            hreflang: The language of the linked resource. Defaults to None.
            media_type: The media type of the linked resource. Defaults to None.
            properties: A space-separated list of properties for the link.
                Defaults to None.
            refines: A URI reference to the metadata item that this link refines.
                Defaults to None.
            rel: The relationship of the linked resource to the current document.
                Defaults to None.

        Returns:
            The newly added link metadata item.
        """
        item = LinkMetadataItem(
            soup=self.soup,
            href=href,
            hreflang=hreflang,
            media_type=MediaType(media_type).value,
            properties=properties,
            refines=refines,
            rel=rel,
        )
        return cast(LinkMetadataItem, self.add_item(item))

    def get_valued(self, name: str) -> ValuedMetadataItem | None:
        """
        Get the first metadata that has a value (i.e. all kinds except
        LinkMetadataItem) item with the given name.

        Args:
            name: The name of the metadata item to get.

        Returns:
            The first metadata item with the given name, or None if not found.
        """
        return self.get(name, ValuedMetadataItem)

    @property
    def identifier(self) -> str | None:
        """
        The book's unique identifier as a string, or None if not set.
        """
        item = self.get("identifier")
        if item and isinstance(item, DublinCoreMetadataItem):
            return item.value
        return None

    @identifier.setter
    def identifier(self, value: str) -> None:
        item = self.get("identifier")

        package = self.tag.parent
        unique_identifier = None
        if package and package.name == "package" and package.get("unique-identifier"):
            unique_identifier = attr_to_str(package["unique-identifier"])

        if item and isinstance(item, DublinCoreMetadataItem):
            item.value = value
            if unique_identifier:
                item.tag["id"] = unique_identifier
            return

        item = DublinCoreMetadataItem(
            soup=self.soup,
            name="identifier",
            value=value,
        )
        if unique_identifier:
            item.tag["id"] = unique_identifier

        __ = self.add_item(item)

    @property
    def title(self) -> str | None:
        """
        The book's title as a string, or None if not set.
        """
        item = self.get("title")
        if item and isinstance(item, DublinCoreMetadataItem):
            return item.value
        return None

    @title.setter
    def title(self, value: str) -> None:
        item = self.get("title")
        if item and isinstance(item, DublinCoreMetadataItem):
            item.value = value
            return

        item = DublinCoreMetadataItem(soup=self.soup, name="title", value=value)
        __ = self.add_item(item)

    @property
    def language(self) -> str | None:
        """
        The book's language as a string, or None if not set.
        """
        item = self.get("language")
        if item and isinstance(item, DublinCoreMetadataItem):
            return item.value
        return None

    @language.setter
    def language(self, value: str) -> None:
        item = self.get("language")
        if item and isinstance(item, DublinCoreMetadataItem):
            item.value = value
            return

        item = DublinCoreMetadataItem(soup=self.soup, name="language", value=value)
        __ = self.add_item(item)

    @property
    def modified(self) -> datetime | None:
        """
        The book's last modified date as a datetime object, or None if not set
        or if the value is not a valid ISO 8601 date.
        """
        item = self.get("dcterms:modified")
        if item and isinstance(item, GenericMetadataItem):
            try:
                return datetime.fromisoformat(item.value)
            except ValueError:
                return None
        return None

    @modified.setter
    def modified(self, value: datetime) -> None:
        str_value = datetime_to_str(value)

        item = self.get("dcterms:modified")
        if item and isinstance(item, GenericMetadataItem):
            item.value = str_value
            return

        item = GenericMetadataItem(
            soup=self.soup,
            name="dcterms:modified",
            value=str_value,
        )
        __ = self.add_item(item)
