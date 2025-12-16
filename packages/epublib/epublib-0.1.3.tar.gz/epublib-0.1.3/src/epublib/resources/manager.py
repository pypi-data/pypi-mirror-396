from abc import ABC, abstractmethod
from collections.abc import Callable, Generator, Iterable, MutableSequence, Sequence
from pathlib import Path
from typing import (
    Literal,
    TypedDict,
    Unpack,
    cast,
    overload,
    override,
)

import bs4

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.media_type import Category, MediaType
from epublib.nav.resource import NavigationDocument
from epublib.ncx.resource import NCXFile
from epublib.package.guide import BookGuide
from epublib.package.manifest import BookManifest, ManifestItem
from epublib.package.metadata import BookMetadata
from epublib.package.resource import PackageDocument, resource_to_manifest_item
from epublib.package.spine import BookSpine, SpineItemRef
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    SoupChanging,
    XMLResource,
)
from epublib.resources.window import Window
from epublib.soup import WithSoupProtocol
from epublib.util import (
    attr_to_str,
    get_absolute_href,
    get_relative_href,
    split_fragment,
    strip_fragment,
)

type ResourceIdentifier = str | Path | EPUBId | ManifestItem | SpineItemRef
"""An identifier for a resource in an EPUB."""

type ResourceQuery[R: Resource = Resource] = type[R] | MediaType | Category
"""A query for filtering resources in a ResourceManager."""


class AddResourceOptions(TypedDict, total=False):
    is_cover: bool
    after: Resource | ResourceIdentifier | None
    before: Resource | ResourceIdentifier | None
    add_to_manifest: bool | None
    identifier: str | EPUBId | None
    add_to_spine: bool | None
    spine_position: int | None
    linear: bool | None
    add_to_toc: bool | None
    toc_position: int | None
    add_to_ncx: bool | None
    ncx_position: int | None


def ri_to_filename(
    identifier: ResourceIdentifier,
    manifest: BookManifest,
) -> str | None:
    if isinstance(identifier, ManifestItem):
        return identifier.filename

    if isinstance(identifier, (EPUBId, SpineItemRef)):
        item = manifest.get(identifier)
        if item is None:
            return None
        return item.filename

    return strip_fragment(str(identifier))


def ri_to_id(
    identifier: ResourceIdentifier,
    manifest: BookManifest,
) -> EPUBId | None:
    if isinstance(identifier, ManifestItem):
        return identifier.id

    if isinstance(identifier, EPUBId):
        return identifier

    if isinstance(identifier, SpineItemRef):
        return identifier.idref

    manifest_item = manifest.get(identifier)
    if manifest_item:
        return manifest_item.id
    return None


