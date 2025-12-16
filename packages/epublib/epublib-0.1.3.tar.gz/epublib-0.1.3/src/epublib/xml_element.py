import dataclasses
import enum
import inspect
import typing
from abc import ABC
from collections.abc import Generator, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from functools import cache
from pathlib import Path
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    ForwardRef,
    Protocol,
    Self,
    SupportsIndex,
    cast,
    get_args,
    overload,
    override,
    runtime_checkable,
)

import bs4

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.util import (
    attr_to_str,
    datetime_to_str,
    get_absolute_href,
    get_actual_tag_position,
    get_relative_href,
    new_id_in_tag,
    parse_int,
    remove_optional_type,
    split_fragment,
    strip_fragment,
    strip_type_parameters,
)

type AttributeValue = str | datetime | bool | list[str] | EPUBId | int


_sentinel_tag = bs4.BeautifulSoup("", "xml").new_tag("sentinel")


class SyncType(enum.Enum):
    ATTR = enum.auto()  # Sync with tag attribute
    STRING = enum.auto()  # sync with tag string
    NAME = enum.auto()  # sync with tag name


@dataclass
class XMLAttribute:
    """
    Represents the relation between the attribute of a XML tag and its
    representation in an object.

    This class is used as metadata for dataclass fields, in combination
    with typing.Annotated.

    >>> @dataclass(kw_only=True)
    ... class MyElement(XMLElement):
    ...     my_attr: Annotated[str, XMLAttribute(init_name="my-attr", sync=SyncType.ATTR)] = ""

    Args:
        init_name: Name of the attribute in the XML. If None, the name of
            the dataclass field is used, with underscores replaced by
            hyphens.
        sync: How to sync this attribute with the XML tag. One of:
            - SyncType.ATTR: Sync with a tag attribute
            - SyncType.STRING: Sync with the tag string
            - SyncType.NAME: Sync with the tag name
        get: A tag name or callable to get the relevant tag from the parent tag.
            If None, the parent tag is used.
        create: A tag name or callable to create the relevant tag if it
            does not exist. If None, no tag is created.
        prefix: The namespace prefix to use when creating a new tag.
            Only used if `create` is SyncType.Name.
    """

    init_name: str | None = None
    name: str = dataclasses.field(init=False, repr=False)
    sync: SyncType = SyncType.ATTR
    get: str | Callable[[bs4.Tag], bs4.Tag | None] | None = None
    create: str | Callable[[bs4.BeautifulSoup, bs4.Tag], bs4.Tag] | None = None
    prefix: str = ""
    typ: type[AttributeValue] = dataclasses.field(init=False, repr=False)
    init: bool = dataclasses.field(init=False, repr=False)

    def __post_init__(self) -> None:
        pass

    def get_tag(self, tag: bs4.Tag) -> bs4.Tag | None:
        if self.get is None:
            return tag

        if isinstance(self.get, str):
            return tag.select_one(f"& > {self.get}")

        return self.get(tag)

    def create_tag(self, soup: bs4.BeautifulSoup, tag: bs4.Tag) -> bs4.Tag:
        if self.create is None:
            return tag

        if isinstance(self.create, str):
            new_tag = soup.new_tag(self.create)
            __ = tag.insert(0, new_tag)
            return new_tag

        return self.create(soup, tag)


@runtime_checkable
class _XMLAttributeMetadataProtocol(Protocol):
    __metadata__: tuple[XMLAttribute, ...]
    __origin__: type[AttributeValue]


@dataclass
class BaseElement[S: bs4.BeautifulSoup = bs4.BeautifulSoup](ABC):
    """
    Abstract base class for an XML element. Responsible for creating
    the tag if it does not exist.

    Args:
        soup: The BeautifulSoup this object is part of.
        tag: The existing tag to use. If not provided, a new tag is created.
    """

    soup: S = dataclasses.field(repr=False)
    tag: bs4.Tag = dataclasses.field(default=_sentinel_tag, repr=False)

    tag_name: ClassVar[str]

    def __post_init__(self) -> None:
        if self.tag is _sentinel_tag:
            self.create_tag()

    def create_tag(self) -> None:
        """
        Create a new tag for this element.
        """
        self.tag = self.soup.new_tag(self.get_tag_name())

    def get_tag_name(self) -> str:
        """
        Return the tag name for this element.
        """
        try:
            return self.tag_name
        except AttributeError as error:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define a class variable "
                "`tag_name` with the name of the XML tag, or override the "
                "`get_tag_name` method."
            ) from error


