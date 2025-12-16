from collections.abc import Iterable
from typing import cast

import bs4

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.nav.resource import NavigationDocument
from epublib.nav.util import LandmarkEntryData, PageBreakData, TOCEntryData, detect_page
from epublib.resources import ContentDocument, Resource, XMLResource
from epublib.types import BookProtocol
from epublib.util import (
    attr_to_str,
    new_id_in_tag,
)


def get_flat_toc_entries(
    resources: Iterable[Resource],
    targets_selector: str | None = None,
    include_filenames: bool = False,
) -> list[TOCEntryData]:
    entries: list[TOCEntryData] = []

    for resource in resources:
        if targets_selector is None or include_filenames:
            label = resource.get_title()
            entries.append(TOCEntryData(resource.filename, label=label))
        if targets_selector and isinstance(resource, XMLResource):
            soup = cast(bs4.BeautifulSoup, resource.soup)
            for index, tag in enumerate(soup.select(targets_selector)):
                label = tag.get_text()
                identifier = attr_to_str(tag.get("id"))
                if not identifier:
                    base_id = label if label else f"toc-target-{index + 1}"
                    identifier = tag["id"] = new_id_in_tag(base_id, soup)
                entries.append(
                    TOCEntryData(
                        resource.filename,
                        label=label,
                        id=identifier,
                    )
                )

    return entries


def get_nested_toc_entries(
    resources: Iterable[XMLResource],
    targets_selector: str,
    include_filenames: bool,
) -> list[TOCEntryData]:
    assert set(map(str.strip, targets_selector.split(","))) <= {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }
    headings = {
        name: int(name[1])
        for name in sorted(map(str.strip, targets_selector.split(",")))
    }

    entries: list[TOCEntryData] = []

    for resource in resources:
        stack: list[tuple[int, TOCEntryData]] = []

        if include_filenames:
            label = resource.get_title()
            entries.append(TOCEntryData(resource.filename, label=label))

        for count, tag in enumerate(resource.soup.select(targets_selector), start=1):
            level = headings[tag.name]
            identifier = attr_to_str(tag.get("id"))
            label = tag.get_text()
            if not identifier:
                base_id = label if label else f"heading-{count}"
                identifier = tag["id"] = new_id_in_tag(base_id, resource.soup)

            entry = TOCEntryData(filename=resource.filename, label=label, id=identifier)
            while stack and stack[-1][0] >= level:
                __ = stack.pop()

            if stack:
                stack[-1][1].children.append(entry)
            else:
                entries.append(entry)

            stack.append((level, entry))

    return entries


def reset_toc(
    book: BookProtocol,
    targets_selector: str | None = "h1, h2, h3, h4, h5, h6",
    include_filenames: bool = False,
    spine_only: bool = True,
    reset_ncx: bool | None = None,
    resource_class: type[Resource] = ContentDocument,
    title: str | None = None,
) -> None:
    """Reset the table of contents in the navigation document to the given
    entries. Will replace any existing table of contents.

    Typically used indirectly from an EPUB instance with the `reset_toc` or
    `create_toc` methods.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     book.reset_toc(title = "New table of Contents")

    Args:
        book: The book to reset the table of contents for.
        targets_selector: A CSS selector to find the targets for the table of
            contents. If `None`, only the resource titles will be used.
            Defaults to `"h1, h2, h3, h4, h5, h6"`.
        include_filenames: Whether to include the resource filenames as top-level
            entries in the table of contents. Defaults to `False`.
        spine_only: Whether to only include resources in the spine. Defaults to
            `True`. Guarantees the toc is in reading order.
        reset_ncx: Whether to also reset the NCX file if there is one. If `None`
            (the default), the NCX file will be reset if it exists in the EPUB.
        resource_class: The resource class to consider. Defaults to
            `ContentDocument`.
        title: An optional title for the table of contents. If `None`, the
            existing title will be kept if there is one.

    Raises:
        EPUBError: If `reset_ncx` is `True` but the book has no NCX file.
    """
    if reset_ncx and not book.ncx:
        raise EPUBError.missing_ncx(book, "reset_toc")

    if spine_only:
        resources = (book.resources[item] for item in book.spine.items)
    else:
        resources = book.resources.filter(resource_class)

    if targets_selector and set(map(str.strip, targets_selector.split(","))) <= {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }:
        entries = get_nested_toc_entries(
            (
                cast(ContentDocument[bs4.BeautifulSoup], res)
                for res in resources
                if isinstance(res, ContentDocument)
            ),
            targets_selector,
            include_filenames,
        )
    else:
        entries = get_flat_toc_entries(resources, targets_selector, include_filenames)

    if title is None:
        try:
            title = book.nav.toc.title if book.nav.toc else None
        except EPUBError:
            pass

    book.nav.reset_toc(entries)

    if (reset_ncx or reset_ncx is None) and book.ncx:
        book.ncx.nav_map.reset(entries)

    if title is not None:
        book.nav.toc.title = title


