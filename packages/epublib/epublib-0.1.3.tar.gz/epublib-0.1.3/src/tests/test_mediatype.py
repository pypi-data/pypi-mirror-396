import pytest

from epublib.media_type import Category, MediaType


class TestMediaType:
    def test_mediatype(self) -> None:
        mt = MediaType("text/html")
        assert mt.value == "text/html"
        assert str(mt) == "text/html"
        assert mt is MediaType("text/html")
        assert mt is MediaType(mt)
        assert mt != MediaType("text/css")
        assert mt

        mt = MediaType("font/woff2")
        assert mt is MediaType(mt)
        assert mt.category is Category.FONT
        assert mt is MediaType.FONT_WOFF2

        mt = MediaType.from_filename("example.jpg")
        assert mt != ""
        assert mt
        assert mt.value == "image/jpeg"
        assert mt is MediaType("image/jpeg")
        assert mt is MediaType(mt)
        assert mt != MediaType("text/css")
        assert str(mt) == "image/jpeg"

        assert MediaType.from_filename("toc.ncx") is MediaType.NCX

    def test_errors(self) -> None:
        with pytest.raises(ValueError):
            __ = MediaType(3)

        assert MediaType.from_filename("example") is None