@dataclass(kw_only=True)
class XMLElement[S: bs4.BeautifulSoup = bs4.BeautifulSoup](
    BaseElement[S],
    ABC,
):
    """
    Abstract base class for an XML element. Responsible for syncing object
    and tag, and exposing important tag attributes as convenient
    instance attributes.

    This class uses dataclass fields annotated with typing.Annotated
    and XMLAttribute metadata to determine which attributes to sync.
    """

    __cached_attributes: ClassVar[dict[type[Self], dict[str, XMLAttribute]]] = {}

    @classmethod
    def _get_attributes(cls) -> dict[str, XMLAttribute]:
        """
        Infer XML attributes from dataclass fields.
        """
        if cls.__cached_attributes.get(cls):
            return cls.__cached_attributes[cls]

        attributes: dict[str, XMLAttribute] = {}
        for field in dataclasses.fields(cls):
            if (
                typing.get_origin(field.type) is Annotated
                and isinstance(field.type, _XMLAttributeMetadataProtocol)
                and field.type.__metadata__
            ):
                attribute = field.type.__metadata__[0]
                attribute.name = (
                    field.name.replace("_", "-")
                    if attribute.init_name is None
                    else attribute.init_name
                )
                attribute.typ = strip_type_parameters(field.type.__origin__)
                attribute.init = field.init
                attributes[field.name] = attribute

        cls.__cached_attributes[cls] = attributes
        return attributes

    @override
    def __setattr__(self, name: str, value: AttributeValue | None) -> None:
        """
        Set an attribute and update the tag accordingly.
        """

        ret = super().__setattr__(name, value)
        self.update_tag(name, value)
        return ret

    @override
    def create_tag(self) -> None:
        super().create_tag()
        for name in self._get_attributes().keys():
            self.update_tag(name, cast(AttributeValue | None, getattr(self, name)))

    def update_tag(self, name: str, value: AttributeValue | None) -> None:
        """
        Update the tag to reflect the current value of the attribute.

        Args:
            name: The name of the attribute to update.
            value: The current value of the attribute.
        """
        if self.tag is _sentinel_tag:
            return

        attribute = self._get_attributes().get(name)
        if attribute is None:
            return

        value = self.attribute_to_str(name, value) if value is not None else None

        tag = attribute.get_tag(self.tag)
        if tag is None and value is not None:
            tag = attribute.create_tag(self.soup, self.tag)

        if tag is None:
            return

        match attribute.sync:
            case SyncType.ATTR:
                if value is None:
                    del tag[attribute.name]
                else:
                    tag[attribute.name] = value
            case SyncType.STRING:
                if value is None and tag is not self.tag:
                    tag.decompose()
                else:
                    tag.string = "" if value is None else value
            case SyncType.NAME:
                if not value:
                    raise EPUBError(
                        f"{self.__class__.__name__}.{name} cannot be empty or None"
                    )

                self.tag.name = value
                if attribute.prefix:
                    self.tag.prefix = attribute.prefix

    @classmethod
    def _read_from_tag(
        cls,
        tag: bs4.Tag,
        attribute: XMLAttribute,
    ) -> str | None:
        tag_or_none = attribute.get_tag(tag)

        if tag_or_none is None:
            return None

        tag = tag_or_none

        match attribute.sync:
            case SyncType.ATTR:
                return attr_to_str(tag.get(attribute.name))
            case SyncType.STRING:
                return tag.get_text()
            case SyncType.NAME:
                return tag.name

    @classmethod
    def from_tag(
        cls,
        soup: S,
        tag: bs4.Tag,
        **kwargs: AttributeValue,
    ) -> Self:
        """
        Create this XMLElement from an existing tag.

        Any attributes that are not represented in the tag are passed as keyword
        arguments.

        Args:
            soup: The BeautifulSoup this element is part of.
            tag: The existing tag to use.
            **kwargs: Any attributes that are not represented in the tag.

        Returns:
            An instance of this XMLElement.
        """
        attributes = cls._get_attributes()
        tag_kwargs = {
            name: cls.str_to_attribute(
                cls._read_from_tag(tag, attribute),
                attribute.typ,
            )
            for name, attribute in attributes.items()
            if attribute.init
        }

        instance = cls(
            soup=soup,
            tag=tag,
            **tag_kwargs,
            **kwargs,
        )

        return instance

    def attribute_to_str(
        self,
        name: str,  # type: ignore[reportUnusedParameter]
        value: AttributeValue,
    ) -> str:
        """
        Convert an attribute of this object to a string suitable for
        XML serialization.

        Args:
            name: The name of the attribute to convert.
            value: The value of the attribute to convert.

        Returns:
            The string representation of the attribute.
        """
        if isinstance(value, datetime):
            return datetime_to_str(value)

        if isinstance(value, bool):
            return "yes" if value else "no"

        if isinstance(value, int):
            return str(value)

        if isinstance(value, list):
            return " ".join(str(el) for el in value)

        return value

    @classmethod
    def str_to_attribute(
        cls,
        value: str | None,
        typ: type[AttributeValue],
    ) -> AttributeValue | None:
        """
        Convert a string from an XML attribute to an attribute of this
        object.

        Args:
            value: The string value to convert.
            typ: The type to convert the string to.

        Returns:
            An instance of the specified type.
        """
        if value is None:
            return None

        typ = remove_optional_type(typ)
        if issubclass(typ, list):
            return value.split()

        if issubclass(typ, datetime):
            return datetime.fromisoformat(value)

        if issubclass(typ, bool):
            return value != "no"

        if issubclass(typ, int):
            return parse_int(value)

        if issubclass(typ, EPUBId):
            return EPUBId(value)

        return str(value)


