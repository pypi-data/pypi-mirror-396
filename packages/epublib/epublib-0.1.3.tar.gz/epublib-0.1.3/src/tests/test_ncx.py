import re
from pathlib import Path
from typing import final

import pytest
from bs4 import Tag
from bs4.element import NamespacedAttribute

from epublib import EPUB
from epublib.exceptions import EPUBError
from epublib.nav import NavItem
from epublib.nav.util import TOCEntryData
from epublib.ncx import NCXHead, NCXNavMap, NCXNavPoint, NCXPageTarget
from epublib.resources import ContentDocument
from epublib.soup import NCXSoup
from epublib.util import attr_to_str, get_fragment, strip_fragment


@final
class TestEPUBNCX:
    def test_ncx(self, epub: EPUB, epub_path: Path) -> None:
        assert epub.ncx
        assert epub.ncx.head
        assert epub.ncx.title
        assert epub.ncx.nav_map
        assert repr(epub.ncx)

        epub.ncx.title.text = "New title"
        epub.write(epub_path)
        epub = EPUB(epub_path)

        assert epub.ncx
        assert epub.ncx.title.text == "New title"

    def test_metadata(self, epub: EPUB, epub_path: Path) -> None:
        assert epub.ncx
        assert epub.ncx.head
        __ = epub.ncx.head.uid
        __ = epub.ncx.head.depth
        __ = epub.ncx.head.total_page_count
        __ = epub.ncx.head.max_page_number

        epub.ncx.head.uid = "new-uid"
        epub.ncx.head.depth = 2
        epub.ncx.head.total_page_count = 100
        epub.ncx.head.max_page_number = 50
        new_item = epub.ncx.head.add(name="custom-meta", content="custom value")

        epub.write(epub_path)
        epub = EPUB(epub_path)
        assert epub.ncx

        assert epub.ncx.head.uid == "new-uid"
        assert epub.ncx.head.depth == 2
        assert epub.ncx.head.total_page_count == 100
        assert epub.ncx.head.max_page_number == 50
        assert epub.ncx.head["custom-meta"] == new_item

    def test_ncx_metadata_errors(self, epub: EPUB) -> None:
        soup = NCXSoup("<ncx><head /><docTitle /><navMap /></ncx>", "xml")
        head = soup.head
        head.name = "nothead"

        with pytest.raises(EPUBError):
            __ = NCXHead(soup=soup, tag=head)

        ncx = epub.reset_ncx()
        tag = ncx.head.tag.select_one('[name="dtb:uid"]')
        assert tag
        tag.decompose()

        tag = ncx.head.tag.select_one('[name="dtb:depth"]')
        assert tag
        tag.decompose()

        tag = ncx.head.tag.select_one('[name="dtb:totalPageCount"]')
        assert tag
        tag.decompose()

        ncx.on_soup_change()

        with pytest.raises(EPUBError):
            __ = ncx.head.uid

        with pytest.raises(EPUBError):
            __ = ncx.head.depth

        with pytest.raises(EPUBError):
            __ = ncx.head.total_page_count

    def test_nav_point_from_tag(self) -> None:
        html = """
        <ncx><navMap>
        <head />
        <docTitle />
        <navPoint id="navPoint1">
        <navLabel>
        <text>Lorem ipsum</text>
        </navLabel>
        <content src="../Text/Section0001.xhtml"/>
        </navPoint>
        </navMap>
        </ncx>
        """
        soup = NCXSoup(html, "xml")
        assert soup.navPoint

        nav_point = NCXNavPoint.from_tag(
            soup=soup,
            tag=soup.navPoint,
            own_filename="toc.ncx",
        )

        assert nav_point.href == "../Text/Section0001.xhtml"
        assert nav_point.text == "Lorem ipsum"
        assert nav_point.id == "navPoint1"

    def test_nav_point_add(self, epub: EPUB) -> None:
        assert epub.ncx
        nav_point = epub.ncx.nav_map.items[0]
        new_item = nav_point.add("New item", "newitemhref")
        assert new_item.text == "New item"
        assert new_item.filename == "newitemhref"

    def test_nav_point_id(self, epub: EPUB) -> None:
        assert epub.ncx
        nav_point = epub.ncx.nav_map.items[0]
        new_item = nav_point.add("New item", "newitemhref")
        other_item = nav_point.add("New item", "newitemhref")
        assert new_item.id != other_item.id

    def test_page_target_id(self, epub: EPUB) -> None:
        __ = epub.reset_ncx()
        epub.reset_page_list()
        assert epub.ncx
        assert epub.ncx.page_list

        new_item = epub.ncx.page_list.add("1", "pageref")
        other_item = epub.ncx.page_list.add("1", "pageref")
        assert new_item.id != other_item.id

    def test_nav_map(self, epub: EPUB, tmp_path: Path) -> None:
        assert epub.ncx

        nav_map = epub.ncx.nav_map
        assert nav_map
        assert nav_map.items

        for item in nav_map.items:
            assert item
            assert item.text
            assert item.href

        item = nav_map.items[0]
        nav_map.text = "Spec allows nav map with text"

        item.href = "testhref"
        item.text = "test text"

        __ = nav_map.insert(1, "New item", "newitemhref")

        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)
        epub = EPUB(outfn)

        assert epub.ncx
        nav_map = epub.ncx.nav_map
        assert nav_map
        assert nav_map.text == "Spec allows nav map with text"
        item = nav_map.items[0]
        assert item.href == "testhref"
        assert item.text == "test text"

        assert all(
            item.tag.find("text") and item.tag.find("content") for item in nav_map.items
        )

        epub.ncx.nav_map.tag.decompose()
        epub.ncx.on_soup_change()
        assert epub.ncx.nav_map

    def test_generate_ncx(self, epub: EPUB, epub_path: Path) -> None:
        with pytest.raises(EPUBError):
            __ = epub.generate_ncx()

        assert epub.ncx
        epub.resources.remove(epub.ncx)
        epub.metadata.title = ""
        with pytest.raises(EPUBError):
            __ = epub.generate_ncx()

        epub.metadata.title = "Test generate NCX"

        new_ncx = epub.generate_ncx()
        assert not epub.ncx.soup.select("docTitle[text], docAuthor[text]")

        assert epub.ncx
        assert epub.ncx is new_ncx
        assert epub.ncx.nav_map.items
        assert epub.ncx.head
        assert epub.ncx.title
        assert epub.ncx.nav_map
        assert repr(epub.ncx)

        epub.ncx.title.text = "New title"
        epub.write(epub_path)

        with EPUB(epub_path) as epub:
            assert epub.ncx
            assert epub.ncx.title.text == "New title"

            __ = epub.ncx.head.uid
            __ = epub.ncx.head.depth
            __ = epub.ncx.head.total_page_count
            __ = epub.ncx.head.max_page_number

            epub.ncx.head.uid = "new-uid"
            epub.ncx.head.depth = 2
            epub.ncx.head.total_page_count = 100
            epub.ncx.head.max_page_number = 50
            new_item = epub.ncx.head.add(name="custom-meta", content="custom value")
            assert new_item

            nav_map = epub.ncx.nav_map
            assert nav_map
            assert nav_map.items

            for item in nav_map.items:
                assert item
                assert item.text
                assert item.href

            item = nav_map.items[0]
            assert item

    def test_reset_ncx(self, epub: EPUB) -> None:
        epub.metadata.title = "Test reset NCX"
        epub.metadata.language = "es-ES"
        __ = epub.reset_ncx()

        assert epub.ncx
        assert epub.ncx.title.text == "Test reset NCX"
        lang_tag = epub.ncx.soup.find("ncx", attrs={"xml:lang": True})
        assert isinstance(lang_tag, Tag)
        assert lang_tag["xml:lang"] == "es-ES"

    def test_reset_ncx_from_non_existant(self, epub: EPUB) -> None:
        assert epub.ncx
        epub.resources.remove(epub.ncx)
        assert not epub.ncx

        epub.metadata.title = "Test reset NCX"
        __ = epub.reset_ncx()

        assert epub.ncx
        assert epub.ncx.title.text == "Test reset NCX"

    def test_nav_map_add_after(self, epub: EPUB) -> None:
        assert epub.ncx
        assert epub.ncx.nav_map

        item = epub.ncx.nav_map.items[0]
        __ = item.add_after_self("Uau", "example.com")
        assert epub.ncx.nav_map.tag.select('content[src$="example.com"]')

    def test_page_list(self, epub: EPUB) -> None:
        assert epub.ncx

        if epub.ncx.soup.select("pageList"):
            assert epub.ncx.page_list

    def test_nav_lists(self, epub: EPUB) -> None:
        assert epub.ncx

        if epub.ncx.soup.select("navList"):
            assert epub.ncx.nav_lists
            for nav_list in epub.ncx.nav_lists:
                assert nav_list.items

    def test_create_nav_map(self, epub: EPUB) -> None:
        assert epub.ncx
        epub.ncx.nav_map.reset([])

        epub.reset_toc()
        old_len = len(epub.ncx.nav_map.items)
        assert len(list(epub.ncx.soup.select("navMap"))) == 1
        assert len(list(epub.ncx.soup.select("docTitle"))) == 1
        assert len(list(epub.ncx.soup.select("pageList"))) <= 1

        epub.reset_toc()
        assert epub.ncx.nav_map.items
        assert len(epub.ncx.nav_map.items) == old_len
        assert epub.ncx.nav_map.tag.name == "navMap"
        assert epub.ncx.nav_map.tag.select("content[src]")

        epub.reset_toc(targets_selector="h1", spine_only=False)
        assert epub.ncx.nav_map
        assert epub.ncx.nav_map.items
        tag = epub.ncx.nav_map.tag.select_one("content[src]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("src")))
        assert len(list(epub.ncx.soup.select("navMap"))) == 1

        epub.reset_toc(targets_selector="h1")
        assert epub.ncx.nav_map
        assert epub.ncx.nav_map.items
        tag = epub.ncx.nav_map.tag.select_one("content[src]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("src")))
        assert len(list(epub.ncx.soup.select("navMap"))) == 1
        assert len(list(epub.ncx.soup.select("docTitle"))) == 1
        assert len(list(epub.ncx.soup.select("pageList"))) <= 1

    def test_create_nav_map_error(self, epub: EPUB) -> None:
        if epub.ncx:
            epub.resources.remove(epub.ncx)

        with pytest.raises(EPUBError):
            epub.reset_toc(reset_ncx=True)  # type: ignore[reportArgumentType]

    def test_reset_page_list(self, epub: EPUB) -> None:
        assert epub.ncx

        if epub.ncx.page_list:
            epub.ncx.page_list.tag.decompose()
            epub.ncx.on_soup_change()

        if epub.nav.page_list:
            epub.nav.page_list.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_page_list()
        assert epub.ncx.page_list
        old_len = len(epub.ncx.page_list.items)

        epub.reset_page_list()
        assert epub.ncx.page_list
        assert epub.ncx.page_list.items
        assert len(epub.ncx.page_list.items) == old_len
        assert epub.ncx.page_list.tag.name == "pageList"
        assert epub.ncx.page_list.tag.select("content[src]")
        href = epub.ncx.page_list.items[0].href
        assert get_fragment(href)

        __, existing_tag = epub.resources.resolve_href(
            href,
            relative_to=epub.ncx.filename,
        )

        assert existing_tag
        existing_id = attr_to_str(existing_tag["id"])

        res = next(epub.resources.filter(ContentDocument))
        new_tag = res.soup.new_tag(
            "p",
            string="3",
            attrs={
                NamespacedAttribute(
                    "epub",
                    "type",
                    "http://www.idpf.org/2007/ops",
                ): "pagebreak",
                "id": existing_id + "2",
            },
        )
        assert res.soup.body
        assert res.soup.body.append(new_tag)

        epub.reset_page_list()
        assert len(epub.ncx.page_list.items) == old_len + 1
        assert all(item.href for item in epub.ncx.page_list.items)
        hrefs = [item.href for item in epub.ncx.page_list.items]
        assert len(hrefs) == len(set(hrefs))

        with pytest.raises(EPUBError):
            epub.create_page_list()

    def test_reset_page_list_error(self, epub: EPUB) -> None:
        if epub.ncx:
            epub.resources.remove(epub.ncx)

        with pytest.raises(EPUBError):
            epub.create_page_list(reset_ncx=True)  # type: ignore[reportArgumentType]

        with pytest.raises(EPUBError):
            epub.reset_page_list(reset_ncx=True)  # type: ignore[reportArgumentType]

    def test_create_nav_list(self, epub: EPUB, epub_path: Path) -> None:
        assert epub.ncx

        nav_list = epub.ncx.add_nav_list(
            TOCEntryData(
                doc.filename,
                label=f"Document {index}",
                id=f"i-{index}",
            )
            for index, doc in enumerate(epub.documents, start=1)
        )
        nav_list.text = "Nav list title"

        epub.write(epub_path)
        epub = EPUB(epub_path)
        assert epub.ncx
        assert epub.ncx.nav_lists
        nav_list = next(nl for nl in epub.ncx.nav_lists if nl.text == "Nav list title")

        assert all(nav_list.items_referencing(doc.filename) for doc in epub.documents)

    def test_add_resource(self, epub: EPUB) -> None:
        doc = ContentDocument(b"<h1>Uau!</h1>", "added-document.xhtml")
        assert epub.ncx

        epub.resources.add(doc)
        assert next(epub.ncx.nav_map.items_referencing(doc.filename))

    def test_add_resource_no_ncx(self, epub: EPUB) -> None:
        doc = ContentDocument(b"content", "added-document.xhtml")

        epub.resources.add(doc, add_to_ncx=False)
        assert epub.ncx
        assert not next(
            epub.ncx.nav_map.items_referencing(doc.filename),
            None,
        )

    def test_add_resource_no_toc(self, epub: EPUB) -> None:
        doc = ContentDocument(b"content", "added-document.xhtml")

        epub.resources.add(doc, add_to_toc=False)
        assert epub.ncx
        assert not next(
            epub.ncx.nav_map.items_referencing(doc.filename),
            None,
        )

    def test_add_resource_error(self, epub: EPUB) -> None:
        doc = ContentDocument(b"content", "added-document.xhtml")

        assert epub.ncx
        epub.resources.remove(epub.ncx)

        with pytest.raises(EPUBError):
            epub.resources.add(doc, add_to_ncx=True)

    def test_remove_resource(self, epub: EPUB) -> None:
        doc = next(
            epub.resources[item.filename]
            for item in epub.nav.toc.items
            if strip_fragment(item.filename) != epub.nav.filename
        )
        img = epub.images[0]

        assert doc
        assert epub.ncx
        __ = epub.ncx.add_nav_list(
            [
                TOCEntryData(doc.filename, doc.get_title()),
                TOCEntryData(img.filename, img.get_title()),
            ]
        )
        assert next(epub.ncx.nav_map.items_referencing(doc.filename))
        assert next(epub.ncx.nav_lists[0].items_referencing(doc.filename))

        epub.resources.remove(doc)

        assert not next(
            epub.ncx.nav_map.items_referencing(doc.filename),
            None,
        )
        assert not next(
            epub.ncx.nav_lists[0].items_referencing(doc.filename),
            None,
        )

    def test_rename_resource(self, epub: EPUB) -> None:
        assert epub.ncx
        resource = epub.resources.resolve_href(
            epub.ncx.nav_map.items[0].href,
            False,
            relative_to=epub.ncx,
        )
        assert resource

        epub.resources.rename(resource, "renamed-document.xhtml")

        assert (
            Path(strip_fragment(epub.ncx.nav_map.items[0].href)).name
            == "renamed-document.xhtml"
        )

    def test_play_order(self, epub: EPUB) -> None:
        assert epub.ncx
        epub.reset_toc()
        __ = epub.reset_ncx()

        assert epub.ncx.nav_map.items[0].play_order == 1
        assert epub.ncx.nav_map.items[1].play_order
        assert epub.ncx.nav_map.items[1].play_order > 1

        order = [tag["playOrder"] for tag in epub.ncx.nav_map.tag.find_all("navPointc")]
        assert order == list(range(1, len(order) + 1))

    def test_insert_in_soup(self, epub: EPUB) -> None:
        soup = NCXSoup("<ncx><head /><docTitle /><navMap /></ncx>", "xml")
        tag = soup.navMap.extract()
        assert epub.ncx

        nav_map = NCXNavMap(soup=soup, tag=tag, own_filename="toc.ncx", parent=epub.ncx)
        nav_map.insert_self_in_soup()
        assert nav_map.tag.parent == soup.ncx

    def test_page_target_type(self) -> None:
        soup = NCXSoup("<ncx><head /><docTitle /><navMap /></ncx>", "xml")
        pt = NCXPageTarget(
            soup=soup,
            filename="any",
            own_filename="toc.ncx",
            text="IV",
            id="pt1",
        )

        assert pt.type == "front"

        pt = NCXPageTarget(
            soup=soup,
            filename="any",
            own_filename="toc.ncx",
            text="32",
            id="pt1",
        )
        assert pt.type == "normal"

        pt = NCXPageTarget(
            soup=soup,
            filename="any",
            own_filename="toc.ncx",
            text="something completely different",
            id="pt1",
        )
        assert pt.type == "special"

    def test_ncx_authors(self, epub: EPUB) -> None:
        __ = epub.metadata.add_dc("creator", "John")
        __ = epub.reset_ncx()
        assert epub.ncx
        authors = list(epub.ncx.authors)
        assert authors
        assert all(author.tag.name == "docAuthor" for author in authors)
        assert all(author.text for author in authors)

        __ = epub.ncx.add_author("New author")
        assert any(author.text == "New author" for author in epub.ncx.authors)

        removed = epub.ncx.remove_author("New author")
        assert removed
        assert all(author.text != "New author" for author in epub.ncx.authors)

        assert epub.ncx.remove_author("New author") is None

    def test_reset_ncx_errors(self, epub: EPUB) -> None:
        if epub.ncx:
            epub.resources.remove(epub.ncx)

        epub.metadata.title = ""

        with pytest.raises(EPUBError):
            __ = epub.reset_ncx()

        epub.metadata.title = "Valid title"
        epub.metadata.language = ""

        ncx = epub.reset_ncx()
        assert "xml:lang" not in ncx.soup.ncx.attrs

        epub.metadata.remove("creator")
        __ = epub.metadata.add_dc("creator", "John")

        __ = ncx.add_author("John")

        ncx = epub.reset_ncx()
        assert (
            len([author.text for author in ncx.authors if author.text == "John"]) == 1
        )

    def test_update_numbers(self, epub: EPUB) -> None:
        ncx = epub.reset_ncx()

        old_depth = ncx.head.depth
        deepest_node = None
        max_depth = 0

        for node in ncx.nav_map.nodes:
            depth = 0
            other = node
            while isinstance(other, (NCXNavPoint, NCXNavMap)):
                depth += 1
                other = other.parent

            if depth > max_depth:
                max_depth = depth
                deepest_node = node

        assert deepest_node
        __ = deepest_node.add("Subitem", "subitemhref")
        ncx.update_numbers()

        assert ncx.head.depth == old_depth + 1

        if ncx.page_list:
            ncx.page_list.tag.decompose()
            ncx.on_soup_change()
        if epub.nav.page_list:
            epub.nav.page_list.tag.decompose()
            epub.nav.on_soup_change()

        assert ncx.page_list is None

        with pytest.raises(EPUBError):
            __ = ncx.sync_page_list(epub.nav)
        ncx.update_total_page_count()
        ncx.update_max_page_number()
        assert ncx.head.total_page_count is None
        assert ncx.head.max_page_number is None

        epub.reset_page_list()

        ncx.content = ncx.content.decode().replace("pageList", "something").encode()
        ncx.update_numbers()
        assert ncx.page_list is None
        assert ncx.head.max_page_number is None

    def test_recursive_toc(self, epub: EPUB) -> None:
        epub.reset_toc()
        item = next(
            item
            for item in epub.nav.toc.nodes
            if isinstance(item, NavItem) and isinstance(item.parent, NavItem)
        )

        assert isinstance(item.parent, NavItem)
        __ = item.add_item(item.parent)

        with pytest.raises(EPUBError):
            assert epub.ncx
            __ = epub.reset_ncx()