class GenericResourceManager[T: Resource](MutableSequence[T], ABC):
    default_reference_attrs: tuple[str, ...] = (
        "href",
        "src",
        "full-path",
        "xlink:href",
    )

    def __init__(
        self,
        resources: MutableSequence[T],
        container_file: XMLResource,
        package_document: PackageDocument,
        nav_getter: Callable[[], NavigationDocument],
        ncx_getter: Callable[[], NCXFile | None] = lambda: None,
    ):
        self._resources: MutableSequence[T] = resources
        self.container_file: XMLResource = container_file
        self.package_document: PackageDocument = package_document
        self._get_nav: Callable[[], NavigationDocument] = nav_getter
        self._get_ncx: Callable[[], NCXFile | None] = ncx_getter

    def ri_to_filename(self, identifier: ResourceIdentifier) -> str | None:
        """
        Convert various resource identifier types to its corresponding filename,
        or None if not found.

        Args:
            identifier: The resource identifier -- filename (`str` or `Path`),
            an id (`EPUBId`), a manifest item or a spine item -- to convert.

        Returns:
            The corresponding filename as a string, or None if resource is not
            found.
        """
        return ri_to_filename(identifier, self.manifest)

    def ri_to_id(self, identifier: ResourceIdentifier) -> EPUBId | None:
        """
        Convert various resource identifier types to its corresponding EPUBId.

        Args:
            identifier: The resource identifier -- filename (`str` or `Path`),
                an id (`EPUBId`), a manifest item or a spine item -- to convert.

        Returns:
            The corresponding EPUBId as a string, or None if resource is not
            found.
        """
        return ri_to_id(identifier, self.manifest)

    @property
    def manifest(self) -> BookManifest:
        return self.package_document.manifest

    @property
    def metadata(self) -> BookMetadata:
        return self.package_document.metadata

    @property
    def spine(self) -> BookSpine:
        return self.package_document.spine

    @property
    def guide(self) -> BookGuide | None:
        return self.package_document.guide

    @property
    def ncx(self) -> NCXFile | None:
        return self._get_ncx()

    @property
    def nav(self) -> NavigationDocument:
        return self._get_nav()

    @overload
    def filter(self, query: MediaType | Category) -> Generator[T]: ...

    @overload
    def filter[R: Resource](self, query: ResourceQuery[R]) -> Generator[R]: ...

    @overload
    def filter(self, query: type[T] | None = None) -> Generator[T]: ...

    def filter(
        self,
        query: ResourceQuery[Resource] | None = None,
    ) -> Generator[Resource]:
        """
        Filter resources in this EPUB by media type, category or class.

        Typically used from an `EPUB` instance.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     xhtml_files = list(book.resources.filter(MediaType.IMAGE_PNG))
        ...     filenames = [res.filename for res in xhtml_files]
        >>> filenames
        ['Images/image.png', 'Images/image2.png']

        Args:
            query: The query to filter by. If None, all resources are returned.
                If a MediaType is provided, all PublicationResources with that
                media type are returned. If a Category is provided, all
                PublicationResources in that category are returned. If a class
                (subclass of Resource) is provided, all resources of that class
                are returned.

        Yields:
            Resources matching the query.
        """
        if query is None:
            yield from self._resources
        if isinstance(query, MediaType):
            yield from (
                resource
                for resource in self._resources
                if isinstance(resource, PublicationResource)
                and resource.media_type is query
            )
        elif isinstance(query, Category):
            yield from (
                resource
                for resource in self._resources
                if isinstance(resource, PublicationResource)
                and resource.media_type.category is query
            )
        elif isinstance(query, type):
            yield from (
                resource for resource in self._resources if isinstance(resource, query)
            )

    def get(
        self,
        identifier: ResourceIdentifier,
        query: ResourceQuery[T] | None = None,
    ) -> T | None:
        """
        Get a resource by an identifier, optionally filtering by a query.

        Typically used from an `EPUB` instance.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     resource = book.resources.get("Text/chapter1.xhtml")
        ...     filename = resource.filename if resource else None
        >>> filename
        'Text/chapter1.xhtml'

        Args:
            identifier: The resource identifier -- filename (`str` or `Path`),
                an id (`EPUBId`), a manifest item or a spine item -- to get.
            query: The query to filter by. If None, all resources are
                considered. If a MediaType is provided, only
                PublicationResources with that media type are considered. If a
                Category is provided, only PublicationResources in that category
                are considered. If a class (subclass of Resource) is provided,
                only resources of that class are considered.

        Returns:
            The resource matching the identifier and query, or None if not
            found.
        """
        id_or_none = self.ri_to_filename(identifier)
        if id_or_none is None:
            return None

        identifier = id_or_none
        return next(
            (
                resource
                for resource in self.filter(query)
                if resource.filename == identifier
            ),
            None,
        )

    @overload
    def __getitem__(self, identifier: slice) -> MutableSequence[T]: ...
    @overload
    def __getitem__(self, identifier: ResourceIdentifier | int) -> T: ...
    @override
    def __getitem__(  # type: ignore[reportIncompatibleMethodOverride]
        self, identifier: ResourceIdentifier | int | slice
    ) -> T | MutableSequence[T]:
        """
        Get a resource by an identifier.

        Typically used from an `EPUB` instance.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     resource = book.resources["Text/chapter1.xhtml"]
        ...     filename = resource.filename
        >>> filename
        'Text/chapter1.xhtml'



        Args:
            identifier: The resource identifier -- filename (`str` or `Path`),
                an id (`EPUBId`), a manifest item or a spine item -- to get.

        Raises:
            KeyError: If the resource is not found.
        """
        if isinstance(identifier, (int, slice)):
            x = self._resources[identifier]
            return x

        resource = self.get(identifier)
        if resource is None:
            raise KeyError(identifier)

        return resource

    @override
    def __iter__(self) -> Generator[T]:
        """
        Yield the resources in this manager.

        Yields:
            All resources in this manager.
        """
        yield from self._resources

    @override
    def __reversed__(self) -> Generator[T]:
        yield from reversed(self._resources)

    @override
    def count(self, value: T) -> int:
        return self._resources.count(value)

    @override
    def index(self, value: T, start: int = 0, stop: int | None = None) -> int:
        kwargs = {"stop": stop} if stop is not None else {}
        return self._resources.index(value, start, **kwargs)

    @override
    def __contains__(self, value: Resource) -> bool:  # type: ignore[reportIncompatibleMethodOverride]
        return value in self._resources

    @override
    def __len__(self) -> int:
        return len(self._resources)

    @overload
    def __setitem__(self, index: int, item: T) -> None: ...
    @overload
    def __setitem__(self, index: slice, item: Iterable[T]) -> None: ...
    @override
    def __setitem__(self, index: int | slice, item: T | Iterable[T]) -> None:
        self._resources.__setitem__(index, item)  # type: ignore[reportArgumentType]

    @override
    def __delitem__(self, i: int | slice) -> None:
        del self._resources[i]

    def _resolve_position(
        self,
        default: int,
        position: int | None = None,
        after: Resource | None = None,
        before: Resource | None = None,
    ):
        if after and position is None:
            try:
                return self._resources.index(after) + 1
            except ValueError as error:
                raise EPUBError(
                    f"resource provided as argument 'after' ('{after}') "
                    "must be part of this epub"
                ) from error
        if before and position is None:
            try:
                return self._resources.index(before) - 1
            except ValueError as error:
                raise EPUBError(
                    f"resource provided as argument 'before' ('{after}') "
                    "must be part of this epub"
                ) from error
        if position is not None:
            return position
        return default

    @staticmethod
    def _should_be_manifested(resource: Resource) -> bool:
        return Path(resource.filename).parts[0] != "META-INF"

    @staticmethod
    def _should_be_in_spine(resource: Resource) -> bool:
        return isinstance(resource, ContentDocument)

    @staticmethod
    def _should_be_spine_linear(_resource: Resource) -> bool:
        return True

    def add_to_manifest[R: Resource](
        self,
        resource: R,
        media_type: MediaType | str | None = None,
        identifier: EPUBId | str | None = None,
        fallback: str | None = None,
        media_overlay: str | None = None,
        is_cover: bool = False,
        is_nav: bool = False,
        properties: list[str] | None = None,
        detect_properties: bool = True,
        exists_ok: bool = False,
    ) -> tuple[R, ManifestItem]:
        """
        Add a resource to the manifest, if not already present. The
        resource may be promoted to a PublicationResource if needed, so
        the resource is returned as well.

        Args:
            resource: The resource to add to the manifest.
            media_type: The media type of the resource. If None, it will be
                inferred from the resource's filename.
            identifier: The identifier to use for the manifest item. If None,
                an identifier will be generated.
            fallback: The id of a fallback item, if any.
            media_overlay: The id of a media overlay item, if any.
            is_cover: Whether this resource is the cover image.
            is_nav: Whether this resource is the navigation document.
            properties: Additional properties to add to the manifest item.
            detect_properties: Whether to automatically detect properties
                based on the resource's media type and role (e.g. nav,
                cover).
            exists_ok: If True, do not raise an error if the resource is
                already in the manifest.

        Returns:
            A tuple (resource, manifest_item) of the (possibly promoted)
            resource and the manifest item.

        Raises:
            EPUBError:
                - If the resource is already in the manifest and
                  `exists_ok` is False.
                - If the resource is not a PublicationResource and
                  `media_type` is not provided, and it can't be inferred from
                  the resource's filename.
                - If `is_nav` is True but the media type is not XHTML or SVG.
        """
        manifest_item = self.manifest.get(resource.filename)
        if manifest_item:
            if exists_ok:
                return resource, manifest_item
            raise EPUBError(f"Resource '{resource.filename}' already in manifest")

        # Promoting to PublicationResource
        if not isinstance(resource, PublicationResource):
            new_resource = PublicationResource.from_resource(resource, media_type)
            try:
                index = self._resources.index(resource)
                self._resources[index] = new_resource  # type: ignore[reportArgumentType]
            except ValueError:
                pass

            resource = new_resource

        manifest_item = resource_to_manifest_item(
            resource,
            self.package_document,
            media_type=media_type,
            identifier=identifier,
            fallback=fallback,
            media_overlay=media_overlay,
            is_cover=is_cover,
            is_nav=is_nav,
            properties=properties,
            detect_properties=detect_properties,
        )
        __ = self.manifest.add_item(manifest_item)

        return resource, manifest_item

    def add(
        self,
        resource: T,
        is_cover: bool = False,
        position: int | None = None,
        after: Resource | ResourceIdentifier | None = None,
        before: Resource | ResourceIdentifier | None = None,
        add_to_manifest: bool | None = None,
        identifier: str | EPUBId | None = None,
        add_to_spine: bool | None = None,
        spine_position: int | None = None,
        linear: bool | None = None,
        add_to_toc: bool | None = None,
        toc_position: int | None = None,
        add_to_ncx: bool | None = None,
        ncx_position: int | None = None,
    ) -> None:
        """
        Add a resource to this EPUB.

        Typicial usage is from an `EPUB` instance.

        >>> from epublib import EPUB
        >>> from epublib.resources.create import create_resource
        >>> resource = create_resource(b"<svg></svg>", "image.svg")
        >>> with EPUB(sample) as book:
        ...     book.resources.add(resource, is_cover=True, position=3)
        ...     filename = book.resources[3].filename
        >>> filename
        'image.svg'

        Args:
            resource: The resource to add.
            is_cover: Whether this resource is the cover image.
            position: The position to insert the resource at. If None,
                the resource is appended to the end.
            after: A resource or identifier of a resource to insert
                after. Ignored if `position` is provided.
            before: A resource or identifier of a resource to insert
                before. Ignored if `position` or `after` is provided.
            add_to_manifest: Whether to add the resource to the manifest. If
                None, it will be added if it isn't in the META-INF folder.
            identifier: The identifier to use for the manifest item. If None,
                an identifier will be generated.
            add_to_spine: Whether to add the resource to the spine. If None,
                it will be added if it is a ContentDocument.
            spine_position: The position in the spine to insert the resource. If
                None, it will be appended to the end of the spine.
            linear: Whether the spine item should be linear. If None, it will
                be linear.
            add_to_toc: Whether to add the resource to the navigation document's
                table of contents. If None, it will be added if it is in the
                spine.
            toc_position: The position in the navigation document's table of
                content. If None, it will be appended to the end.
            add_to_ncx: Whether to add the resource to the NCX file's. If None,
                it will be added if there is an NCX file and if add_to_toc is
                True.
            ncx_position: The position in the NCX file's table of content. If
                None, it will be the same as `toc_position`.

        Raises:
            EPUBError:
                - If `add_to_spine` is True but `add_to_manifest` is False.
                - If `add_to_toc` is True but `add_to_manifest` is False.
                - If `add_to_ncx` is True but there is no NCX file.
                - If the resource is already in the EPUB.
        """
        is_nav = isinstance(resource, NavigationDocument)

        if not isinstance(after, Resource) and after is not None:
            after = self.get(after)
        if not isinstance(before, Resource) and before is not None:
            before = self.get(before)

        position = self._resolve_position(len(self._resources), position, after, before)

        self._resources.insert(position, resource)

        if add_to_manifest is False and add_to_spine:
            raise EPUBError("Cannot add to spine without adding to manifest")

        if add_to_manifest is False and add_to_toc:
            raise EPUBError(
                "Cannot update navigation document without adding to manifest"
            )

        if add_to_manifest is None:
            add_to_manifest = add_to_spine or self._should_be_manifested(resource)

        if add_to_spine is None:
            add_to_spine = add_to_manifest and self._should_be_in_spine(resource)

        if add_to_toc is None:
            add_to_toc = add_to_spine

        if add_to_ncx and not self.ncx:
            raise EPUBError.missing_ncx(self, "add_resource", "add_to_ncx")

        if add_to_ncx is None:
            add_to_ncx = self.ncx is not None and add_to_toc

        if ncx_position is None:
            ncx_position = toc_position

        manifest_item: None | ManifestItem = None

        if add_to_manifest:
            resource, manifest_item = self.add_to_manifest(
                resource,
                identifier=identifier,
                is_cover=is_cover,
                is_nav=is_nav,
                exists_ok=False,
            )

            if spine_position is None:
                spine_position = len(self.spine.items)

            if add_to_spine:
                if linear is None:
                    linear = self._should_be_spine_linear(resource)
                spine_item = SpineItemRef(
                    self.spine.soup,
                    idref=manifest_item.id,
                    linear=linear,
                )
                __ = self.spine.insert_item(spine_position, spine_item)

            if add_to_toc and self.nav:
                assert self.nav.toc
                __ = self.nav.toc.insert(
                    toc_position,
                    resource.get_title(),
                    resource.filename,
                )

            if add_to_ncx and self.ncx:
                __ = self.ncx.nav_map.insert(
                    ncx_position,
                    resource.get_title(),
                    resource.filename,
                )

    @override
    def insert(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        position: int,
        resource: T,
        **kwargs: Unpack[AddResourceOptions],
    ) -> None:
        """
        Insert a resource at a given position in this EPUB.

        Args:
            position: The position to insert the resource at.
            resource: The resource to add.
            **kwargs: Additional options to pass to `add()`.

        Raises:
            EPUBError:
                - If `add_to_spine` is True but `add_to_manifest` is False.
                - If `add_to_toc` is True but `add_to_manifest` is False.
                - If `add_to_ncx` is True but there is no NCX file.
                - If the resource is already in the EPUB.
        """
        return self.add(resource, **kwargs, position=position)

    def append(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        resource: T,
        **kwargs: Unpack[AddResourceOptions],
    ) -> None:
        """
        Insert a resource at the end of an EPUB.

        Args:
            resource: The resource to add.
            **kwargs: Additional options to pass to `add()`.

        Raises:
            EPUBError:
                - If `add_to_spine` is True but `add_to_manifest` is False.
                - If `add_to_toc` is True but `add_to_manifest` is False.
                - If `add_to_ncx` is True but there is no NCX file.
                - If the resource is already in the EPUB.
        """
        return self.add(resource, **kwargs)

    @override
    def remove(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        resource: ResourceIdentifier | T,
        remove_css_js_links: Literal[False] | None = None,
    ):
        """
        Remove a resource from this EPUB.

        Args:
            resource: The resource or identifier of the resource to remove.
            remove_css_js_links: Whether to remove links to this resource
                from content documents if it is a CSS or JavaScript file.
                If None, links will be removed if the resource is a CSS or
                JavaScript file. If False, links will not be removed.

        Raises:
            EPUBError:
                - If the resource is not in this EPUB.
                - If trying to remove the container file, package document
                  or navigation document.
                - If `remove_css_js_links` is True but the resource is not
                  a CSS or JavaScript file.
        """

        if not isinstance(resource, Resource):
            res = self.get(resource)
            if res is None:
                raise EPUBError(
                    f"Can't remove resource '{resource}' not in this epub ('{self}')"
                )

            resource = res

        elif resource not in self:
            raise EPUBError(f"Resource '{resource}' not in EPUB")

        if resource is self.package_document:
            raise EPUBError("Can't remove package document")

        if resource is self.container_file:
            raise EPUBError("Can't remove container file")

        if resource is self.nav:
            raise EPUBError(
                "Can't remove navigation document. Set the navigation "
                "document to another resource or first."
            )

        self.nav.remove(resource.filename)

        if self.ncx and resource is not self.ncx:
            self.ncx.remove(resource.filename)

        if self.guide and self.guide.get(resource.filename):
            self.guide.remove(resource.filename)

        remove_links: bool | None = remove_css_js_links
        if remove_links is None:
            remove_links = isinstance(resource, PublicationResource) and (
                resource.media_type.is_css() or resource.media_type.is_js()
            )

        self.package_document.remove(resource.filename)
        self._resources.remove(resource)

        if remove_links:
            if not isinstance(resource, PublicationResource) or not (
                resource.media_type.is_css() or resource.media_type.is_js()
            ):
                raise EPUBError(
                    "Can't remove CSS and JavaScript links for file "
                    "that is neither CSS nor JavaScript"
                )

            for res in self.filter(ContentDocument):
                relative_href = get_relative_href(res.filename, resource.filename)
                for tag in res.soup.find_all(
                    "link",
                    rel="stylesheet",
                    href=relative_href,
                ):
                    tag.decompose()
                for tag in res.soup.find_all(
                    "script",
                    src=relative_href,
                ):
                    tag.decompose()

    def rename(
        self,
        resource: ResourceIdentifier | T,
        new_filename: str | Path,
        update_references: bool = True,
        reference_attrs: list[str] | None = None,
    ):
        """
        Rename the resource, optionally updating references to it.

        Typically used from an `EPUB` instance.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     _, tag = next(book.resources.tags_referencing("Text/chapter1.xhtml"))
        ...     book.resources.rename("Text/chapter1.xhtml", "Text/chapter100.xhtml")
        >>> tag
        <a href="chapter100.xhtml"...

        Args:
            resource: The resource or identifier of the resource to rename.
            new_filename: The new filename for the resource.
            update_references: Whether to update references to this resource
                in other resources. Defaults to True.
            reference_attrs: The attributes to update references in. If None,
                the default attributes will be used:
                `('href', 'src', 'full-path', 'xlink:href')`.

        Raises:
            EPUBError:
                - If the resource is not in this EPUB.
                - If trying to rename the container file.
        """

        if not isinstance(resource, Resource):
            res = self.get(resource)
            if res is None:
                raise EPUBError(
                    f"Can't rename resource '{resource}' not in this epub ('{self}')"
                )

            resource = res

        elif resource not in self:
            raise EPUBError(
                f"Can't rename resource '{resource}' not in this epub ('{self}')"
            )

        if resource is self.container_file:
            raise EPUBError("Can't rename container file")

        if reference_attrs is None:
            reference_attrs = list(self.default_reference_attrs)

        selector = ", ".join(f"[{attr.replace(':', '|')}]" for attr in reference_attrs)

        new_filename = str(new_filename)

        other_resources = (
            self.filter(XMLResource)
            if update_references
            else [self.package_document, *([self.ncx] if self.ncx else [])]
        )
        for other_resource in other_resources:
            if other_resource is resource:
                # If file moves to different folder, all refs must be updated
                if Path(new_filename).parent != Path(resource.filename).parent:
                    soup = cast(bs4.BeautifulSoup, resource.soup)
                    for tag in soup.select(selector):
                        for attr in reference_attrs:
                            value = attr_to_str(tag.get(attr))
                            if value is None:
                                continue
                            ref, identifier = split_fragment(value)
                            if ref:
                                old_absolute_ref = get_absolute_href(
                                    resource.filename,
                                    ref,
                                )
                                if old_absolute_ref == resource.filename:
                                    new_ref = get_relative_href(
                                        new_filename,
                                        new_filename,
                                    )
                                else:
                                    new_ref = get_relative_href(
                                        new_filename,
                                        old_absolute_ref,
                                    )

                                tag[attr] = new_ref + (
                                    f"#{identifier}" if identifier else ""
                                )

            for tag in other_resource.soup.select(selector):
                for attr in reference_attrs:
                    value = attr_to_str(tag.get(attr))
                    if value is None:
                        continue
                    if attr == "full-path":
                        if resource.filename == value:
                            tag[attr] = new_filename
                    else:
                        ref, identifier = split_fragment(value)
                        old_absolute_ref = get_absolute_href(
                            other_resource.filename,
                            ref,
                        )
                        if old_absolute_ref == resource.filename:
                            new_ref = get_relative_href(
                                other_resource.filename,
                                new_filename,
                            )
                            tag[attr] = new_ref + (
                                f"#{identifier}" if identifier else ""
                            )

            if isinstance(other_resource, SoupChanging):
                other_resource.on_soup_change()

        resource.filename = new_filename

    @overload
    def resolve_href[R: Resource](
        self,
        href: str,
        with_tag: Literal[False],
        relative_to: Resource | ResourceIdentifier | None,
        query: ResourceQuery[R],
    ) -> R | None: ...
    @overload
    def resolve_href(
        self,
        href: str,
        with_tag: Literal[False],
        relative_to: T | ResourceIdentifier | None = None,
        query: None = None,
    ) -> T | None: ...
    @overload
    def resolve_href(
        self,
        href: str,
        with_tag: Literal[True] = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        query: None = None,
    ) -> tuple[T, bs4.Tag | None] | tuple[None, None]: ...
    @overload
    def resolve_href[R: Resource](
        self,
        href: str,
        with_tag: Literal[True] = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        query: ResourceQuery[R] | None = None,
    ) -> tuple[R, bs4.Tag | None] | tuple[None, None]: ...
    @overload
    def resolve_href[R: Resource](
        self,
        href: str,
        with_tag: bool = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        query: ResourceQuery[R] | None = None,
    ) -> tuple[R, bs4.Tag | None] | tuple[None, None] | R | None: ...

    def resolve_href(  # type: ignore[reportInconsistentOverload]
        self,
        href: str,
        with_tag: bool = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        query: ResourceQuery[T] | None = None,
    ) -> tuple[T, bs4.Tag | None] | tuple[None, None] | T | None:
        """
        Resolve an href (possibly with a fragment identifier) to a
        resource. Optionally return the tag of the matched fragment
        within that resource.

        Typically used from an `EPUB` instance.

        >>> from epublib import EPUB
        >>> with EPUB(sample) as book:
        ...     resource, tag = book.resources.resolve_href(
        ...         "chapter1.xhtml#heading2",
        ...         relative_to="Text/nav.xhtml"
        ...     )
        >>> tag
        <h2 id="heading2">Heading 2</h2>
        >>> resource.filename
        'Text/chapter1.xhtml'

        Args:
            href: The href to resolve. May include a fragment identifier.
            with_tag: Whether to return the tag of the matched fragment
                within the resource. Defaults to True.
            relative_to: The resource or identifier of the resource
                containing the href, if the href is relative. If None,
                the href is considered absolute. Defaults to None.
            query: The query parameter to pass to the `get` method.
        """

        filename = href
        if relative_to is not None:
            if isinstance(relative_to, Resource):
                relative_to = relative_to.filename
            else:
                relative_to = self.ri_to_filename(relative_to)
                if relative_to is None:
                    return (None, None) if with_tag else None

            filename = get_absolute_href(relative_to, href)

        filename, identifier = split_fragment(filename)
        resource = self.get(filename, query)

        if not with_tag:
            return resource

        if resource is None:
            return None, None

        if isinstance(resource, WithSoupProtocol):
            return cast(T, resource), resource.soup.select_one(
                f'[id="{identifier}"]'
            ) if identifier is not None else None

        return resource, None

    def set_cover_image(self, resource: ResourceIdentifier | Resource) -> None:
        """
        Set the cover image of this EPUB. The resource must be an image and will
        be added to the manifest if not already present.

        Args:
            resource: The resource or identifier of the resource to set as the
                cover image.
        Raises:
            EPUBError:
                - If the resource is not in this EPUB.
                - If the resource is not an image.

        """

        if not isinstance(resource, Resource):
            res = self.get(resource)
            if res is None:
                raise EPUBError(
                    f"Can't set cover image to resource '{resource}' not in "
                    f"this epub ('{self}')"
                )

            resource = res

        elif resource not in self:
            raise EPUBError(f"Resource '{resource}' not in EPUB")

        if (
            not isinstance(resource, PublicationResource)
            or resource.media_type.category is not Category.IMAGE
        ):
            raise EPUBError("Cover image must be an image")

        manifest_item = self.manifest[resource]
        for other in self.manifest.items:
            other.remove_property("cover-image")
        manifest_item.add_property("cover-image")

        metadata_item = self.metadata.get_valued("cover")
        if manifest_item and metadata_item:
            metadata_item.value = manifest_item.id

    def tags_referencing(
        self,
        filename: str | Path,
        reference_attrs: Sequence[str] | None = None,
        ignore_fragment: bool = False,
    ) -> Generator[tuple[ContentDocument, bs4.Tag]]:
        """
        Find all tags and their respective resources in content documents that
        reference the given filename.

        Args:
            filename: The filename to search for, possibily with a fragment.
            reference_attrs: The attributes to search for references in. If
                None, the default attributes will be used:
                `('href', 'src', 'full-path', 'xlink:href')`.
            ignore_fragment: Whether to ignore fragment identifiers when
                searching for references. Defaults to False.

        Yields:
            Tuples of (resource, tag) where tag it the tag that references
            `filename` and `resource` is the content document containing that
            tag.
        """

        filename = str(filename)

        if reference_attrs is None:
            reference_attrs = list(self.default_reference_attrs)
            reference_attrs.remove("full-path")

        for document in self.filter(ContentDocument):
            relative_href = get_relative_href(document.filename, filename)
            if ignore_fragment:
                relative_href = strip_fragment(relative_href)
            for attr in reference_attrs:
                for tag in document.soup.find_all(attrs={attr: True}):
                    value = attr_to_str(tag[attr])
                    value = strip_fragment(value) if value else value
                    if value == relative_href:
                        yield document, tag

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({len(self)} resources)"