@dataclass(kw_only=True)
class HrefElement[S: bs4.BeautifulSoup = bs4.BeautifulSoup](XMLElement[S], ABC):
    """
    XMLElement with a reference to a file. This class handles the logic
    of syncing the 'href' (relative filename) and 'filename' (absolute
    filename).

    Args:
        soup: The BeautifulSoup object this element belongs to.
        filename: The absolute filename this element refers to. If not
            provided, it is derived from `href` and `own_filename`. One of `href`
            or `filename` must be provided.
        href: The relative filename this element refers to. If not
            provided, it is derived from `filename` and `own_filename`. On of
            `href` or `filename` must be provided.
        own_filename: The absolute filename of the file this element
            is part of.
    """

    filename: str
    href: Annotated[str, XMLAttribute()] = ""
    own_filename: str

    @property
    def pk(self) -> str:
        return self.filename

    def href_to_filename(self, href: str) -> str:
        return get_absolute_href(self.own_filename, href)

    def filename_to_href(self, filename: str) -> str:
        return get_relative_href(self.own_filename, filename)

    def __post_init__(self) -> None:
        if not self.href and self.filename:
            self.href = self.filename_to_href(self.filename)
        elif not self.filename and self.href:
            self.filename = self.href_to_filename(self.href)

        super().__post_init__()

    @override
    def __setattr__(self, name: str, value: AttributeValue | None) -> None:
        super().__setattr__(name, value)
        if hasattr(self, "own_filename"):
            if name == "filename":
                if not value:
                    super().__setattr__("href", value)
                elif isinstance(value, str | Path):
                    super().__setattr__("href", self.filename_to_href(value))

            elif name == "href":
                if not value:
                    super().__setattr__("filename", value)
                elif isinstance(value, str | Path):
                    super().__setattr__("filename", self.href_to_filename(value))

    @classmethod
    @override
    def from_tag(  # type: ignore[reportIncompatibleMethodOverride]
        cls,
        soup: S,
        tag: bs4.Tag,
        own_filename: str,
        **kwargs: AttributeValue,
    ) -> Self:
        return super().from_tag(
            soup,
            tag,
            filename="",
            own_filename=own_filename,
            **kwargs,
        )


