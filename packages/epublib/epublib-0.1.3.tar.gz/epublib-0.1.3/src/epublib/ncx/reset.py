from pathlib import Path

from bs4.element import NamespacedAttribute

from epublib.exceptions import EPUBError
from epublib.ncx.resource import NCXFile
from epublib.package.metadata import BookMetadata, ValuedMetadataItem
from epublib.types import BookProtocol

ncx_template = """<?xml version="1.0" encoding="UTF-8"?>
<ncx version="2005-1" {lang_attr} xmlns="http://www.daisy.org/z3986/2005/ncx/">
<head></head>
<docTitle><text>{title}</text></docTitle>
<navMap></navMap>
</ncx
"""


def get_minimal_ncx_content(title: str, lang: str | None) -> bytes:
    """
    Get a minimal NCX file content with the given title and language.
    Caution: the minimality of this template is in regard to the parsing
    available in this library. To get a minimal valid NCX file, consider
    using `EPUB.generate_ncx` instead.

    Args:
        title: The title of the NCX document.
        lang: The language of the NCX document, or `None` for no language.
    """
    if lang:
        lang_attr = f'xml:lang="{lang}"'
    else:
        lang_attr = ""
    return ncx_template.format(title=title, lang_attr=lang_attr).encode()


def generate_ncx(book: BookProtocol, filename: str | Path | None = None) -> NCXFile:
    """
    Generate an NCX file for the given book, based on its metadata and
    navigation document. The generated NCX file will be added to the book's
    resources, and the book's spine will be updated to reference it.

    Typically used from an `EPUB` instance:

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     if not book.ncx:
    ...         book.generate_ncx()
    ...     else:
    ...         book.reset_ncx()
    NCXFile(...)

    Args:
        book: The book to generate the NCX for.
        filename: The filename to use for the NCX file in the EPUB archive. If
            `None`, "toc.ncx" in the book's base directory will be used.

    Returns:
        The generated NCX file.
    """
    if filename is None:
        filename = book.base_dir / "toc.ncx"

    if not book.metadata.title:
        raise EPUBError("Can't generate NCX without book title in metadata")

    if book.ncx is not None:
        raise EPUBError(
            "Can't generate NCX as it already exists. Try "
            f"{book.__class__.__name__}.reset_ncx() instead"
        )

    ncx = NCXFile(
        get_minimal_ncx_content(
            book.metadata.title,
            book.metadata.language,
        ),
        filename,
    )

    ncx = reset_ncx(book, ncx)
    book.resources.add(ncx)
    book.spine.tag["toc"] = book.manifest[ncx.filename].id
    return ncx


def reset_author(ncx: NCXFile, metadata: BookMetadata) -> None:
    creator_item = metadata.get("creator")
    creator = (
        creator_item.value if isinstance(creator_item, ValuedMetadataItem) else None
    )

    for author in ncx.authors:
        if author.text == creator:
            continue
        __ = ncx.remove_author(author)

    if creator and not ncx.get_author(creator):
        __ = ncx.add_author(creator)


def reset_ncx(book: BookProtocol, ncx: NCXFile | None = None) -> NCXFile:
    """
    Reset the given NCX file to match the book's metadata and navigation
    document. If no NCX file is given, the book's existing NCX file will be
    used. If the book has no NCX file, a new one will be generated.

    Typically used from an `EPUB` instance:
    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     if not book.ncx:
    ...         book.generate_ncx()
    ...     else:
    ...         book.reset_ncx()
    NCXFile(...)

    Args:
        book: The book to reset the NCX for.
        ncx: The NCX file to reset, or `None` to use the book's existing NCX
            file, or generate a new one if none exists.
    """

    if not book.metadata.title:
        raise EPUBError("Can't reset NCX without book title in metadata")

    if ncx is None:
        ncx = book.ncx

    if ncx is None:
        return generate_ncx(book)

    ncx.title.text = book.metadata.title
    reset_author(ncx, book.metadata)

    if book.metadata.language:
        ncx.soup.ncx[NamespacedAttribute("xml", "lang")] = book.metadata.language

    __ = ncx.sync_toc(book.nav)
    if book.nav.page_list:
        __ = ncx.sync_page_list(book.nav)
    __ = ncx.sync_head(book.metadata)

    return ncx
