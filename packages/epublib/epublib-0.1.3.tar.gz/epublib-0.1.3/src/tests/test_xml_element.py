from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Annotated, ClassVar, final, override

import bs4
import pytest

from epublib.exceptions import EPUBError
from epublib.nav import NavItem
from epublib.xml_element import (
    HrefElement,
    HrefRecursiveElement,
    SyncType,
    XMLAttribute,
    XMLElement,
    XMLParent,
)


@dataclass(kw_only=True)
class ParagraphElement(XMLElement):
    id: Annotated[str, XMLAttribute()]
    cls: Annotated[list[str] | None, XMLAttribute("class")]

    tag_name: ClassVar[str] = "p"

    @property
    def pk(self) -> str:
        return self.id


class ParagraphParent(XMLParent[ParagraphElement]):
    @override
    def parse_items(self) -> list[ParagraphElement]:
        return [
            ParagraphElement(
                id=f"id{i}", cls=[f"xpto{i}", f"class-{i}"], soup=self.soup
            )
            for i in range(5)
        ]


@dataclass(kw_only=True)
class Href(HrefElement):
    tag_name: ClassVar[str] = "a"


class NoTagNameXMLElement(XMLElement):
    pass


@dataclass(kw_only=True)
class RecursiveHref(HrefRecursiveElement["RecursiveHref"]):
    tag_name: ClassVar[str] = "div"
    href: Annotated[str, XMLAttribute(get="a", create="a")] = ""

    @override
    def create_parent_tag(self) -> bs4.Tag:
        return self.tag

    @property
    @override
    def parent_tag(self) -> bs4.Tag | None:
        return self.tag

    @override
    def parse_items(self) -> Sequence["RecursiveHref"]:
        return [
            self.__class__.from_tag(self.soup, tag, self.own_filename)
            for tag in self.tag.find_all("div", recursive=False)
        ]