# When generic constraints to generics become supported, we should use this:
# XMLChildProtocol[S: bs4.BeautifulSoup = bs4.BeautifulSoup](Protocol)
#
# And then:
# class XMLParent[S: bs4.BeautifulSoup = bs4.BeautifulSoup, I: XMLChildProtocol[S]](...)


class XMLChildProtocol(Protocol):
    tag: bs4.Tag

    @property
    def pk(self) -> str:
        """
        A primary key that uniquely identifies this element. Used by parent to
        find elements.
        """
        ...

    @classmethod
    def from_tag(
        cls,
        soup: Any,  # type: ignore[reportAny]
        tag: bs4.Tag,
        **kwargs: Any,  # type: ignore[reportAny]
    ) -> Self: ...


@dataclass(kw_only=True)
class XMLParent[I: XMLChildProtocol, S: bs4.BeautifulSoup = bs4.BeautifulSoup](
    BaseElement[S],
    ABC,
):
    """
    Abstract base class for an XML element that contains other XML elements.

    Args:
        soup: The BeautifulSoup this object is part of.
        tag: The existing tag to use. If not provided, a new tag is created.
    """

    def __post_init__(self) -> None:
        super().__post_init__()
        self._items: list[I] = list(self.parse_items())

    @classmethod
    @cache
    def _child_class(cls) -> type[I]:
        try:
            parent_base = next(
                c
                for c in cast(tuple[type[Any], ...], cls.__orig_bases__)  # type: ignore[reportAttributeAccessIssue]
                if issubclass(typing.get_origin(c) or c, XMLParent)
            )
            typ = get_args(parent_base)[0]  # type: ignore[reportAttributeAccessIssue]
            if isinstance(typ, ForwardRef) and typ.__forward_arg__ == cls.__name__:
                return cast(type[I], cls)
            assert inspect.isclass(typ)
            return typ
        except (AttributeError, IndexError, AssertionError, StopIteration):
            raise NotImplementedError(
                f"Cannot determine child class for {cls.__name__}. Specify "
                "the generic type of override _child_class."
            )

    def get_child_tags(self) -> Iterable[bs4.Tag]:
        """
        Return the tags of the children of this element.
        """
        parent_tag = self.parent_tag
        if parent_tag is None:
            return []

        child_tag_name = getattr(self._child_class(), "tag_name", True)

        return parent_tag.find_all(child_tag_name, recursive=False)

    def _get_common_dataclass_attrs(
        self,
        exclude: Sequence[str] = (),
        exclude_tag: bool = False,
        exlcude_soup: bool = False,
        include_self_as_parent: bool = True,
    ) -> dict[str, AttributeValue]:
        child_class = self._child_class()
        child_field_names = {
            field.name
            for field in dataclasses.fields(
                child_class,  # type: ignore[reportArgumentType]
            )
        }

        kwargs = {
            field.name: getattr(self, field.name)
            for field in dataclasses.fields(self)
            if field.name in child_field_names
            and field.name not in exclude
            and (not exclude_tag or field.name != "tag")
            and (not exlcude_soup or field.name != "soup")
        }

        if include_self_as_parent and "parent" in child_field_names:
            kwargs["parent"] = self

        return kwargs

    def parse_items(self) -> Sequence[I]:
        """
        Parse child items from self.tag and return their representations in a list.

        Returns:
            A sequence of child items.
        """
        # This generic implementation will get all tag children of the
        # parent element, and call the _child_class().from_tag method.
        # If there are any dataclass attributes on the child class that
        # have the same name as in this own class, they will be passed
        # to the from_tag method.

        child_class = self._child_class()
        kwargs = self._get_common_dataclass_attrs(exclude_tag=True)

        return [
            child_class.from_tag(tag=tag, **kwargs) for tag in self.get_child_tags()
        ]

    @overload
    def get[J: XMLChildProtocol](self, pk: str, cls: type[J]) -> J | None: ...
    @overload
    def get(self, pk: str, cls: type[I] | None = None) -> I | None: ...

    def get(self, pk: str, cls: type[I] | None = None):
        return next(
            (
                item
                for item in self._items
                if item.pk == pk and (cls is None or isinstance(item, cls))
            ),
            None,
        )

    def __getitem__(self, pk: str | SupportsIndex) -> I:
        if isinstance(pk, SupportsIndex):
            return self._items[pk]

        value = self.get(pk)
        if value is None:
            raise KeyError(pk)
        return value

    @property
    def parent_tag(self) -> bs4.Tag | None:
        """
        Return the parent tag of this element (i.e. the one whose direct
        descendants are the children of this element) or None if it does not
        exist.
        """
        return self.tag

    def create_parent_tag(self) -> bs4.Tag:
        """
        Return the parent tag of this element (i.e. the one whose direct
        descendants are the children of this element), creating it if it does
        not exist.
        """
        return self.tag

    # When generic constraints to generics become supported, we should use this:
    # def add_item[T: I](self, item: T) -> T:
    # def insert_item[T: I](self, position: int, item: T) -> T:
    def add_item(self, item: I) -> I:
        """
        Add an item to this element.

        Args:
            item: The item to add.

        Returns:
            The added item.
        """
        return self.insert_item(len(self._items), item)

    def insert_item(self, position: int | None, item: I) -> I:
        """
        Insert an item at the specified position.

        Args:
            position: The position to insert the item at. If None, the item
                is added at the end.
            item: The item to insert.

        Returns:
            The inserted item.
        """
        parent_tag = self.parent_tag
        if not parent_tag:
            parent_tag = self.create_parent_tag()

        assert item.tag is not self.tag

        if position is None:
            self._items.append(item)
            __ = parent_tag.append(item.tag)
        else:
            self._items.insert(position, item)
            child_tag_name: str | None = getattr(self._child_class(), "tag_name", None)
            actual_position = get_actual_tag_position(
                parent_tag,
                position,
                child_tag_name,
            )
            __ = parent_tag.insert(actual_position, item.tag)

        return item

    def remove_item(self, item: I) -> None:
        """
        Remove an item from this element.

        Args:
            item: The item to remove.
        """
        self._items.remove(item)
        item.tag.decompose()

    def create_child(self, **kwargs: AttributeValue | None) -> I:
        common = self._get_common_dataclass_attrs(exclude_tag=True)

        return self._child_class()(
            **common,
            **kwargs,
        )

    def insert(self, position: int | None, **kwargs: AttributeValue | None) -> I:
        """
        Create and insert a child item at the specified position.

        Args:
            position: The position to insert the item at. If None, the item
                is added at the end.
            **kwargs: Attributes to pass to the child item constructor.

        Returns:
            The newly created item.
        """
        item = self.create_child(**kwargs)
        return self.insert_item(position, item)

    def add(self, **kwargs: AttributeValue | None) -> I:
        """
        Create and add a child item.

        Args:
            **kwargs: Attributes to pass to the child item constructor.

        Returns:
            The newly created item.
        """
        return self.insert(None, **kwargs)

    def remove(self, pk: str) -> None:
        """
        Remove an item from this element, if it exists.

        Args:
            pk: The primary key of the item to remove.
        """
        item = self.get(pk)
        if item:
            return self.remove_item(item)

    @property
    def items(self) -> Sequence[I]:
        return tuple(self._items)

    def get_new_id(self, base: Path | str | EPUBId) -> EPUBId:
        """
        Generate a new unique ID for this element based on the given base.
        """
        if isinstance(base, Path):
            base = EPUBId(base.stem)
        return new_id_in_tag(EPUBId.to_valid(base), self.soup)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self.items)} items)"


