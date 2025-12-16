from datetime import datetime
from pathlib import Path
from typing import final

import bs4
import pytest

from epublib import EPUB
from epublib.exceptions import EPUBError, EPUBWarning
from epublib.media_type import MediaType
from epublib.package.metadata import (
    DublinCoreMetadataItem,
    GenericMetadataItem,
    LinkMetadataItem,
    OPF2MetadataItem,
)

from . import SAMPLES_DIR


@final
class TestEPUBMetadata:
    sample_filename = SAMPLES_DIR / "sample.epub"

    def test_metadata(self, epub: EPUB) -> None:
        assert epub.metadata
        assert epub.package_document.metadata
        assert repr(epub.metadata)

    def test_read(self, epub: EPUB) -> None:
        assert epub.metadata.identifier
        assert epub.metadata.title
        assert epub.metadata.modified
        assert epub.metadata.language

    def test_edit(self, epub: EPUB, epub_path: Path) -> None:
        date = datetime.now()
        epub.metadata.identifier = "987654321"
        epub.metadata.title = "Testing title"
        epub.metadata.modified = date
        epub.metadata.language = "ps-AR"
        __ = epub.metadata.add(name="test", value="test value")

        epub.write(epub_path)
        epub = EPUB(epub_path)

        assert epub.metadata.identifier == "987654321"
        assert epub.metadata.title == "Testing title"
        assert epub.metadata.modified
        assert epub.metadata.modified.astimezone() == date.astimezone().replace(
            microsecond=0
        )
        assert epub.metadata.language == "ps-AR"

        new_item = epub.metadata.get("test", GenericMetadataItem)
        assert new_item
        assert new_item.value == "test value"

    def test_edit_no_dups(self, epub: EPUB) -> None:
        epub.metadata.title = "Test title"
        assert len(epub.metadata.tag.find_all("dc:title")) == 1

        epub.metadata.identifier = "123456789"
        assert len(epub.metadata.tag.find_all("dc:identifier")) == 1

        epub.metadata.language = "es-ES"
        assert len(epub.metadata.tag.find_all("dc:language")) == 1

        epub.metadata.modified = datetime.now()
        assert (
            len(
                epub.metadata.tag.find_all(
                    "opf:meta",
                    attrs={"property": "dcterms:modified"},
                )
            )
            == 1
        )

    def test_edit_extra_attr(self, epub: EPUB, epub_path: Path) -> None:
        epub = EPUB(self.sample_filename)

        title = epub.metadata.get("title")
        assert title

        title.tag["data-testattr"] = "testval"

        epub.write(epub_path)
        epub = EPUB(epub_path)
        title = epub.metadata.get("title")

        assert title
        assert title.tag["data-testattr"] == "testval"

    def test_unique_identifier(self, epub: EPUB) -> None:
        package = epub.package_document.soup.package
        assert package
        package["unique-identifier"] = "xpto-id"

        id_item = epub.metadata.get("identifier")
        assert id_item

        epub.metadata.remove_item(id_item)

        epub.metadata.identifier = "987654321"
        assert epub.metadata["identifier"].tag["id"] == "xpto-id"

    def test_link_metadata(self, epub: EPUB) -> None:
        link_item = epub.metadata.add_link(
            href="https://example.com",
            rel="related",
            media_type=MediaType("text/html"),
        )
        assert link_item
        assert link_item.tag.name == "link"
        assert link_item.tag["href"] == "https://example.com"
        assert link_item.tag["rel"] == "related"
        assert link_item.tag["media-type"] == "text/html"

        link_item = epub.metadata.get("https://example.com")
        assert link_item
        assert link_item.tag.name == "link"
        assert link_item.tag["href"] == "https://example.com"
        assert link_item.tag["rel"] == "related"
        assert link_item.tag["media-type"] == "text/html"

        epub.metadata.remove_item(link_item)
        link_item = epub.metadata.get("https://example.com")
        assert link_item is None

        soup = bs4.BeautifulSoup(
            '<link href="https://example.com" media-type="text/html" rel="related"/>',
            "xml",
        )
        assert soup.link
        __ = epub.metadata.tag.append(soup.link)
        epub.package_document.on_soup_change()

        link_item = epub.metadata.get("https://example.com")
        assert isinstance(link_item, LinkMetadataItem)

    def test_not_recognized(self, epub: EPUB) -> None:
        soup = bs4.BeautifulSoup("<none />", "xml")
        none = soup.none
        assert none
        __ = epub.metadata.tag.append(none)
        epub.package_document.on_soup_change()

        with pytest.warns(EPUBWarning):
            __ = epub.metadata

        with pytest.raises(EPUBError):
            __ = LinkMetadataItem.from_tag(soup=soup, tag=none)
        with pytest.raises(EPUBError):
            __ = DublinCoreMetadataItem.from_tag(soup=soup, tag=none)
        with pytest.raises(EPUBError):
            __ = OPF2MetadataItem.from_tag(soup=soup, tag=none)
        with pytest.raises(EPUBError):
            __ = GenericMetadataItem.from_tag(soup=soup, tag=none)

    def test_remove_obligatory(self, epub: EPUB) -> None:
        epub.metadata.remove("identifier")
        assert epub.metadata.identifier is None

        item = epub.metadata.get_valued("dcterms:modified")
        if item:
            item.value = "something completely different"
        assert epub.metadata.modified is None

        epub.metadata.remove("dcterms:modified")
        assert epub.metadata.modified is None

        epub.metadata.remove("title")
        assert epub.metadata.title is None

        epub.metadata.remove("language")
        assert epub.metadata.language is None