class ResourceManager(GenericResourceManager[Resource]):
    """
    The resource manager for an EPUB. Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     num_resources = len(book.resources)
    ...     first_resource = book.resources[0]
    >>> num_resources
    8
    >>> first_resource.filename
    'mimetype'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    @override
    def _resolve_position(
        self,
        default: int,
        position: int | None = None,
        after: Resource | None = None,
        before: Resource | None = None,
    ):
        position = super()._resolve_position(default, position, after, before)
        if position == 0:
            # Prevent inserting before mimetype
            position = 1
        return position

    @overload
    def filter(
        self, query: Literal[MediaType.XHTML, MediaType.IMAGE_SVG]
    ) -> Generator[ContentDocument]: ...
    @overload
    def filter(self, query: Literal[MediaType.NCX]) -> Generator[NCXFile]: ...
    @overload
    def filter(self, query: MediaType | Category) -> Generator[PublicationResource]: ...
    @overload
    def filter[R: Resource](self, query: ResourceQuery[R]) -> Generator[R]: ...
    @overload
    def filter(
        self, query: ResourceQuery[Resource] | None = None
    ) -> Generator[Resource]: ...

    @override
    def filter(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        query: ResourceQuery[Resource] | None = None,
    ) -> Generator[Resource]:
        return super().filter(query)

    @overload
    def get[R: PublicationResource](
        self, identifier: EPUBId | ManifestItem, query: type[R]
    ) -> R | None: ...
    @overload
    def get(
        self,
        identifier: EPUBId | ManifestItem | SpineItemRef,
        query: ResourceQuery[PublicationResource] = PublicationResource,
    ) -> PublicationResource | None: ...
    @overload
    def get[R: Resource](self, identifier: str | Path, query: type[R]) -> R | None: ...
    @overload
    def get(
        self,
        identifier: str | Path,
        query: ResourceQuery[Resource] = Resource,
    ) -> Resource | None: ...
    @override
    def get(
        self,
        identifier: ResourceIdentifier,
        query: ResourceQuery[Resource] | None = None,
    ) -> Resource | None:
        return super().get(identifier, query)

    @overload
    def resolve_href[R: Resource](
        self,
        href: str,
        with_tag: Literal[False],
        relative_to: Resource | ResourceIdentifier | None,
        query: ResourceQuery[R],
    ) -> R | None: ...
    @overload
    def resolve_href(
        self,
        href: str,
        with_tag: Literal[False],
        relative_to: Resource | ResourceIdentifier | None = None,
        query: None = None,
    ) -> Resource | None: ...
    @overload
    def resolve_href(
        self,
        href: str,
        with_tag: Literal[True] = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        query: None = None,
    ) -> tuple[XMLResource, bs4.Tag] | tuple[Resource, None] | tuple[None, None]: ...
    @overload
    def resolve_href[R: Resource](
        self,
        href: str,
        with_tag: Literal[True] = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        query: ResourceQuery[R] | None = None,
    ) -> tuple[R, bs4.Tag | None] | tuple[None, None]: ...
    @override
    def resolve_href(  # type: ignore[reportIncompatibleMethodOverride]
        self,
        href: str,
        with_tag: bool = True,
        relative_to: Resource | ResourceIdentifier | None = None,
        query: ResourceQuery[Resource] | None = None,
    ):
        return super().resolve_href(href, with_tag, relative_to, query)

    @overload
    def __getitem__(self, identifier: slice) -> MutableSequence[Resource]: ...
    @overload
    def __getitem__(self, identifier: str | Path | int) -> Resource: ...
    @overload
    def __getitem__(
        self, identifier: EPUBId | ManifestItem | SpineItemRef
    ) -> PublicationResource: ...
    @override
    def __getitem__(  # type: ignore[reportIncompatibleMethodOverride]
        self, identifier: ResourceIdentifier | int | slice
    ) -> Resource | MutableSequence[Resource]:
        return super().__getitem__(identifier)

    @property
    def cover_image(self) -> PublicationResource | None:
        manifest_item = self.manifest.cover_image
        return self.get(manifest_item) if manifest_item else None


class WindowedResourceManager[T: PublicationResource](GenericResourceManager[T], ABC):
    base_class: type[T]

    def _is_in_window(self, resource: Resource) -> bool:
        return isinstance(resource, self.base_class)

    @abstractmethod
    def _error_message(self, resource: Resource) -> str: ...

    def __init__(
        self,
        resources: MutableSequence[Resource],
        container_file: XMLResource,
        package_document: PackageDocument,
        nav_getter: Callable[[], NavigationDocument],
        ncx_getter: Callable[[], NCXFile | None] = lambda: None,
    ):
        super().__init__(
            Window[Resource, T](
                resources,
                self._is_in_window,
                self._error_message,
            ),
            container_file,
            package_document,
            nav_getter,
            ncx_getter,
        )

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.base_class}]({len(self)} {self.base_class.__name__} resources)"


class PublicationResourceManager(WindowedResourceManager[PublicationResource]):
    """
    The resource manager for publication resources in an EPUB. An implementation
    of the resource manager windowed for publication resources. Publication
    resources are all resources that contribute to the reading of the
    publication (and are thus listed in the manifest).

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     num_resources = len(book.publication_resources)
    ...     first_resource = book.publication_resources[0]
    >>> num_resources
    5
    >>> first_resource.filename
    'Text/nav.xhtml'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    base_class: type[PublicationResource] = PublicationResource

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not a publication resource"