class HrefChildProtocol(XMLChildProtocol, Protocol):
    href: str
    filename: str


@dataclass(kw_only=True, repr=False)
class ParentOfHref[
    I: HrefChildProtocol,
    S: bs4.BeautifulSoup = bs4.BeautifulSoup,
](
    XMLParent[I, S],
    ABC,
):
    """
    An XML element that contains other XML elements that have hrefs.
    """

    own_filename: str

    @overload
    def get[J: HrefChildProtocol](
        self,
        filename: str | Path,
        cls: type[J],
        ignore_fragment: bool = False,
    ) -> J | None: ...
    @overload
    def get(
        self,
        filename: str | Path,
        cls: type[I] | None = None,
        ignore_fragment: bool = False,
    ) -> I | None: ...

    @override
    def get(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        filename: str | Path,
        cls: type[I] | None = None,
        ignore_fragment: bool = False,
    ):
        filename = strip_fragment(str(filename)) if ignore_fragment else str(filename)

        return next(
            (
                item
                for item in self._items
                if (strip_fragment(item.filename) if ignore_fragment else item.filename)
                == filename
                and (cls is None or isinstance(item, cls))
            ),
            None,
        )

    @override
    def remove(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        filename: str | Path,
        ignore_fragment: bool = True,
    ) -> None:
        item = self.get(filename, ignore_fragment=ignore_fragment)
        if item:
            self.remove_item(item)

    def remove_all(self, filename: str | Path) -> None:
        while self.get(filename, ignore_fragment=True):
            self.remove(filename, ignore_fragment=True)

    @override
    def _get_common_dataclass_attrs(
        self,
        exclude: Sequence[str] = (),
        exclude_tag: bool = False,
        exlcude_soup: bool = False,
        include_self_as_parent: bool = True,
    ) -> dict[str, AttributeValue]:
        child_class = self._child_class()

        return super()._get_common_dataclass_attrs(
            exclude=(
                "filename",
                *exclude,
                *child_class._get_attributes().keys(),  # type: ignore[reportPrivateUsage]
            ),
            exclude_tag=exclude_tag,
            exlcude_soup=exlcude_soup,
            include_self_as_parent=include_self_as_parent,
        )


