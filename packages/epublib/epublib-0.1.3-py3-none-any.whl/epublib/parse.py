from zipfile import ZipInfo

from epublib.exceptions import NotEPUBError
from epublib.package.manifest import ManifestItem
from epublib.package.resource import PackageDocument
from epublib.resources import Resource, XMLResource
from epublib.resources.create import create_resource
from epublib.source import SourceProtocol
from epublib.util import attr_to_str


def parse_container_file(source: SourceProtocol) -> tuple[XMLResource, str]:
    """
    Parse the container.xml file at the root of the document. Only
    consider the first rootfile. Return also the filename of the package
    document

    Args:
        source: The source to read the EPUB from.

    Returns:
        A tuple (container, package_fn) of the container XMLResource and the
        package document filename.
    """

    try:
        info = source.getinfo("META-INF/container.xml")
    except KeyError as error:
        raise NotEPUBError("Missing 'META-INF/container.xml'") from error
    container = XMLResource(source.open(info), info)
    rootfile = container.soup.select_one("rootfile")

    if not rootfile:
        raise NotEPUBError("Can't find rootfile in container.xml")

    package_document_filename = attr_to_str(rootfile.attrs.get("full-path", ""))

    if not package_document_filename:
        raise NotEPUBError("rootfile in container.xml has no full-path")

    return container, package_document_filename


def parse_package_document(source: SourceProtocol, filename: str) -> PackageDocument:
    """Parse the package document (META-INF/container.xml)"""

    info = source.getinfo(filename)
    return PackageDocument(source.open(info), info)


def init_resource(
    source: SourceProtocol,
    info: ZipInfo,
    manifest_item: ManifestItem | None,
) -> Resource:
    """Initialize a Resource object from a ZipInfo and optional ManifestItem"""

    args = source.open(info), info

    if manifest_item is None:
        return Resource(*args)

    return create_resource(
        source.open(info),
        info,
        manifest_item.media_type,
        is_nav=manifest_item.has_property("nav"),
    )


def parse(
    source: SourceProtocol,
) -> tuple[XMLResource, PackageDocument, list[Resource]]:
    """Read and parse the EPUB file from the source"""
    container_file, package_document_filename = parse_container_file(source)
    package_document = parse_package_document(source, package_document_filename)

    resources: list[Resource] = []
    for info in source.infolist():
        if info.is_dir():
            continue

        manifest_item = package_document.manifest.get(info.filename)
        if info.filename == package_document.filename:
            resources.append(package_document)
        elif info.filename == container_file.filename:
            resources.append(container_file)
        else:
            resources.append(init_resource(source, info, manifest_item))

    return container_file, package_document, resources
