import tempfile
from pathlib import Path

import bs4
import pytest

from epublib.exceptions import EPUBError
from epublib.media_type import Category, MediaType
from epublib.resources import PublicationResource, Resource, XMLResource

from . import samples


class TestResources:
    def test_from_file(self) -> None:
        resources = Resource.from_path(samples.image, samples.image.name)

        assert resources.filename == samples.image.name
        assert resources.content == samples.image.read_bytes()

        resources.content = b"changed"

        assert resources.content == resources.get_content()

    def test_xml_resources(self) -> None:
        resource = XMLResource.from_path(samples.page, "page.xhtml")

        assert resource.get_title()
        assert resource.soup.find("html") is not None
        assert b"<html" in resource.content

        resource.soup = bs4.BeautifulSoup("<html><sometag /></html>", "xml")
        assert resource.soup.find("sometag") is not None

        resource.content = b"<html><othertag /></html>"
        assert resource.soup.find("othertag") is not None

    def test_publication_resource(self) -> None:
        resource = PublicationResource.from_path(samples.image, "image.jpg")
        assert resource.media_type == "image/jpeg"
        assert resource.category is Category.IMAGE
        assert not resource.is_foreign

        resource = PublicationResource.from_path(
            samples.image,
            "image.jpg",
            MediaType("image/other"),
        )
        assert resource.media_type == "image/other"
        assert resource.category is Category.FOREIGN
        assert resource.is_foreign

        raw = Resource.from_path(samples.image, samples.image.name)
        resource = PublicationResource.from_resource(raw)
        assert resource.media_type == "image/jpeg"

        raw.close()
        with pytest.raises(EPUBError):
            __ = PublicationResource.from_resource(raw)

    def test_publication_resource_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "file.unknown"
            tmp_path.touch()

            with pytest.raises(EPUBError):
                _ = PublicationResource.from_path(tmp_path, "file.unknown")