class ParentProtocol(Protocol):
    @property
    def items(self) -> Sequence[XMLChildProtocol]: ...

    def insert_item(  # type: ignore[reportAny]
        self,
        position: int,
        item: Any,  # type: ignore[reportAny]
    ) -> Any: ...  # type: ignore[reportAny]

    def remove_item(self, item: Any) -> None: ...  # type: ignore[reportAny]


class RecursiveChildProtocol(XMLChildProtocol, Protocol):
    def max_depth(self, base: int = 1) -> int: ...


class RecursiveParent[
    I: RecursiveChildProtocol,
    S: bs4.BeautifulSoup = bs4.BeautifulSoup,
](XMLParent[I, S], ABC):
    """
    An XML element whose child type is recursive (can contain itself as
    elements).
    """

    def max_depth(self, base: int = 1) -> int:
        if not self.items:
            return base

        return max(item.max_depth(base + 1) for item in self.items)


class RecursiveHrefChildProtocol(
    RecursiveChildProtocol,
    HrefChildProtocol,
    Protocol,
):
    """
    An XML element whose child type is recursive and has hrefs.
    """

    def items_referencing(
        self,
        filename: str,
        ignore_fragment: bool = False,
    ) -> Generator[XMLChildProtocol]: ...

    @classmethod
    def _get_attributes(cls) -> dict[str, XMLAttribute]: ...

    @property
    def parent(self) -> ParentProtocol | None: ...
    @property
    def items(self) -> Sequence[Self]: ...
    @property
    def nodes(self) -> Generator[Self]: ...
    def remove_nodes(self, filename: str, ignore_fragments: bool = True) -> None: ...