class ImagesManager(PublicationResourceManager):
    """
    The resource manager for images in an EPUB. An implementation of the
    resource manager windowed for images.

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     num_resources = len(book.images)
    ...     first_resource = book.images[0]
    >>> num_resources
    2
    >>> first_resource.filename
    'Images/image.png'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    @override
    def _is_in_window(self, resource: Resource) -> bool:
        return (
            isinstance(resource, PublicationResource)
            and resource.media_type.category is Category.IMAGE
        )

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not an image"

    @property
    def cover(self) -> PublicationResource | None:
        manifest_item = self.manifest.cover_image
        return self.get(manifest_item) if manifest_item else None


class ScriptsManager(PublicationResourceManager):
    """
    The resource manager for scripts in an EPUB. An implementation of the
    resource manager windowed for scritps.

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> from epublib.resources.create import create_resource
    >>> with EPUB(sample) as book:
    ...     resource = create_resource(b"console.log('Hello, world!');", "Misc/script.js")
    ...     book.scripts.add(resource)
    ...     num_resources = len(book.scripts)
    ...     first_resource = book.scripts[0]
    >>> num_resources
    1
    >>> first_resource.filename
    'Misc/script.js'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    @override
    def _is_in_window(self, resource: Resource) -> bool:
        return isinstance(resource, PublicationResource) and resource.media_type.is_js()

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not a script"


