from collections.abc import Generator
from pathlib import Path
from typing import IO, Any, Callable, Literal, Self, TypedDict, overload, override
from zipfile import is_zipfile

import bs4

from epublib.create import EPUBCreator
from epublib.exceptions import ClosedEPUBError, EPUBError, NotEPUBError
from epublib.identifier import EPUBId
from epublib.nav.reset import (
    create_landmarks,
    create_page_list,
    reset_landmarks,
    reset_page_list,
    reset_toc,
)
from epublib.nav.resource import NavigationDocument
from epublib.ncx.reset import generate_ncx, reset_ncx
from epublib.ncx.resource import NCXFile
from epublib.package.guide import BookGuide
from epublib.package.manifest import (
    BookManifest,
    ManifestItem,
    detect_manifest_properties,
)
from epublib.package.metadata import BookMetadata, ValuedMetadataItem
from epublib.package.resource import PackageDocument
from epublib.package.spine import BookSpine, SpineItemRef
from epublib.parse import parse
from epublib.resources import (
    ContentDocument,
    Resource,
    XMLResource,
)
from epublib.resources.manager import (
    AudioManager,
    ContentDocumentManager,
    FontsManager,
    ImagesManager,
    PublicationResourceManager,
    ResourceIdentifier,
    ResourceManager,
    ScriptsManager,
    StylesManager,
    VideoManager,
)
from epublib.source import (
    DirectorySink,
    DirectorySource,
    SinkProtocol,
    SourceProtocol,
    ZipFile,
)
from epublib.util import get_epublib_version


class _ManagerDict(TypedDict, total=False):
    documents: ContentDocumentManager
    images: ImagesManager
    scripts: ScriptsManager
    styles: StylesManager
    fonts: FontsManager
    audios: AudioManager
    videos: VideoManager
    publication_resources: PublicationResourceManager


