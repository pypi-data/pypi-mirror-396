import re
from itertools import permutations
from pathlib import Path
from typing import final

import bs4
import pytest
from bs4.element import NamespacedAttribute

from epublib import EPUB
from epublib.exceptions import EPUBError, EPUBWarning
from epublib.nav import NavItem
from epublib.nav.util import detect_page
from epublib.resources import ContentDocument
from epublib.util import get_fragment


@final
class TestEPUBNav:
    def test_nav(self, epub: EPUB) -> None:
        assert epub.manifest.nav
        assert repr(epub.nav)

    def test_toc(self, tmp_path: Path, epub: EPUB) -> None:
        toc = epub.nav.toc
        assert toc.title
        assert toc.text == toc.title
        assert toc.items
        assert toc.tag.get("epub:type") == "toc"
        for item in toc.items:
            assert item
            assert item.text
            assert item.href
            assert item in toc.nodes

        item = toc.items[0]

        toc.title = "testtoctitle"
        item.href = "testhref"
        item.text = "test text"

        assert item.tag.get("href") is None
        item = toc.insert(1, "New item", "newitemhref")
        assert item.tag.select("& > a[href]")

        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)
        epub = EPUB(outfn)

        toc = epub.nav.toc
        assert toc.title == "testtoctitle"
        item = toc.items[0]
        assert item.href == "testhref"

        assert all(not (item.tag.a and item.tag.span) for item in toc.items)

        epub.nav.toc.tag.decompose()
        epub.nav.on_soup_change()

        with pytest.raises(EPUBError):
            __ = epub.nav.toc

        epub.reset_toc()
        assert epub.nav.toc

        epub.nav.toc.title = "XXX"
        epub.nav.content = epub.nav.content.decode().replace("XXX", "YYY").encode()
        assert epub.nav.toc.title == "YYY"

    def test_toc_add_after(self, epub: EPUB) -> None:
        item = epub.nav.toc.items[0]
        __ = item.add_after_self("Uau", "example.com")
        assert epub.nav.toc.items[1].text == "Uau"
        assert epub.nav.toc.items[1].filename == "example.com"
        assert epub.nav.toc.tag.select('[href$="example.com"]')

    def test_page_list(self, epub: EPUB) -> None:
        if epub.nav.soup.select("[epub|type='page-list']"):
            pl = epub.nav.toc
            assert pl

    def test_landmarks(self, epub: EPUB) -> None:
        if epub.nav.soup.select("[epub|type='landmarks']"):
            pl = epub.nav.toc
            assert pl
            assert pl.items
            assert pl.items[0].href

    def test_reset_page_list(self, epub: EPUB) -> None:
        if epub.nav.page_list:
            epub.nav.page_list.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_page_list()
        assert epub.nav.page_list
        old_len = len(epub.nav.page_list.items)

        epub.reset_page_list()
        assert epub.nav.page_list
        assert epub.nav.page_list.items
        assert len(epub.nav.page_list.items) == old_len
        assert epub.nav.page_list.tag.get("epub:type") == "page-list"
        assert epub.nav.page_list.tag.select("[href]")

        _, existing = epub.resources.resolve_href(
            epub.nav.page_list.items[0].href or "",
            relative_to=epub.nav.filename,
        )
        assert existing
        existing_id = str(existing["id"])

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
                "id": existing_id,
            },
        )
        assert res.soup.body
        assert res.soup.body.append(new_tag)

        epub.reset_page_list()
        assert len(epub.nav.page_list.items) == old_len + 1
        ids = [
            re.sub(r".*#(\w)$", "$1", item.href or "")
            for item in epub.nav.page_list.items
        ]
        assert len(ids) == len(set(ids))

        with pytest.raises(EPUBError):
            epub.create_page_list()

    def test_reset_toc_flat(self, epub: EPUB) -> None:
        epub.nav.toc.reset([])

        epub.reset_toc(targets_selector=None)
        old_len = len(epub.nav.toc.items)

        epub.reset_toc(targets_selector=None)
        assert epub.nav.toc.items
        assert len(epub.nav.toc.items) == old_len
        assert epub.nav.toc.tag.get("epub:type") == "toc"
        assert epub.nav.toc.tag.select("[href]")

        epub.reset_toc(targets_selector="h1", spine_only=False)
        assert epub.nav.toc.items
        assert epub.nav.toc.tag.get("epub:type") == "toc"
        tag = epub.nav.toc.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))

        epub.reset_toc(targets_selector="h1")
        assert epub.nav.toc.items
        assert epub.nav.toc.tag.get("epub:type") == "toc"
        tag = epub.nav.toc.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))

        doc = next(doc for doc in epub.documents if doc is not epub.nav)
        h2 = doc.soup.new_tag("h2", id="newh2")
        h2.string = "aham!"
        h3 = doc.soup.new_tag("h3", id="newh3")
        h3.string = "\t  \n"

        assert doc.soup.body
        __ = doc.soup.body.insert(0, h2)
        __ = h2.insert_after(h3)

        # including a will trigger a flat TOC
        epub.reset_toc(targets_selector="a, h1, h2")
        assert any(get_fragment(item.href) == "newh2" for item in epub.nav.toc.items)
        assert all(get_fragment(item.href) != "newh3" for item in epub.nav.toc.items)

    def test_reset_toc_h1(self, epub: EPUB) -> None:
        epub.reset_toc()
        assert epub.nav.soup.h1

    def test_create_nested_toc(self, epub: EPUB) -> None:
        epub.reset_toc()

        assert any(item.items for item in epub.nav.toc.items)

        doc = next(doc for doc in epub.documents if doc is not epub.nav)
        h2 = doc.soup.new_tag("h2", id="newh2")
        h2.string = "aham!"
        assert doc.soup.body
        __ = doc.soup.body.append(h2)

        for item in epub.nav.toc.items:
            res, tag = epub.resources.resolve_href(item.filename)
            if "#" in item.filename:
                assert tag, item.filename
            assert res

        epub.reset_toc()
        previous_len = len(epub.nav.toc.items)

        h3 = doc.soup.new_tag("h3", id="newh3")
        __ = h2.insert_after(h3)
        epub.reset_toc()
        assert len(epub.nav.toc.items) == previous_len

    def test_reset_toc_with_title(self, epub: EPUB) -> None:
        title = "My TOC Title"
        epub.reset_toc(title=title)
        assert epub.nav.toc.title == "My TOC Title"

        epub.reset_toc()
        assert epub.nav.toc.title == "My TOC Title"

        epub.reset_toc(title="Another TOC Title")
        assert epub.nav.toc.title == "Another TOC Title"

        epub.nav.toc.title = "\n"
        with pytest.raises(EPUBError):
            epub.reset_landmarks()

    def test_remove_nav_error(self, epub: EPUB) -> None:
        with pytest.raises(EPUBError):
            epub.resources.remove(epub.nav)

    def test_create_landmarks(self, epub: EPUB) -> None:
        if epub.nav.landmarks:
            epub.nav.landmarks.tag.decompose()
            epub.nav.on_soup_change()

        epub.create_landmarks()
        assert epub.nav.landmarks
        old_len = len(epub.nav.landmarks.items)

        epub.reset_landmarks()
        assert epub.nav.landmarks
        assert epub.nav.landmarks.items
        assert len(epub.nav.landmarks.items) == old_len
        assert epub.nav.landmarks.tag.get("epub:type") == "landmarks"
        assert epub.nav.landmarks.tag.select("[href]")

        del epub.nav.toc.tag["id"]

        assert all(
            item.tag.a and item.tag.a.attrs.get("epub:type")
            for item in epub.nav.landmarks.items
        )

        epub.reset_landmarks(targets_selector="h1")
        assert epub.nav.landmarks
        assert epub.nav.landmarks.items
        assert epub.nav.landmarks.tag.get("epub:type") == "landmarks"
        tag = epub.nav.landmarks.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))
        assert all(
            item.tag.a and item.tag.a.attrs.get("epub:type")
            for item in epub.nav.landmarks.items
        )

        epub.reset_landmarks(targets_selector="h1")
        assert epub.nav.landmarks
        assert epub.nav.landmarks.items
        assert epub.nav.landmarks.tag.get("epub:type") == "landmarks"
        tag = epub.nav.landmarks.tag.select_one("[href]")
        assert tag
        assert re.search(r"#\S+", str(tag.get("href")))
        hrefs = [item.href for item in epub.nav.landmarks.items]
        assert len(set(hrefs)) == len(hrefs)
        assert all(
            item.tag.a and item.tag.a.attrs.get("epub:type")
            for item in epub.nav.landmarks.items
        )

        doc = epub.documents[0]
        assert doc.soup.body
        tag = doc.soup.new_tag("h1", id="newh1")
        __ = doc.soup.body.append(tag)

        epub.reset_landmarks(targets_selector="h1#newh1")
        assert all(
            get_fragment(item.href) != "newh1" for item in epub.nav.landmarks.items
        )
        tag.string = "hi"
        epub.reset_landmarks(targets_selector="h1#newh1")
        assert any(
            get_fragment(item.href) == "newh1" for item in epub.nav.landmarks.items
        )

    def test_create_landmarks_error(self, epub: EPUB) -> None:
        with pytest.raises(EPUBError):
            epub.create_landmarks()

    def test_items_referencing(self, epub: EPUB) -> None:
        epub.reset_toc(include_filenames=True)

        assert list(epub.nav.toc.items_referencing("nonexisting")) == []
        assert all(
            list(item.items_referencing(item.filename)) for item in epub.nav.toc.items
        )

        assert all(
            list(epub.nav.toc.items_referencing(doc.filename)) for doc in epub.documents
        )

        epub.reset_toc(targets_selector="never")
        assert len(epub.nav.toc.items) == 0

        __ = epub.nav.toc.add("Self referential link", href="#some-id")
        assert list(
            epub.nav.toc.items_referencing(epub.nav.filename, ignore_fragment=True)
        )

        assert list(
            epub.nav.toc.items_referencing(
                f"{epub.nav.filename}#some-id",
                ignore_fragment=False,
            )
        )
        assert not list(
            epub.nav.toc.items_referencing(
                f"{epub.nav.filename}#some-other",
                ignore_fragment=False,
            )
        )

    def test_on_soup_change(self, epub: EPUB) -> None:
        assert epub.nav.toc.items

        epub.reset_toc()
        epub.nav.on_soup_change()

        assert epub.nav.toc.items

    @pytest.mark.parametrize("ignore_fragments", [True, False])
    def test_remove_nodes(self, ignore_fragments: bool) -> None:
        root = NavItem(
            soup=bs4.BeautifulSoup("", "lxml"),
            own_filename="nav.xhtml",
            text="TOC",
        )

        item1 = root.add("Item 1", "item1.xhtml")
        _item2 = root.add("Item 2", "item2.xhtml")
        _item3 = root.add("Item 3", "item3.xhtml")

        subitem11 = item1.add("Subitem 1", "item1.xhtml#frag1")
        subitem12 = item1.add("Subitem 2", "item1.xhtml#frag2")
        subitem13 = item1.add("Subitem 3", "item2.xhtml")

        assert len(list(root.nodes)) == 7
        root.remove_nodes("item1.xhtml", ignore_fragments=ignore_fragments)

        assert item1 not in root.nodes
        assert subitem13 in root.items

        if ignore_fragments:
            assert len(root.items) == 3
            assert subitem11 not in root.nodes
            assert subitem12 not in root.nodes
        else:
            assert len(root.items) == 5
            assert subitem11 in root.nodes
            assert subitem12 in root.nodes

    def test_add_item_after_self_error(self) -> None:
        root = NavItem(
            soup=bs4.BeautifulSoup("", "lxml"),
            own_filename="nav.xhtml",
            text="TOC",
        )
        item = root.add("Item 1", "item1.xhtml")

        with pytest.raises(EPUBError):
            __ = root.add_item_after_self(item)
        root.parent = item

        with pytest.raises(EPUBError):
            __ = root.add_item_after_self(item)

    def test_nav_item_remove_href(self) -> None:
        item = NavItem(
            soup=bs4.BeautifulSoup("", "lxml"),
            own_filename="nav.xhtml",
            text="TOC",
        )

        assert item.tag.find("span", recursive=False)
        assert not item.tag.find("a", recursive=False)

        item.filename = "hi"
        assert not item.tag.find("span", recursive=False)
        assert item.tag.find("a", recursive=False)

        item.filename = ""
        assert item.tag.find("span", recursive=False)
        assert not item.tag.find("a", recursive=False)

        item.href = "there"
        assert not item.tag.find("span", recursive=False)
        assert item.tag.find("a", recursive=False)

        item.href = ""
        assert item.tag.find("span", recursive=False)
        assert not item.tag.find("a", recursive=False)

    def destroy_nav_roots(self, epub: EPUB) -> None:
        if epub.nav.landmarks:
            __ = epub.nav.landmarks.tag.extract()

        if epub.nav.page_list:
            __ = epub.nav.page_list.tag.extract()

        __ = epub.nav.toc.tag.extract()

        epub.nav.on_soup_change()

    def test_insert_in_soup(self, epub: EPUB) -> None:
        epub.reset_landmarks()
        epub.reset_page_list()
        assert epub.nav.landmarks
        assert epub.nav.page_list

        for i in range(3):
            if i == 1:
                assert epub.nav.soup.body
                main = epub.nav.soup.body.wrap(epub.nav.soup.new_tag("main"))
                __ = main.wrap(epub.nav.soup.body)

            elif i == 2:
                assert epub.nav.soup.main
                assert epub.nav.soup.body
                __ = epub.nav.soup.main.unwrap()
                __ = epub.nav.soup.body.unwrap()

            for f, g, h in permutations(
                [
                    epub.nav.landmarks.insert_self_in_soup,
                    epub.nav.page_list.insert_self_in_soup,
                    epub.nav.toc.insert_self_in_soup,
                ]
            ):
                self.destroy_nav_roots(epub)
                f()
                g()
                h()

                assert (
                    epub.nav.toc.tag in epub.nav.page_list.tag.find_previous_siblings()
                )
                assert (
                    epub.nav.page_list.tag
                    in epub.nav.landmarks.tag.find_previous_siblings()
                )

    def test_detect_page(self) -> None:
        tag = bs4.BeautifulSoup("<div>3</div>", "xml").div
        assert tag
        assert detect_page(tag) == "3"

        tag = bs4.BeautifulSoup('<div title="4"></div>', "xml").div
        assert tag
        assert detect_page(tag) == "4"

        tag = bs4.BeautifulSoup('<div aria-label="53"></div>', "xml").div
        assert tag
        assert detect_page(tag) == "53"

        tag = bs4.BeautifulSoup("<div>XIV</div>", "xml").div
        assert tag
        assert detect_page(tag) == "XIV"

        tag = bs4.BeautifulSoup("<div></div>", "xml").div
        assert tag

        with pytest.warns(EPUBWarning):
            page = detect_page(tag)

        assert page is None
