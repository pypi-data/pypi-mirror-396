import typing
from datetime import datetime, timedelta, timezone
from typing import final, override

import pytest
from bs4 import BeautifulSoup

from epublib.exceptions import EPUBError
from epublib.util import (
    ResolutionType,
    attr_to_str,
    datetime_to_str,
    get_absolute_href,
    get_relative_href,
    new_id,
    parse_int,
    slugify,
    strip_type_parameters,
)


@final
class TestUtil:
    def test_datetime_to_str(self) -> None:
        old = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        new = datetime.fromisoformat(datetime_to_str(old))
        assert old.replace(microsecond=0) == new

        old = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
        new = datetime.fromisoformat(datetime_to_str(old))
        assert old.astimezone(timezone.utc).replace(microsecond=0) == new

        dt = datetime.now()
        new = datetime.fromisoformat(datetime_to_str(dt))
        assert dt.astimezone(timezone.utc).replace(microsecond=0) == new

        dt = datetime.now()
        new = datetime.fromisoformat(datetime_to_str(dt))

        assert new.microsecond == 0

    def test_strip_type_parameters(self) -> None:
        assert strip_type_parameters(list[str]) is list
        assert strip_type_parameters(str) is str
        assert strip_type_parameters(typing.Literal["hi", "bye"]) is str  # type: ignore[reportArgumentType]
        assert strip_type_parameters(typing.Literal["hi", 3, 5.4]) == str | int | float  # type: ignore[reportArgumentType]
        assert (
            strip_type_parameters(
                typing.Optional[typing.Literal["front", "normal", "special"]]  # type: ignore[reportArgumentType]
            )
            == str | None
        )

    def test_absolute_relative_hrefs(self) -> None:
        assert (
            get_absolute_href(
                "OEBPS/toc.ncx",
                "chapter1.html",
            )
            == "OEBPS/chapter1.html"
        )
        assert (
            get_absolute_href(
                "OEBPS/toc.ncx",
                "../chapter1.html",
            )
            == "chapter1.html"
        )
        assert (
            get_absolute_href(
                "OEBPS/Text/chapter2.html#fragment",
                "chapter1.html",
            )
            == "OEBPS/Text/chapter1.html"
        )
        assert (
            get_absolute_href(
                "OEBPS/Text/chapter2.html#fragment",
                "../../chapter1.html",
            )
            == "chapter1.html"
        )
        assert (
            get_absolute_href(
                "toc.ncx",
                "chapter1.html",
            )
            == "chapter1.html"
        )
        assert (
            get_absolute_href(
                "/absolute/path/toc.ncx",
                "chapter1.html",
            )
            == "/absolute/path/chapter1.html"
        )
        assert (
            get_absolute_href(
                "OEBPS/toc.ncx",
                "#section1",
            )
            == "OEBPS/toc.ncx#section1"
        )
        assert (
            get_absolute_href(
                "OEBPS/Text/chapter2.html",
                "#section1",
            )
            == "OEBPS/Text/chapter2.html#section1"
        )

        assert (
            get_relative_href(
                "OEBPS/toc.ncx",
                "OEBPS/chapter1.html",
            )
            == "chapter1.html"
        )
        assert (
            get_relative_href(
                "OEBPS/toc.ncx",
                "chapter1.html",
            )
            == "../chapter1.html"
        )
        assert (
            get_relative_href(
                "OEBPS/Text/chapter2.html",
                "OEBPS/Text/chapter1.html",
            )
            == "chapter1.html"
        )
        assert (
            get_relative_href(
                "OEBPS/Text/chapter2.html",
                "chapter1.html",
            )
            == "../../chapter1.html"
        )
        assert (
            get_relative_href(
                "toc.ncx#fragment",
                "chapter1.html",
            )
            == "chapter1.html"
        )
        assert (
            get_relative_href(
                "/absolute/path/toc.ncx",
                "/absolute/path/chapter1.html",
            )
            == "chapter1.html"
        )
        assert (
            get_relative_href(
                "/other/path/toc.ncx#other-fragment",
                "/absolute/path/chapter1.html",
            )
            == "../../absolute/path/chapter1.html"
        )
        assert (
            get_relative_href(
                "OEBPS/toc.ncx",
                "OEBPS/toc.ncx#section1",
            )
            == "#section1"
        )
        assert (
            get_relative_href(
                "OEBPS/Text/chapter2.html",
                "OEBPS/Text/chapter2.html#section1",
            )
            == "#section1"
        )
        assert (
            get_relative_href(
                "OEBPS/Text/chapter2.html",
                "OEBPS/Text/chapter2.html",
            )
            == "#"
        )
        assert (
            get_relative_href(
                "OEBPS/Text/chapter2.html#other-fragment",
                "OEBPS/Text/chapter2.html",
            )
            == "#"
        )

    def test_parse_int(self) -> None:
        assert parse_int("42") == 42
        assert parse_int("not a number") is None
        assert parse_int(None) is None
        assert parse_int("3.14") == 3
        assert parse_int("-7 zlkdsf z 8") == -78
        assert parse_int("xxx0xxx") == 0

    def test_slugify(self) -> None:
        assert slugify("Hello, World!") == "hello-world"
        assert (
            slugify("  Leading and trailing spaces  ") == "leading-and-trailing-spaces"
        )
        assert slugify("Special & Characters *%$#@!") == "special-characters"
        assert slugify("") == ""
        assert slugify("     ") == ""
        assert slugify("123 Numbers 456") == "123-numbers-456"
        assert slugify("Mixed CASE Letters") == "mixed-case-letters"

    def test_attr_to_str(self) -> None:
        soup = BeautifulSoup(
            '<div id="test" data-value="123" class="hi hello"></div>',
            "lxml",
        )

        tag = soup.find("div")
        assert tag

        assert attr_to_str(tag["id"]) == "test"
        assert attr_to_str(tag.get("data-value")) == "123"
        assert attr_to_str(tag.get("non-existent")) is None
        assert tag["class"] == ["hi", "hello"]
        assert attr_to_str(tag["class"]) == "hi hello"
        assert attr_to_str(tag["class"], ResolutionType.FIRST) == "hi"

    def test_new_id(self) -> None:
        gone: set[str] = set()
        for _ in range(1, 10):
            new = "item"
            previous = gone.copy()
            n = new_id(new, gone)
            assert n in gone
            assert n not in previous

        class EverythingSet(set[str]):
            @override
            def __contains__(self, o: object, /) -> bool:
                return True

        gone = EverythingSet()
        with pytest.raises(EPUBError):
            __ = new_id("item", gone)