def reset_page_list(
    book: BookProtocol,
    id_format: str = "page_{page}",
    label_format: str = "{page}",
    pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
    reset_ncx: bool | None = None,
):
    """Reset the page list in the navigation document based on the pagebreak
    elements in the book's content documents. Will replace any existing page
    list.

    Typically used indirectly from an EPUB instance with the `reset_page_list`.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     book.reset_page_list()

    Args:
        book: The book to reset the page list for.
        id_format: A format string to generate IDs for pagebreak elements that
            don't have one. The string must contain a `{page}` placeholder which
            will be replaced with the page number. Defaults to `"page_{page}"`.
        label_format: A format string to generate labels for the page list
            entries. The string must contain a `{page}` placeholder which will be
            replaced with the page number. Defaults to `"{page}"`.
        pagebreak_selector: A CSS selector to find the pagebreak elements.
            Defaults to `'[role="doc-pagebreak"], [epub|type="pagebreak"]'`.
        reset_ncx: Whether to also reset the NCX file if there is one. If `None`
            (the default), the NCX file will be reset if it exists

    Raises:
        EPUBError: If `reset_ncx` is `True` but the book has no NCX file.
    """

    pagebreaks: list[PageBreakData] = []

    if reset_ncx and not book.ncx:
        raise EPUBError.missing_ncx(book, "reset_page_list")

    resources = (book.documents[item] for item in book.spine.items)

    for resource in resources:
        for tag in resource.soup.select(pagebreak_selector):
            page = detect_page(tag)
            if not page:
                continue

            if not tag.get("id"):
                tag["id"] = new_id_in_tag(
                    id_format.format(page=EPUBId.to_valid(page)),
                    resource.soup,
                )

            pagebreaks.append(
                PageBreakData(
                    filename=f"{resource.filename}#{attr_to_str(tag['id'])}",
                    label=label_format.format(page=page),
                )
            )

    book.nav.reset_page_list(pagebreaks)
    if book.ncx and (reset_ncx or reset_ncx is None):
        book.ncx.reset_page_list(pagebreaks)


def create_page_list(
    book: BookProtocol,
    id_format: str = "page_{page}",
    label_format: str = "{page}",
    pagebreak_selector: str = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
    reset_ncx: bool | None = None,
):
    """Create a page list in the navigation document based on the pagebreak
    elements in the book's content documents.

    Typically used indirectly from an EPUB instance with the `create_page_list`
    method.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     book.create_page_list()

    Args:
        book: The book to create the page list for.
        id_format: A format string to generate IDs for pagebreak elements that
            don't have one. The string must contain a `{page}` placeholder which
            will be replaced with the page number. Defaults to `"page_{page}"`.
        label_format: A format string to generate labels for the page list
            entries. The string must contain a `{page}` placeholder which will be
            replaced with the page number. Defaults to `"{page}"`.
        pagebreak_selector: A CSS selector to find the pagebreak elements.
            Defaults to `'[role="doc-pagebreak"], [epub|type="pagebreak"]'`.
        reset_ncx: Whether to also reset the NCX file if there is one. If `None`
            (the default), the NCX file will be reset if it exists.

    Raises:
        EPUBError: If `reset_ncx` is `True` but the book has no NCX file, or if
            the book already has a page list.
    """

    if reset_ncx and not book.ncx:
        raise EPUBError.missing_ncx(book, "create_page_list")

    if book.nav.page_list is not None:
        raise EPUBError(
            "Can't create page list as it already exists. "
            f"Consider using '{book.__class__.__name__}.reset_page_list'"
        )

    return reset_page_list(
        book,
        id_format,
        label_format,
        pagebreak_selector,
        reset_ncx,
    )


