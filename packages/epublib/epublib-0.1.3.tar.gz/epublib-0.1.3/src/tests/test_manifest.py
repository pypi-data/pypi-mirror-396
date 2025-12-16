import zipfile
from pathlib import Path
from tempfile import TemporaryFile

import bs4
import pytest

from epublib import EPUB
from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.media_type import Category, MediaType
from epublib.package.manifest import ManifestItem
from epublib.resources import ContentDocument, PublicationResource
from epublib.resources.create import create_resource, create_resource_from_path
from epublib.util import attr_to_str
from tests import samples


class TestEPUBManifest:
    def test_manifest(self, epub: EPUB) -> None:
        assert epub.manifest
        assert repr(epub.manifest)

    @pytest.mark.parametrize("i", range(5))
    def test_manifest_get_item(self, epub: EPUB, i: int) -> None:
        resources = list(epub.resources.filter(PublicationResource))
        resource = resources[i]
        manifest_item = epub.manifest.get(resource)
        assert manifest_item
        assert manifest_item is epub.manifest.get(resource.filename)
        assert manifest_item.media_type
        assert manifest_item.media_type == str(resource.media_type)

    @pytest.mark.parametrize("i", range(5))
    def test_change_manifest_reference(self, epub: EPUB, i: int) -> None:
        manifest_item = epub.manifest.items[i]
        absolute = Path(manifest_item.filename)
        relative = Path(manifest_item.href)

        new_absolute = absolute.parent / "test" / "xpto" / "newname.txt"
        new_relative = relative.parent / "test" / "xpto" / "newname.txt"

        manifest_item.filename = str(new_absolute)
        assert manifest_item.href == str(new_relative)

    def test_manifest_properties(self, epub: EPUB) -> None:
        for item in epub.manifest.items:
            item.properties = None
            item.add_property("custom")

        assert all(
            item.properties and "custom" in item.properties
            for item in epub.manifest.items
        )
        assert all(
            "custom" in attr_to_str(item.tag["properties"]).split()
            for item in epub.manifest.items
        )

        assert all(item.has_property("custom") for item in epub.manifest.items)

        for item in epub.manifest.items:
            item.add_property("custom")

        assert all(
            item.properties is not None and len(item.properties) == 1
            for item in epub.manifest.items
        )

        for item in epub.manifest.items:
            item.remove_property("custom")

        assert all(item.properties is None for item in epub.manifest.items)
        assert all(
            "custom" not in str(item.tag.get("properties")).split()
            for item in epub.manifest.items
        )

    def test_update_manifest_properties(self, epub: EPUB) -> None:
        for item in epub.manifest.items:
            item.properties = None

        doc = epub.documents[0]
        assert doc.soup.body
        __ = doc.soup.body.append(doc.soup.new_tag("math"))

        doc = epub.documents[1]
        assert doc.soup.body
        __ = doc.soup.body.append(doc.soup.new_tag("a", href="https://google.com"))

        doc = epub.documents[2]
        assert doc.soup.body
        __ = doc.soup.body.append(doc.soup.new_tag("epub:switch"))

        doc = epub.documents[3]
        assert doc.soup.body
        __ = doc.soup.body.append(doc.soup.new_tag("script", src="script.js"))

        epub.update_manifest_properties()
        assert any(item.properties for item in epub.manifest.items)
        assert all(item.properties != [] for item in epub.manifest.items)
        assert any(item.has_property("mathml") for item in epub.manifest.items)
        assert any(
            item.has_property("remote-resources") for item in epub.manifest.items
        )
        assert any(item.has_property("scripted") for item in epub.manifest.items)
        assert any(item.has_property("switch") for item in epub.manifest.items)

    def test_create_manifest_item(self) -> None:
        item = ManifestItem(
            soup=bs4.BeautifulSoup("<manifest></manifest>", "xml"),
            filename="Text/nav.xhtml",
            id=EPUBId("nav"),
            media_type=MediaType.XHTML.value,
            properties=["nav"],
            own_filename="content.opf",
        )

        assert item.tag.get("href")

    def test_create_manifest_item_from_epub(self, epub: EPUB) -> None:
        path = Path("OEBPS", "Images", "image2-xxx.jpg")

        __ = epub.manifest.add_item(
            ManifestItem(
                soup=epub.package_document.soup,
                filename=str(path),
                id=EPUBId(path.name.replace(".", "")),
                media_type=str(MediaType.IMAGE_JPEG),
                own_filename=epub.manifest.own_filename,
            )
        )

        assert epub.package_document.soup.manifest.select('[href$="image2-xxx.jpg"]')
        assert not epub.package_document.soup.manifest.select("[manifest-filename]")

    def test_create_manifest_item_for_existing_file(self, epub: EPUB) -> None:
        filename = Path("OEBPS", "Images", "image2-xxx.jpg")
        with TemporaryFile() as f:
            epub.write(f)
            __ = f.seek(0)

            with zipfile.ZipFile(f, "a") as zf:
                zf.write(samples.image, filename)

            __ = f.seek(0)

            epub = EPUB(f)
            resource = epub.resources.get(filename)
            assert resource
            assert not epub.manifest.get(str(filename))

            resource, manifest_item = epub.resources.add_to_manifest(resource)
            assert resource
            assert manifest_item

            assert epub.manifest.get(str(filename))

            resource = epub.resources.get(filename)
            assert isinstance(resource, PublicationResource)

    def test_properties_of_created(self, epub: EPUB) -> None:
        res1 = create_resource_from_path(samples.image)
        res2 = create_resource(b"p { color: red; }", "styles.css")

        epub.resources.add(res1, is_cover=True)
        epub.resources.add(res2)

        item1 = epub.manifest.get(res1)
        item2 = epub.manifest.get(res2)

        for item in (item1, item2):
            assert item and (item.properties is None or item.properties)

    def test_duplicate_id_filename_check(self, epub: EPUB) -> None:
        item = epub.manifest.items[0]

        with pytest.raises(EPUBError):
            __ = epub.manifest.add_item(item)

        with pytest.raises(EPUBError):
            __ = epub.manifest.add_item(
                ManifestItem(
                    soup=item.soup,
                    filename=item.filename,
                    id=item.id,
                    media_type="text/plain",
                    own_filename=epub.package_document.filename,
                )
            )

        with pytest.raises(EPUBError):
            __ = epub.manifest.add_item(
                ManifestItem(
                    soup=item.soup,
                    filename=item.filename,
                    id=EPUBId("some-id"),
                    media_type="text/plain",
                    own_filename=epub.package_document.filename,
                )
            )
        with pytest.raises(EPUBError):
            __ = epub.resources.add(ContentDocument(b"aham", item.filename))

        with pytest.raises(EPUBError):
            __ = epub.resources.add(
                ContentDocument(b"aham", "text.xhtml"),
                identifier=item.id,
            )

    def test_rename_id(self, epub: EPUB) -> None:
        item = epub.manifest.items[0]
        old_id = item.id
        new_id = EPUBId("new-id")
        epub.rename_id(item, new_id)

        assert item.id == new_id
        assert old_id != new_id
        assert not epub.package_document.soup.select(f'[id="{old_id}"]')
        assert epub.package_document.soup.select(f'[id="{new_id}"]')

        ncx = epub.reset_ncx()
        epub.rename_id(ncx, EPUBId("new-id-ncx"))
        assert epub.spine.tag["toc"] == "new-id-ncx"

        spine_item = epub.spine.items[0]
        old_id = spine_item.idref
        new_id = EPUBId("new-id-spine")
        epub.rename_id(spine_item, new_id)

        assert epub.manifest.get(new_id)

    def test_change_cover(self, epub: EPUB) -> None:
        cover = epub.manifest.cover_image
        assert cover
        new_cover = next(
            image
            for image in epub.resources.filter(Category.IMAGE)
            if epub.manifest.get(image) is not cover
        )

        metadata_item = epub.metadata.get_valued("cover")

        epub.resources.set_cover_image(new_cover)
        assert epub.manifest.cover_image is not cover
        assert (
            len(
                [
                    item
                    for item in epub.manifest.items
                    if item.has_property("cover-image")
                ]
            )
            == 1
        )

        if metadata_item:
            assert metadata_item.value == epub.manifest[new_cover].id

    def test_no_nav(self, epub: EPUB) -> None:
        item = epub.manifest.nav
        item.properties = None

        with pytest.raises(EPUBError):
            __ = epub.manifest.nav

    def test_get_by_id(self, epub: EPUB) -> None:
        item = epub.manifest.items[0]
        assert epub.manifest[item.id]

        with pytest.raises(KeyError):
            __ = epub.manifest[EPUBId("non-existing")]

    def test_remove(self, epub: EPUB) -> None:
        item = epub.manifest.items[0]
        resource = epub.resources.get(item)
        assert resource

        epub.manifest.remove(item.filename)
        assert not epub.manifest.get(item.filename)