@final
class TestXMLElement:
    def test_xml_element(self) -> None:
        soup = bs4.BeautifulSoup("", "xml")
        p = ParagraphElement(soup=soup, id="param1", cls=["text", "bold"])
        __ = list(
            isinstance("anything", attribute.typ)
            for attribute in p._get_attributes().values()  # type: ignore[reportPrivateUsage]
        )
        assert p.tag
        assert p.tag["class"] == "text bold"
        assert p.tag["id"] == "param1"

    def test_xml_element_from_tag(self) -> None:
        soup = bs4.BeautifulSoup('<p id="param1" class="text bold"/>', "xml")
        tag = soup.select_one("p")
        assert tag is not None
        p = ParagraphElement.from_tag(soup, tag)
        assert p.tag is tag
        assert p.cls == ["text", "bold"]
        assert p.id == "param1"

    def test_xml_parent(self) -> None:
        soup = bs4.BeautifulSoup("", "xml")
        tag = soup.new_tag("div")

        parent = ParagraphParent(soup=soup, tag=tag)
        assert parent.tag is tag
        assert parent.items
        assert parent.parent_tag is tag
        assert parent.create_parent_tag() is tag

        assert all(isinstance(item, ParagraphElement) for item in parent.items)
        for item in parent.items:
            assert item is parent[item.pk]

        new_item = parent.add_item(
            ParagraphElement(id="id100", cls=["new", "item"], soup=soup)
        )
        assert new_item in parent.items

        removed = parent.items[1]
        parent.remove_item(removed)
        assert parent.get(removed.pk) is None

    def test_recursive(self) -> None:
        html = """
        <div id="master">
            <div id="line1">
              <div id="cell1.1"></div>
              <div id="cell1.2"></div>
              <div id="cell1.3"></div>
            </div>
            <div id="line2">
              <div id="cell2.1"></div>
              <div id="cell2.2"></div>
              <div id="cell2.3"></div>
            </div>
            <div id="line3">
              <div id="cell3.1"></div>
              <div id="cell3.2"></div>
              <div id="cell3.3"></div>
            </div>
        </div>
        """

        soup = bs4.BeautifulSoup(html, "xml")
        master = soup.div
        assert master

        parent = RecursiveHref.from_tag(
            soup=soup,
            tag=master,
            own_filename="base/toc.xhtml",
        )
        assert len(parent.items) == 3
        assert all(len(item.items) == 3 for item in parent.items)

    def test_href_element(self) -> None:
        soup = bs4.BeautifulSoup('<a href="text.xhtml">Some text</a>', "xml")
        tag = soup.a
        assert tag is not None
        href = Href.from_tag(soup, tag, own_filename="base/toc.xhtml")
        assert href.tag is tag
        assert href.pk == href.filename
        assert href.href == "text.xhtml"
        assert href.filename == "base/text.xhtml"

    def test_recursive_href_parent(self) -> None:
        html = """
        <div id="master">
          <a href="text.xhtml">text</a>
          <div id="line1">
            <a href="text.xhtml">text</a>
            <div id="cell1.1"><a href="text.xhtml">text</a></div>
          </div>
          <div id="line2">
            <a href="text.xhtml">text</a>
          </div>
          <div id="line3">
            <a href="text.xhtml">text</a>
          </div>
        </div>
        """

        soup = bs4.BeautifulSoup(html, "xml")
        master = soup.div
        assert master

        root = RecursiveHref.from_tag(soup, master, own_filename="base/toc.xhtml")
        assert len(root.items) == 3
        assert root.href
        assert all(item.href for item in root.items)

    def test_recursive_href_parent_create(self) -> None:
        soup = bs4.BeautifulSoup("", "xml")
        parent = RecursiveHref(
            soup=soup,
            filename="base/index.xhtml",
            own_filename="base/toc.xhtml",
        )
        __ = parent.add_item(
            RecursiveHref(
                filename="child1",
                own_filename=parent.own_filename,
                soup=soup,
            )
        )
        __ = parent.add_item(
            RecursiveHref(
                filename="child2",
                own_filename=parent.own_filename,
                soup=soup,
            )
        )
        item = parent.add_item(
            RecursiveHref(
                filename="child3",
                own_filename=parent.own_filename,
                soup=soup,
            )
        )

        __ = item.add_item(
            RecursiveHref(
                filename="grandchild1",
                own_filename=parent.own_filename,
                soup=soup,
            )
        )
        __ = item.add_item(
            RecursiveHref(
                filename="grandchild2",
                own_filename=parent.own_filename,
                soup=soup,
            )
        )
        __ = item.add_item(
            RecursiveHref(
                filename="grandchild3",
                own_filename=parent.own_filename,
                soup=soup,
            )
        )

        assert parent.parent_tag
        assert len(list(parent.parent_tag.select("& > div"))) == 3
        assert len(list(parent.items[2].tag.select("div"))) == 3

    def test_nav_item_from_tag(self) -> None:
        html = """
        <div>
          <a href="text.xhtml">Some text</a>
        </div>
        """
        soup = bs4.BeautifulSoup(html, "xml")
        tag = soup.div
        assert tag
        item = NavItem.from_tag(soup, tag, own_filename="base/toc.xhtml")
        assert item.text
        assert item.href
        assert not item.tag.get("href")

    def test_no_tag_name(self) -> None:
        with pytest.raises(NotImplementedError):
            __ = NoTagNameXMLElement(soup=bs4.BeautifulSoup("", "xml"))

    def test_xml_attribute(self) -> None:
        html = """
        <div></div>
        """
        soup = bs4.BeautifulSoup(html, "xml")
        tag = soup.div
        assert tag

        attr = XMLAttribute("hi")
        assert attr.get_tag(tag) is tag
        assert attr.create_tag(soup, tag) is tag

        attr = XMLAttribute("hi", get="a", create="a")

        a = attr.get_tag(tag)
        assert a is None
        a = attr.create_tag(soup, tag)
        assert a
        assert a.name == "a"
        assert a.parent is tag

        @dataclass(kw_only=True)
        class Element(XMLElement):
            tag_name: ClassVar[str] = "div"
            string_attr: Annotated[
                str | None,
                XMLAttribute(sync=SyncType.STRING, get="span", create="span"),
            ]
            name_attr: Annotated[str, XMLAttribute(sync=SyncType.NAME)]
            dt_attr: Annotated[datetime, XMLAttribute()] = field(
                default_factory=datetime.now
            )

        element = Element(soup=soup, string_attr="value", name_attr="value2")

        element.name_attr = "changed"
        assert element.tag.name == "changed"
        with pytest.raises(EPUBError):
            element.name_attr = ""

        element.string_attr = "changed"
        span = element.tag.find("span")
        assert span
        assert span.get_text() == "changed"

        element.string_attr = None
        assert element.tag.find("span") is None

        element.dt_attr = datetime(1994, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        assert "1994" in element.tag["dt-attr"]

        element = Element.from_tag(soup, element.tag)
        assert element.dt_attr == datetime(1994, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    def test_no_child(self) -> None:
        class NoChild(XMLParent):  # type: ignore[reportMissingTypeArgument]
            pass

        with pytest.raises(NotImplementedError):
            __ = NoChild(soup=bs4.BeautifulSoup("", "xml"))