class EPUB:
    """
    The main class for reading, writing, and manipulating EPUB files.

    Typical usage example:

    >>> with EPUB() as book:
    ...     book.metadata.title = "New EPUB"
    ...     print(book)
    ...     book.write(folder / "new.epub")
    EPUB(title='New EPUB')

    Args:
        file: A file-like object, path to a zip file, or path to a folder
            representing an 'unzipped' EPUB. If None, creates a new empty EPUB.
        generator_tag: Whether to add a generator tag to the metadata,
            registering that epublib was used to create or edit the EPUB. Defaults
            to True

    Raises:
        NotEPUBError: If the provided file is neither a zip file, a file object
            or a valid path to a zip file or folder.
    """

    def __init__(
        self,
        file: IO[bytes] | str | Path | None = None,
        generator_tag: bool = True,
    ) -> None:
        self.source: SourceProtocol

        if file is None:
            self.source = ZipFile(
                EPUBCreator(add_generator_tag=generator_tag).to_file()
            )
        elif is_zipfile(file):
            self.source = ZipFile(file)
        elif (isinstance(file, str) or isinstance(file, Path)) and Path(file).is_dir():
            self.source = DirectorySource(file)
        else:
            raise NotEPUBError(f"file '{file}' is not ZIP nor folder")

        self.container_file: XMLResource
        self.package_document: PackageDocument
        self._resources: list[Resource]
        self.container_file, self.package_document, self._resources = parse(self.source)
        self.resources: ResourceManager = ResourceManager(
            self._resources,
            container_file=self.container_file,
            package_document=self.package_document,
            nav_getter=lambda: self.nav,
            ncx_getter=lambda: self.ncx,
        )

        self.original_path: Path | None = (
            Path(file) if isinstance(file, str) or isinstance(file, Path) else None
        )

        self._managers: _ManagerDict = {}

        if generator_tag:
            self.add_generator_tag()

    @property
    def manifest(self) -> BookManifest:
        """
        The manifest of this EPUB. An alias to `package_document.manifest`.

        >>> with EPUB(sample) as book:
        ...     item = book.manifest.items[0]
        ...     item = book.manifest["Text/chapter1.xhtml"]
        ...     item = book.manifest.get(EPUBId("chapter1"))
        ...     print(item.id, item.filename, item.media_type)
        chapter1 Text/chapter1.xhtml application/xhtml+xml
        """
        return self.package_document.manifest

    @property
    def metadata(self) -> BookMetadata:
        """
        The metadata of this EPUB. An alias to `package_document.metadata`.

        >>> book = EPUB(sample)
        >>> book.title = "A sample EPUB"
        >>> book.title
        'A sample EPUB'
        >>> book.language = "es"
        >>> book.language
        'es'
        >>> from datetime import datetime
        >>> book.metadata.modified = datetime(2025, 7, 10, 0, 0, 0)
        >>> book.metadata.get("dcterms:modified")
        GenericMetadataItem(name='dcterms:modified', value='2025-07-10...', ...)
        >>> book.close()
        """
        return self.package_document.metadata

    @property
    def spine(self) -> BookSpine:
        """
        The spine of this EPUB. An alias to `package_document.spine`.

        >>> with EPUB(sample) as book:
        ...     item = book.spine.items[0]
        ...     item = book.spine["chapter1"]
        ...     print(item.idref)
        chapter1
        """

        return self.package_document.spine

    @property
    def guide(self) -> BookGuide | None:
        """
        The guide (legacy feature of EPUB2 files) of this EPUB. An alias to
        `package_document.spine`.
        """
        return self.package_document.guide

    @property
    def nav(self) -> NavigationDocument:
        """
        The navgation document of this EPUB. Equivalent to
        `book.resources.get(book.manifest.nav)`.

        Raises:
            EPUBError: If no navigation document is found in the EPUB.
        """
        nav = self.resources.get(self.manifest.nav.filename, NavigationDocument)
        if not nav:
            raise EPUBError("no navigation document found in EPUB")
        return nav

    @property
    def ncx(self) -> NCXFile | None:
        """
        The NCX file of this EPUB, or None if there is no such file.
        """
        return next(self.resources.filter(NCXFile), None)

    def write_to_sink(self, out: SinkProtocol) -> None:
        """
        Write this epub to a sink (any object implementing the SinkProtocol).

        Args:
            out: The sink to write the EPUB to.

        Raises:
            ClosedEPUBError: If the EPUB is already closed.
        """

        self._check_closed("trying to write closed EPUB")

        for resource in self.resources:
            out.writestr(resource.zipinfo, resource.get_content(cache=False))

    def write(self, output_file: IO[bytes] | str | Path) -> None:
        """
        Write this epub to a file or to a file object.

        Args:
            output_file: The path to the output file, or a file-like object
                to write the EPUB to.

        Raises:
            ClosedEPUBError: If the EPUB is already closed.
        """

        with ZipFile(output_file, mode="w") as out_zip:
            self.write_to_sink(out_zip)

    def write_to_folder(self, folder: str | Path) -> None:
        """
        Write this epub to a folder (creating an 'unzipped' EPUB).

        Args:
            output_file: The path to the output file, or a file-like object
                to write the EPUB to.

        Raises:
            ClosedEPUBError: If the EPUB is already closed.

        """

        if not Path(folder).is_dir():
            raise EPUBError(f"Path '{folder}' is not a directory")

        out = DirectorySink(folder)
        self.write_to_sink(out)

    @overload
    def _get_manager(self, name: Literal["documents"]) -> ContentDocumentManager: ...
    @overload
    def _get_manager(self, name: Literal["images"]) -> ImagesManager: ...
    @overload
    def _get_manager(self, name: Literal["scripts"]) -> ScriptsManager: ...
    @overload
    def _get_manager(self, name: Literal["styles"]) -> StylesManager: ...
    @overload
    def _get_manager(self, name: Literal["fonts"]) -> FontsManager: ...
    @overload
    def _get_manager(self, name: Literal["audios"]) -> AudioManager: ...
    @overload
    def _get_manager(self, name: Literal["videos"]) -> VideoManager: ...
    @overload
    def _get_manager(
        self, name: Literal["publication_resources"]
    ) -> PublicationResourceManager: ...
    def _get_manager(
        self,
        name: Literal[
            "documents",
            "images",
            "scripts",
            "styles",
            "fonts",
            "audios",
            "videos",
            "publication_resources",
        ],
    ):
        class ManagerKwargs(TypedDict):
            resources: list[Resource]
            container_file: XMLResource
            package_document: PackageDocument
            nav_getter: Callable[[], NavigationDocument]
            ncx_getter: Callable[[], NCXFile | None]

        kwargs: ManagerKwargs = {
            "resources": self._resources,
            "container_file": self.container_file,
            "package_document": self.package_document,
            "nav_getter": lambda: self.nav,
            "ncx_getter": lambda: self.ncx,
        }

        if name not in self._managers:
            match name:
                case "documents":
                    self._managers[name] = ContentDocumentManager(**kwargs)
                case "images":
                    self._managers[name] = ImagesManager(**kwargs)
                case "scripts":
                    self._managers[name] = ScriptsManager(**kwargs)
                case "styles":
                    self._managers[name] = StylesManager(**kwargs)
                case "fonts":
                    self._managers[name] = FontsManager(**kwargs)
                case "audios":
                    self._managers[name] = AudioManager(**kwargs)
                case "videos":
                    self._managers[name] = VideoManager(**kwargs)
                case "publication_resources":
                    self._managers[name] = PublicationResourceManager(**kwargs)

        return self._managers[name]  # type: ignore[reportReturnType]

    @property
    def documents(self) -> ContentDocumentManager:
        """
        Manage all content documents (XHTML or SVG) in this EPUB.
        """
        return self._get_manager("documents")

    @property
    def images(self) -> ImagesManager:
        """
        Manage all image resources in this EPUB.
        """
        return self._get_manager("images")

    @property
    def scripts(self) -> ScriptsManager:
        """
        Manage all JavaScript resources in this EPUB.
        """
        return self._get_manager("scripts")

    @property
    def styles(self) -> StylesManager:
        """
        Manage all CSS resources in this EPUB.
        """
        return self._get_manager("styles")

    @property
    def fonts(self) -> FontsManager:
        """
        Manage all font resources in this EPUB.
        """

        return self._get_manager("fonts")

    @property
    def audios(self) -> AudioManager:
        """
        Manage all font resources in this EPUB.
        """

        return self._get_manager("audios")

    @property
    def videos(self) -> VideoManager:
        """
        Manage all font resources in this EPUB.
        """

        return self._get_manager("videos")

    @property
    def publication_resources(self) -> PublicationResourceManager:
        """
        Manage all publication resources in this EPUB.
        """
        return self._get_manager("publication_resources")

    def rename_id(
        self,
        old: Resource | ResourceIdentifier,
        new: EPUBId,
    ) -> None:
        """
        Rename a manifest identifier. Look for references for updating it in the
        spine items, the cover-image metadata tag and the toc attribute of the
        spine element.

        Caution is advised, as there may be other references to the old id that
        will become outdated.

        Args:
            old: The old identifier, or the resource whose identifier to rename.
            new: The new identifier.

        Raises:
            EPUBError: If the old identifier does not exist, or if the new
                identifier already exists.
        """

        if not isinstance(old, ManifestItem):
            manifest_item = self.manifest.get(old)
        else:
            manifest_item = old

        if not manifest_item:
            raise EPUBError(f"Can't rename '{old}: not in manifest")

        old_id = manifest_item.id

        existing = self.manifest.get(new)
        if existing:
            raise EPUBError(f"Can't rename to already existing id '{new}' ({existing})")

        # cover-image in metadata
        cover = self.metadata.get_valued("cover")
        if cover and cover.value == old:
            cover.value = new

        # spine tag
        if self.spine.tag.attrs["toc"] == old_id:
            self.spine.tag.attrs["toc"] = new

        spine_item = self.spine.get(old_id)
        if spine_item:
            spine_item.idref = new

        manifest_item.id = new

    def get_spine_item(
        self,
        resource: Resource | ResourceIdentifier,
    ) -> SpineItemRef | None:
        """
        Get spine item associated with a resource or filename.

        >>> with EPUB(sample) as book:
        ...     item = book.get_spine_item("Text/chapter1.xhtml")
        ...     print(item.idref)
        chapter1

        Args:
            resource: The resource, its filename, its id or its manifest item
                to look for in the spine.

        Retrns:
            The spine item if found, None otherwise.
        """
        if isinstance(resource, Resource):
            resource = resource.filename

        epub_id = self.resources.ri_to_id(resource)
        if epub_id:
            return self.spine.get(epub_id)
        return None

    def get_spine_position(
        self,
        resource: Resource | ResourceIdentifier,
    ) -> int | None:
        """
        Get the 0-indexed position of a resource in the spine.

        >>> with EPUB(sample) as book:
        ...     position = book.get_spine_position("Text/chapter1.xhtml")
        ...     print(position)
        0

        Args:
            resource: The resource (or its filename, its id or its manifest item)
                the position of which is to be detected in the spine.

        Returns:
            The 0-indexed position of the resource in the spine, or None if
            the resource is not in the spine.
        """

        if isinstance(resource, Resource):
            resource = resource.filename

        epub_id = self.resources.ri_to_id(resource)
        if epub_id:
            return self.spine.get_position(epub_id)
        return None

    def update_manifest_properties(self) -> None:
        """
        Update manifest properties by detecting them from the resources
        See https://www.w3.org/TR/epub-33/#sec-item-resource-properties.
        """

        for item in self.manifest.items:
            resource = self.resources.get(item.filename, XMLResource)
            if resource:
                for prop in ["mathml", "remote-resources", "scripted", "switch"]:
                    item.remove_property(prop)

                for property in detect_manifest_properties(resource.soup):
                    item.add_property(property)

    def reset_toc(
        self,
        targets_selector: str | None = "h1, h2, h3, h4, h5, h6",
        include_filenames: bool = False,
        spine_only: bool = True,
        reset_ncx: Literal[False] | None = None,
        resource_class: type[Resource] = ContentDocument,
        title: str | None = None,
    ):
        """
        Reset the table of contents in the navigation document by
        detecting targets in content documents. May replace any
        existing TOC.

        Args:
            targets_selector: A CSS selector to detect targets in content
                documents. If None, all headings will be used.
            include_filenames: Whether to include filenames in the TOC.
            spine_only: Whether to only include documents in the spine. This
                ensures the TOC is in reading order.
            reset_ncx: Whether to also reset the NCX file. If None (default),
                will reset the NCX only if an NCX already exists.
            resource_class: The class of resources to consider when searching
                for references for the TOC. Defaults to ContentDocument,
                which includes XHTML and SVG documents.
            title: The title to use for the TOC. If None, will keep the existing
                title if any, or use leave empty if none. Caution is advised, as
                an empty TOC title is not conformant with the EPUB spec.

        Raises:
            EPUBError: If `reset_ncx` is `True` but the book has no NCX file.
        """

        return reset_toc(
            self,
            targets_selector,
            include_filenames,
            spine_only,
            reset_ncx,
            resource_class,
            title,
        )

    def reset_page_list(
        self,
        id_format: str = "page_{page}",
        label_format: str = "{page}",
        pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
        reset_ncx: Literal[False] | None = None,
    ):
        """
        Reset the page list in the navigation document by detecting
        pagebreaks in content documents. Will replace any existing page
        list.

        Args:
            id_format: A format string to generate the id of each pagebreak.
                The string must contain a '{page}' placeholder, which will
                be replaced with the page number (starting at 1).
            label_format: A format string to generate the label of each
                pagebreak. The string must contain a '{page}' placeholder,
                which will be replaced with the page number (starting at 1).
            pagebreak_selector: A CSS selector to detect pagebreaks in
                content documents. Defaults to
                '[role="doc-pagebreak"], [epub|type="pagebreak"]'.
            reset_ncx: Whether to also reset the NCX file. If None (default),
                will reset the NCX only if an NCX file already exists.

        Raises:
            EPUBError: If `reset_ncx` is `True` but the book has no NCX file.
        """
        return reset_page_list(
            self,
            id_format,
            label_format,
            pagebreak_selector,
            reset_ncx,
        )

    def create_page_list(
        self,
        id_format: str = "page_{page}",
        label_format: str = "{page}",
        pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
        reset_ncx: Literal[False] | None = None,
    ):
        """
        Create new page list in the navigation document by detecting
        pagebreaks in content documents. Will raise an error if a page
        list already exists.

        Args:
            id_format: A format string to generate the id of each pagebreak.
                The string must contain a '{page}' placeholder, which will
                be replaced with the page number (starting at 1).
            label_format: A format string to generate the label of each
                pagebreak. The string must contain a '{page}' placeholder,
                which will be replaced with the page number (starting at 1).
            pagebreak_selector: A CSS selector to detect pagebreaks in
                content documents. Defaults to
                '[role="doc-pagebreak"], [epub|type="pagebreak"]'.
            reset_ncx: Whether to also reset the NCX file. If None (default),
                will reset the NCX only if an NCX file already exists.

        Raises:
            EPUBError: If a page list already exists.
        """
        return create_page_list(
            self,
            id_format,
            label_format,
            pagebreak_selector,
            reset_ncx,
        )

    def reset_landmarks(
        self,
        include_toc: bool = True,
        targets_selector: str | None = None,
        default_epub_type: str = "chapter",
    ):
        """
        Reset the landmarks in the navigation document by detecting
        targets in content documents, and optionally including the TOC.
        Will replace existing landmarks.

        Args:
            include_toc: Whether to include the TOC in the landmarks.
            targets_selector: A CSS selector to detect targets in resources.
        """

        return reset_landmarks(self, include_toc, targets_selector, default_epub_type)

    def create_landmarks(
        self,
        include_toc: bool = True,
        targets_selector: str | None = None,
        default_epub_type: str = "chapter",
    ):
        """
        Create landmarks in the navigation document by detecting targets in
        content documents, and optionally including the TOC. Will raise error
        if landmarks already exist.

        Args:
            include_toc: Whether to include the TOC in the landmarks.
            targets_selector: A CSS selector to detect targets in resources.
        """

        return create_landmarks(self, include_toc, targets_selector, default_epub_type)

    def generate_ncx(self, filename: str | Path | None = None) -> NCXFile:
        """
        Generate a new NCX file based on the book metadata and navigation
        document, and add it to the EPUB. Will raise an error if an NCX
        file already exists.

        Args:
            filename: The filename to use for the NCX file. If None, will
                use 'toc.ncx' in the same directory as the package document.

        Raises:
            EPUBError: If an NCX file already exists (try `reset_ncx` instead),
                or if the book metadata does not contain a title.
        """
        return generate_ncx(self, filename)

    def reset_ncx(self) -> NCXFile:
        """
        Reset the contents of the NCX file based on the book metadata and
        navigation document. If no NCX file exists, will generate a new one
        named 'toc.ncx' in the same directory as the package document.

        Raises:
            EPUBError: If the book metadata does not contain a title.
        """
        return reset_ncx(self, self.ncx)

    def select(self, selector: str) -> Generator[tuple[Resource, bs4.Tag]]:
        """
        Select elements matching a CSS selector in all content documents.

        Args:
            selector: A CSS selector to match elements.

        Yields:
            Tuples (resource, tag), where tag corresponds to the the mathced
                element and resource is the content document containing the tag.
        """

        for document in self.documents.filter(XMLResource):
            for tag in document.soup.select(selector):
                yield (document, tag)

    @property
    def base_dir(self) -> Path:
        """
        Returns the base directory for the resources in this EPUB. This is an
        holistic property, and the spec does not define it. There may be more
        than one base directory in an EPUB. This is the one containing the
        package document.
        """

        return Path(self.package_document.filename).parent

    def add_generator_tag(self) -> None:
        """
        Add a generator meta tag to the metadata, containing the epublib version
        used to edit or generate this EPUB. If such tag already exists and
        version is up to date, does nothing.
        """

        generator = self.metadata.get("generator")
        if not generator:
            generator = self.metadata.add_opf("generator", "Edited with epublib")

        version = get_epublib_version()
        if version:
            version_item = self.metadata.get("epublib version")
            if not version_item:
                __ = self.metadata.add_opf("epublib version", version)
            else:
                version_item.value = version

    def remove_generator_tag(self) -> None:
        """Remove the epublib generator tag of the metadata, if any."""

        generator = self.metadata.get("generator")
        if (
            generator
            and isinstance(generator, ValuedMetadataItem)
            and "epublib" in generator.value
        ):
            self.metadata.remove_item(generator)

        version_item = self.metadata.get("epublib version")
        if version_item:
            self.metadata.remove_item(version_item)

    def close(self) -> None:
        """Close the EPUB and its underlying resources."""
        for resource in self.resources:
            resource.close()
        self.source.close()

    @property
    def closed(self) -> bool:
        """Check if the EPUB is closed."""
        return self.source.closed

    def _check_closed(self, msg: str = "EPUB is already closed") -> None:
        if self.closed:
            raise ClosedEPUBError(msg)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:  # type: ignore[Any]
        self.close()

    @override
    def __repr__(self) -> str:
        title = (self.metadata.title or "").strip()
        if title:
            title = f"title='{title}'"
        return f"{self.__class__.__name__}({title})"
