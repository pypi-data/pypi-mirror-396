from pathlib import Path
from typing import IO
from zipfile import ZipInfo

from epublib.exceptions import EPUBError
from epublib.media_type import MediaType
from epublib.nav.resource import NavigationDocument
from epublib.ncx.resource import NCXFile
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    info_to_zipinfo,
)


def create_resource(
    file: IO[bytes] | bytes,
    info: ZipInfo | str | Path,
    media_type: MediaType | str | None = None,
    is_nav: bool = False,
) -> Resource:
    """
    Create a new resource outside of any EPUB.

    Args:
        file: A file-like object or bytes representing the resource's data.
        info: Metadata about the resource, either as a ZipInfo object,
            a string or Path object representing a filename.
        media_type: The media type of the resource. If None, it will be
            inferred from the filename in `info`.
        is_nav: Whether this resource is the navigation document.

    Returns:
        An instance of a subclass of Resource corresponding to the arguments.

    Raises:
        EPUBError:
            - If `is_nav` is True but the media type is not XHTML or SVG.
            - If the media type is not provided and cannot be determined from
              the filename.
    """
    zipinfo = info_to_zipinfo(info)

    if media_type is None:
        media_type = MediaType.from_filename(zipinfo.filename)
    else:
        media_type = MediaType(media_type)

    if (
        media_type is None
        or Path(zipinfo.filename).parts[0] == "META-INF"
        or zipinfo.filename == "mimetype"
    ):
        return Resource(file, zipinfo)

    if media_type is MediaType.NCX:
        return NCXFile(file, zipinfo, media_type)

    if media_type is MediaType.IMAGE_SVG or media_type is MediaType.XHTML:
        if is_nav:
            return NavigationDocument(file, zipinfo, media_type)
        return ContentDocument(file, zipinfo, media_type)

    if is_nav:
        raise EPUBError(
            f"Found media type of '{zipinfo.filename}' to be "
            f"'{media_type}', which is incompatible with argument "
            "'is_nav=True'. Only XHTML or SVG documents can be the "
            "navigation document"
        )

    return PublicationResource(file, zipinfo, media_type)


def create_resource_from_path(
    path: str | Path,
    info: ZipInfo | str | Path | None = None,
    media_type: MediaType | str | None = None,
    is_nav: bool = False,
):
    """
    Create a new resource from existing file. The resource is not related to EPUB.

    Args:
        file: A file-like object or bytes representing the resource's data.
        info: Metadata about the resource, either as a ZipInfo object,
            a string or Path object representing a filename.
        media_type: The media type of the resource. If None, it will be
            inferred from the filename in `info`.
        is_nav: Whether this resource is the navigation document.

    Returns:
        An instance of a subclass of Resource corresponding to the arguments.

    Raises:
        EPUBError:
            - If `is_nav` is True but the media type is not XHTML or SVG.
            - If the media type is not provided and cannot be determined from
              the filename.
    """
    file = open(path, "rb")

    if info is None:
        info = Path(path).name

    zipinfo = info

    if not isinstance(info, ZipInfo):
        zipinfo = ZipInfo.from_file(path, info, strict_timestamps=False)

    return create_resource(file, zipinfo, media_type, is_nav)