class StylesManager(PublicationResourceManager):
    """
    The resource manager for stylesheets in an EPUB. An implementation of the
    resource manager windowed for stylesheets.

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> from epublib.resources.create import create_resource
    >>> with EPUB(sample) as book:
    ...     resource = create_resource(b"p { color: orange }", "Styles/design.css")
    ...     book.styles.insert(0, resource)
    ...     num_resources = len(book.styles)
    ...     first_resource = book.styles[0]
    >>> num_resources
    2
    >>> first_resource.filename
    'Styles/design.css'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    @override
    def _is_in_window(self, resource: Resource) -> bool:
        return (
            isinstance(resource, PublicationResource) and resource.media_type.is_css()
        )

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not a style"


class FontsManager(PublicationResourceManager):
    """
    The resource manager for fonts in an EPUB. An implementation of the
    resource manager windowed for fonts.

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> from epublib.resources.create import create_resource
    >>> with EPUB(sample) as book:
    ...     resource = create_resource(b"", "Fonts/font.ttf")
    ...     book.fonts.insert(0, resource)
    ...     num_resources = len(book.fonts)
    ...     first_resource = book.fonts[0]
    >>> num_resources
    1
    >>> first_resource.filename
    'Fonts/font.ttf'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    @override
    def _is_in_window(self, resource: Resource) -> bool:
        return (
            isinstance(resource, PublicationResource)
            and resource.media_type.category is Category.FONT
        )

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not a font"