class HrefRoot[
    I: RecursiveHrefChildProtocol,
    S: bs4.BeautifulSoup = bs4.BeautifulSoup,
](
    RecursiveParent[I, S],
    ParentOfHref[I, S],
    ABC,
):
    """
    Root of a tree of HrefElements.
    """

    def items_referencing(
        self,
        filename: str,
        ignore_fragment: bool = False,
    ) -> Generator[Self | I]:
        """
        Yield all items in this element that reference the given filename.

        Args:
            filename: The filename to search for.
            ignore_fragment: Whether to ignore the fragment part of the
                searched filenames.

        Yields:
            Items that reference the given filename.
        """
        for item in self.items:
            yield from (
                cast(I, it) for it in item.items_referencing(filename, ignore_fragment)
            )

    @property
    def nodes(self) -> Generator[I | Self]:
        """
        Yields all nodes in the tree (not including the root).
        """
        for item in self.items:
            yield from item.nodes

    def remove_nodes(self, filename: Path | str, ignore_fragments: bool = True) -> None:
        """
        Remove all nodes in the tree that reference the given filename. If a
        parent node is removed but not its children, they are added to the
        parent of the removed node.

        Args:
            filename: The filename to search for.
            ignore_fragments: Whether to ignore the fragment part of the
                searched filenames.
        """
        filename = strip_fragment(str(filename)) if ignore_fragments else str(filename)

        index = 0
        while index < len(self.items):
            item = self.items[index]
            item.remove_nodes(filename, ignore_fragments)
            item_filename = (
                strip_fragment(item.filename) if ignore_fragments else item.filename
            )

            if item_filename == filename:
                for child in item.items:
                    __ = self.insert_item(index, child)
                    index += 1

                self.remove_item(item)
                index -= 1

            index += 1


@dataclass(kw_only=True)
class HrefRecursiveElement[
    I: RecursiveHrefChildProtocol,
    S: bs4.BeautifulSoup = bs4.BeautifulSoup,
](
    HrefRoot[I, S],
    HrefElement[S],
    ABC,
):
    """
    Node of a tree of HrefElements.
    """

    parent: ParentProtocol | None = None

    @property
    @override
    def nodes(self) -> Generator[I | Self]:
        """
        Yields all nodes in the tree.
        """
        yield self
        for item in self.items:
            yield from item.nodes

    @override
    def items_referencing(
        self,
        filename: str,
        ignore_fragment: bool = False,
    ) -> Generator[Self | I]:
        """
        Yield all items in this element (including the element itself) that
        reference the given filename.

        Args:
            filename: The filename to search for.
            ignore_fragment: Whether to ignore the fragment part of the
                searched filenames.

        Yields:
            Items that reference the given filename.
        """
        my_base, my_fragment = split_fragment(self.filename)
        base, fragment = split_fragment(filename)
        if my_base == base and (
            ignore_fragment or fragment is None or my_fragment == fragment
        ):
            yield self

        yield from super().items_referencing(filename, ignore_fragment)

    @override
    def _get_common_dataclass_attrs(
        self,
        exclude: Sequence[str] = (),
        exclude_tag: bool = False,
        exlcude_soup: bool = False,
        include_self_as_parent: bool = True,
    ) -> dict[str, AttributeValue]:
        return super()._get_common_dataclass_attrs(
            (
                *exclude,
                *self._get_attributes().keys(),
            ),
            exclude_tag,
            exlcude_soup,
            include_self_as_parent,
        )

    def add_item_after_self(self, item: I) -> I:
        """
        Add an item after this one in the parent's items.

        Args:
            item: The item to add.

        Returns:
            The added item.

        Raises:
            EPUBError: If this element has no parent, or if this element is
                not found in the parent's items.
        """
        if self.parent is None:
            raise EPUBError(f"{self} has no parent")

        if hasattr(item, "parent"):
            item.parent = self.parent  # type: ignore[reportAttributeAccessIssue]

        try:
            index = self.parent.items.index(self)
        except ValueError as error:
            raise EPUBError(f"{self} not found in parent's items") from error

        self.parent.insert_item(index + 1, item)
        return item

    def add_after_self(self, **kwargs: AttributeValue | None) -> I:
        """
        Create an item and add it after this one in the parent's items.

        Args:
            **kwargs: Attributes to pass to the child item constructor.

        Returns:
            The newly created item.

        Raises:
            EPUBError: If this element has no parent, or if this element is
                not found in the parent's items.
        """
        return self.add_item_after_self(self.create_child(**kwargs))
