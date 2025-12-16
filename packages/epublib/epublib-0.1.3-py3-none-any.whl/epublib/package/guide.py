from dataclasses import dataclass
from typing import Annotated, ClassVar, override

from epublib.xml_element import HrefElement, ParentOfHref, XMLAttribute


@dataclass(kw_only=True)
class GuideItem(HrefElement):
    """
    An item in the EPUB guide (legacy feature).

    Args:
        soup: The BeautifulSoup object of which this item is part of.
        filename: The filename of the referenced resource. If not given, it will
            be derived from `href` and `own_filename`. Only one of `href` and
            `filename` should be given.
        href: The href of the referenced resource. If not given, it will be
            derived from `filename` and `own_filename`. Only one of `href`
            and `filename` should be given.
        own_filename: The filename of the file containing this item.
        title: The title of the reference.
        type: The type of the reference
    """

    type: Annotated[str, XMLAttribute()]
    title: Annotated[str, XMLAttribute()]

    tag_name: ClassVar[str] = "reference"


class BookGuide(ParentOfHref[GuideItem]):
    """
    The EPUB spine, which defines the linear reading order of the book.

    Args:
        soup: The BeautifulSoup object of which this guide is part of.
        tag: The tag representing this guide. If not given, a new tag
            will be created.
        own_filename: The filename of the file containing this guide.
    """

    @override
    def add(self, filename: str, title: str, type: str) -> GuideItem:  # type: ignore[reportIncompatibleMethodOverride]
        """
        Create a new guide item and add it to this guide.

        Args:
            filename: The filename of the referenced resource.
            title: The title of the reference.
            type: The type of the reference

        Returns:
            The newly created guide item.
        """
        return super().add(filename=filename, title=title, type=type)