class AudioManager(PublicationResourceManager):
    """
    The resource manager for audio in an EPUB. An implementation of the
    resource manager windowed for audio files.

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> from epublib.resources.create import create_resource
    >>> with EPUB(sample) as book:
    ...     resource = create_resource(b"", "Audio/audio.mp3")
    ...     book.audios.insert(0, resource)
    ...     num_resources = len(book.audios)
    ...     first_resource = book.audios[0]
    >>> num_resources
    1
    >>> first_resource.filename
    'Audio/audio.mp3'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    @override
    def _is_in_window(self, resource: Resource) -> bool:
        return (
            isinstance(resource, PublicationResource)
            and resource.media_type.category is Category.AUDIO
        )

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not audio"


class VideoManager(PublicationResourceManager):
    """
    The resource manager for video in an EPUB. An implementation of the
    resource manager windowed for video files.

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> from epublib.resources.create import create_resource
    >>> with EPUB(sample) as book:
    ...     resource = create_resource(b"", "Video/video.mp4")
    ...     book.videos.insert(0, resource)
    ...     num_resources = len(book.videos)
    ...     first_resource = book.videos[0]
    >>> num_resources
    1
    >>> first_resource.filename
    'Video/video.mp4'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    @override
    def _is_in_window(self, resource: Resource) -> bool:
        return (
            isinstance(resource, PublicationResource) and resource.media_type.is_video()
        )

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not video"


class ContentDocumentManager(WindowedResourceManager[ContentDocument]):
    """
    The resource manager for content documents in an EPUB. An implementation of
    the resource manager windowed for documents.

    Typically used from an `EPUB` instance.

    >>> from epublib import EPUB
    >>> from epublib.resources.create import create_resource
    >>> with EPUB(sample) as book:
    ...     resource = create_resource(b"", "Text/chapter100.xhtml")
    ...     book.documents.insert(0, resource)
    ...     num_resources = len(book.documents)
    ...     first_resource = book.documents[0]
    >>> num_resources
    3
    >>> first_resource.filename
    'Text/chapter100.xhtml'

    Args:
        resources: The list of all resources in this EPUB.
        container_file: The container file of this EPUB.
        package_document: The package document of this EPUB.
        nav_getter: Callable to get the navigation document of this EPUB.
        ncx_getter: A Callable to get the ncx file of this EPUB,
    """

    base_class: type[ContentDocument] = ContentDocument

    @override
    def _error_message(self, resource: Resource) -> str:
        return f"Resource '{resource}' is not a content document"