def reset_landmarks(
    book: BookProtocol,
    include_toc: bool = True,
    targets_selector: str | None = None,
    default_epub_type: str = "chapter",
):
    """Reset the landmarks in the navigation document by detecting targets in
    content documents, and optionally including the TOC. Will replace existing
    landmarks.

    Typically used indirectly from an EPUB instance with the `reset_landmarks`
    method.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     book.reset_landmarks(targets_selector='#cover, #toc')

    If more control is needed over which landmarks to include, use the
    navigation document's `reset_landmarks` method directly.

    >>> from epublib import EPUB
    >>> from epublib.nav.util import LandmarkEntryData
    >>> with EPUB(sample) as book:
    ...     entries = [
    ...         LandmarkEntryData('cover.xhtml#cover', 'Cover', 'cover'),
    ...         LandmarkEntryData('toc.xhtml#toc', 'Table of Contents', 'toc'),
    ...     ]
    ...     book.nav.reset_landmarks(entries)


    Args:
        book: The book to reset the landmarks for.
        include_toc: Whether to include the table of contents as a landmark.
            Defaults to `True`.
        targets_selector: A CSS selector to find the targets for the landmarks.
            If `None`, no additional landmarks will be added. Defaults to `None`.
        default_epub_type: The default EPUB type to use for landmarks found via
            the `targets_selector`. Defaults to `"chapter"`.
    """

    entries: list[LandmarkEntryData] = []
    if include_toc and book.nav and book.nav.toc:
        tag = book.nav.toc.tag
        if not book.nav.toc.title or not book.nav.toc.title.strip():
            raise EPUBError("Can't include TOC in landmarks as it has no title")

        if not tag.get("id"):
            tag["id"] = new_id_in_tag("toc", book.nav.soup)

        entries.append(
            LandmarkEntryData(
                f"{book.nav.filename}#{attr_to_str(tag['id'])}",
                book.nav.toc.title,
                "toc",
            )
        )

    if targets_selector:
        for resource in book.resources.filter(XMLResource):
            if include_toc and isinstance(resource, NavigationDocument):
                continue

            for index, tag in enumerate(resource.soup.select(targets_selector)):
                label = tag.get_text()

                if not label.strip():
                    continue

                identifier = attr_to_str(tag.get("id"))
                if not identifier:
                    base_id = label if label else f"toc-target-{index + 1}"
                    identifier = tag["id"] = new_id_in_tag(base_id, resource.soup)

                entries.append(
                    LandmarkEntryData(
                        f"{resource.filename}#{identifier}",
                        label,
                        default_epub_type,
                    )
                )
    book.nav.reset_landmarks(entries)


def create_landmarks(
    book: BookProtocol,
    include_toc: bool = True,
    targets_selector: str | None = None,
    default_epub_type: str = "chapter",
):
    """Create landmarks in the navigation document by detecting targets in
    content documents, and optionally including the TOC. Will raise error if
    landmarks already exist.

    Typically used indirectly from an EPUB instance with the `create_landmarks`
    method.

    >>> from epublib import EPUB
    >>> with EPUB(sample) as book:
    ...     book.reset_landmarks(targets_selector='#cover, #toc')

    If more control is needed over which landmarks to include, use the
    navigation document's `reset_landmarks` method directly.

    >>> from epublib import EPUB
    >>> from epublib.nav.util import LandmarkEntryData
    >>> with EPUB(sample) as book:
    ...     entries = [
    ...         LandmarkEntryData('cover.xhtml#cover', 'Cover', 'cover'),
    ...         LandmarkEntryData('toc.xhtml#toc', 'Table of Contents', 'toc'),
    ...     ]
    ...     book.nav.reset_landmarks(entries)


    Args:
        book: The book to reset the landmarks for.
        include_toc: Whether to include the table of contents as a landmark.
            Defaults to `True`.
        targets_selector: A CSS selector to find the targets for the landmarks.
            If `None`, no additional landmarks will be added. Defaults to `None`.
        default_epub_type: The default EPUB type to use for landmarks found via
            the `targets_selector`. Defaults to `"chapter"`.
    """
    if book.nav.landmarks is not None:
        raise EPUBError(
            "Can't create landmarks as it already exists. "
            f"Consider using '{book.__class__.__name__}.reset_landmarks'"
        )

    return reset_landmarks(book, include_toc, targets_selector, default_epub_type)
