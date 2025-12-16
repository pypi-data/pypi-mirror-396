import datetime
import io
import shutil
import tempfile
import zipfile
from collections.abc import Generator
from pathlib import Path
from random import choice
from string import ascii_lowercase
from typing import Literal, cast, final, override

import bs4
import pytest

import epublib.source
from epublib import EPUB
from epublib.create import EPUBCreationError, EPUBCreator
from epublib.exceptions import ClosedEPUBError, EPUBError, NotEPUBError
from epublib.identifier import EPUBId
from epublib.media_type import Category, MediaType
from epublib.nav.resource import NavigationDocument
from epublib.package.resource import PackageDocument
from epublib.resources import (
    ContentDocument,
    PublicationResource,
    Resource,
    XMLResource,
)
from epublib.resources.create import create_resource, create_resource_from_path
from epublib.source import DirectorySink, DirectorySource
from epublib.util import (
    attr_to_str,
    get_absolute_href,
    get_relative_href,
    split_fragment,
)

from . import samples


@final
class TestEPUB:
    @pytest.fixture
    def not_epubs(self, tmp_path: Path) -> Generator[Path]:
        fname = tmp_path / "zip.zip"

        def files() -> Generator[Path]:
            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr("test.txt", "xpto")
            yield fname

            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr("META-INF/container.xml", "not xml")
            yield fname

            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr(
                    "META-INF/container.xml",
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<container version="1.0" '
                    'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                    "</container>",
                )
            yield fname

            with zipfile.ZipFile(fname, "w") as zf:
                zf.writestr(
                    "META-INF/container.xml",
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<container version="1.0" '
                    'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                    "<rootfiles>"
                    '<rootfile media-type="application/oebps-package+xml"/>'
                    "</rootfiles>"
                    "</container>",
                )
            yield fname

        return files()

    def test_non_epub(self, not_epubs: Generator[Path]) -> None:
        with pytest.raises(NotEPUBError):
            __ = EPUB(samples.image)

        for fname in not_epubs:
            with pytest.raises(NotEPUBError):
                __ = EPUB(fname)

    def test_ignore_dirs(self, tmp_path: Path) -> None:
        fname = shutil.copy(samples.epub, tmp_path / "tmp.epub")
        with zipfile.ZipFile(fname, "a") as zf:
            zf.writestr("somefolder/", "")

        with EPUB(fname) as epub:
            assert not any(res.filename == "somefolder" for res in epub.resources)

    def test_context(self, tmp_path: Path) -> None:
        with EPUB(samples.epub) as epub:
            self._test_epub(epub)

        assert epub.closed
        with pytest.raises(ClosedEPUBError):
            epub.write(tmp_path / "tmp.epub")

    def _test_epub(self, epub: EPUB) -> None:
        assert len(epub.resources)
        assert repr(epub)
        assert any(
            isinstance(resource, PackageDocument) for resource in epub.resources
        ), "Package document does not exist"
        assert any(
            isinstance(resource, ContentDocument) for resource in epub.resources
        ), "No content document exists"

    def test_read(self, epub: EPUB) -> None:
        self._test_epub(epub)

    def test_folder_read(self, folder_epub: EPUB) -> None:
        self._test_epub(folder_epub)

    def test_directory_io(self) -> None:
        with pytest.raises(EPUBError):
            __ = DirectorySource("non-existing-folder")

        with pytest.raises(EPUBError):
            __ = DirectorySink("non-existing-folder")

        with tempfile.TemporaryDirectory() as tmpdirname:
            tempdir = Path(tmpdirname)
            files: list[Path] = []
            for _ in range(10):
                file = tempdir / Path(
                    *(choice(ascii_lowercase) for _ in range(choice(range(1, 6)))),
                    choice(ascii_lowercase) + ".txt",
                )
                file.parent.mkdir(parents=True, exist_ok=True)
                file.touch()
                files.append(file)

            source = DirectorySource(tempdir)
            for file in files:
                name = str(file.relative_to(tempdir))
                assert source.getinfo(name)
                with source.open(name) as f:
                    assert f.read() == b""

            with pytest.raises(KeyError):
                __ = source.getinfo("non-existing-file.txt")

            with tempfile.TemporaryDirectory() as outdirname:
                outdir = Path(outdirname)
                sink = DirectorySink(outdir)
                for file in files:
                    name = str(file.relative_to(tempdir))
                    sink.writestr(name, "content")
                    out_file = outdir / name
                    assert out_file.exists()
                    with open(out_file) as f:
                        assert f.read() == "content"

    def test_write(self, tmp_path: Path, epub: EPUB) -> None:
        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)

        out = EPUB(outfn)
        self._test_epub(out)

    def test_double_write(self, tmp_path: Path, epub: EPUB) -> None:
        out1 = tmp_path / "tmp1.epub"
        out2 = tmp_path / "tmp2.epub"

        doc = epub.documents[0]
        assert doc.soup.body
        __ = doc.soup.body.append(doc.soup.new_tag("div", attrs={"id": "id-1"}))

        epub.write(out1)

        epub = EPUB(out1)
        doc = epub.resources.get(doc.filename, ContentDocument)
        assert doc
        assert doc.soup.body
        __ = doc.soup.body.append(doc.soup.new_tag("div", attrs={"id": "id-2"}))

        epub.write(out2)
        epub = EPUB(out2)
        doc = epub.resources.get(doc.filename, ContentDocument)
        assert doc

        assert doc.soup.find(id="id-1")
        assert doc.soup.find(id="id-2")

    def test_folder_write(self, tmp_path: Path, epub: EPUB) -> None:
        outfn = tmp_path / "folder_epub"
        outfn.mkdir(exist_ok=True)
        epub.write_to_folder(outfn)

        epub = EPUB(outfn)
        self._test_epub(epub)

    def test_read_after_write(self, tmp_path: Path, epub: EPUB) -> None:
        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)

        self._test_epub(epub)

    def test_edit_xml(self, tmp_path: Path, epub: EPUB) -> None:
        xml = next(
            cast(ContentDocument[bs4.BeautifulSoup], res)
            for res in epub.resources
            if isinstance(res, ContentDocument) and res.media_type is MediaType.XHTML
        )

        soup = xml.soup
        filename = xml.filename
        div = soup.new_tag("div")
        div["id"] = "testid-xxx"

        assert xml.soup.body
        _ = xml.soup.body.append(div)

        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)

        out = EPUB(outfn)
        new_xml = out.resources.get(filename, XMLResource)
        assert new_xml
        assert new_xml.soup.find(id="testid-xxx"), filename

    def test_resolve_href(self, epub: EPUB) -> None:
        doc = next(doc for doc in epub.documents if doc.soup.find(id=True))
        filename = doc.filename

        target_tag = doc.soup.find(id=True)
        assert target_tag
        target = attr_to_str(target_tag["id"])

        resource = epub.resources.resolve_href(filename, False)

        assert resource
        assert resource.filename == filename

        resource = epub.resources.resolve_href(
            Path(filename).name,
            False,
            relative_to=Path(filename).parent / "another-file.xhtml",
        )
        assert resource
        assert resource.filename == filename

        resource = epub.resources.resolve_href(
            get_relative_href(epub.scripts[0].filename, filename),
            False,
            relative_to=epub.scripts[0],
        )
        assert resource
        assert resource.filename == filename

        resource, tag = epub.resources.resolve_href(
            f"{filename}#{target}",
            query=ContentDocument,
        )
        assert resource
        assert tag
        assert tag.name == target_tag.name

        assert epub.resources.resolve_href("xpto/xpto", False) is None
        assert epub.resources.resolve_href("xpto/xpto") == (None, None)

        resource, tag = epub.resources.resolve_href(
            f"{filename}#invalid:id",
            query=ContentDocument,
        )
        assert tag is None

    def test_create_epub(self, epub_path: Path) -> None:
        epub = EPUB()

        assert epub.metadata
        assert epub.metadata.get("language")
        assert epub.metadata.get("identifier")
        assert epub.metadata.get("title")

        assert epub.manifest
        assert epub.spine

        assert len(epub.resources)

        epub.resources.add(ContentDocument(b"", "Text/chapter1.xhtml"))

        epub.write(epub_path)

        with EPUB(epub_path) as epub:
            assert epub.metadata
            assert epub.manifest
            assert epub.spine
            assert len(epub.resources)
            assert epub.resources.get("Text/chapter1.xhtml")

    def test_create_epub_errors(self) -> None:
        with pytest.raises(EPUBCreationError):
            _ = EPUBCreator(package_document_path="")

        with pytest.raises(EPUBCreationError):
            _ = EPUBCreator(package_document_path="content.xml")

        with pytest.raises(EPUBCreationError):
            _ = EPUBCreator(navigation_document_path="")

        with pytest.raises(EPUBCreationError):
            _ = EPUBCreator(navigation_document_path="etwas.html")

    @pytest.mark.parametrize("as_file", [True, False])
    def test_create_epub_with_options(self, as_file: bool) -> None:
        creator = EPUBCreator(
            language="es-ES",
            book_title="title",
            unique_identifier="other-id",
            package_document_path="some/path/to/opf.opf",
            navigation_document_path="another/path/to/nav.xhtml",
            navigation_document_title="Nav Title",
            toc_title="Table of Contents",
        )
        if as_file:
            file = creator.to_file()
            epub = EPUB(file)
        else:
            bytes = creator.to_bytes()
            epub = EPUB(io.BytesIO(bytes))

        assert epub.metadata
        assert epub.metadata.language == "es-ES"
        assert epub.metadata.title == "title"
        assert epub.package_document.soup.package
        assert epub.package_document.soup.package["unique-identifier"] == "other-id"
        assert epub.package_document.filename == "some/path/to/opf.opf"
        assert epub.nav.filename == "another/path/to/nav.xhtml"
        title_tag = epub.nav.soup.select_one("head > title")
        assert title_tag
        assert title_tag.string == "Nav Title"
        assert epub.nav.toc.title == "Table of Contents"
        assert all(
            item.text == "Table of Contents"
            for item in epub.nav.toc.items_referencing(epub.nav.filename)
        )

    def test_read_after_close(self) -> None:
        epub = EPUB(samples.epub)
        epub.close()
        with pytest.raises(ClosedEPUBError):
            __ = epub.resources[0].content


class TestResourceManagement:
    def test_get_by_id(self, epub: EPUB) -> None:
        identifier = epub.spine.items[0].idref
        assert epub.resources.get(EPUBId(identifier))

    def test_resource_class_choice(self) -> None:
        assert type(create_resource(b"", "META-INF/xpto.xml")) is Resource
        assert (
            type(create_resource(b"", "xpto.xhtml", MediaType.XHTML)) is ContentDocument
        )
        assert (
            type(create_resource(b"", "xpto.xhtml", MediaType.XHTML, True))
            is NavigationDocument
        )
        assert type(
            create_resource(b"", "xpto.svg", MediaType.IMAGE_SVG) is ContentDocument
        )
        assert (
            type(create_resource(b"", "xpto.jpeg", MediaType.IMAGE_JPEG))
            is PublicationResource
        )
        assert type(
            create_resource(b"", "xpto.js", MediaType.JAVASCRIPT) is PublicationResource
        )

    def test_create_resource(self) -> None:
        resource = create_resource_from_path(samples.image)
        assert Path(resource.filename).name == samples.image.name

        with pytest.raises(EPUBError):
            resource = create_resource_from_path(samples.image, is_nav=True)

    @pytest.mark.parametrize("identifier", [None, EPUBId("custom-id"), "string-ig"])
    @pytest.mark.parametrize("method", ["add", "append", "insert"])
    def test_add(
        self,
        epub: EPUB,
        resource: Resource,
        identifier: str | EPUBId | None,
        method: Literal["add", "append", "insert"],
    ):
        if method == "add":
            epub.resources.add(resource, identifier=identifier)
        if method == "append":
            epub.resources.append(resource, identifier=identifier)
        if method == "insert":
            epub.resources.insert(0, resource, identifier=identifier)
            assert all(
                epub.resources.index(pub) > epub.resources.index(resource)
                or pub is resource
                for pub in epub.resources.filter(PublicationResource)
            )

        assert epub.resources.get(resource.filename)
        manifest_item = epub.manifest.get(resource.filename)
        assert manifest_item
        assert manifest_item.id
        if identifier is not None:
            assert manifest_item.id == identifier
        assert type(manifest_item.id) is EPUBId
        assert epub.spine.get(manifest_item.id) is None

    def test_add_after_before(self, epub: EPUB) -> None:
        res1 = ContentDocument(b"", "Text/chapter2.xhtml")
        epub.resources.add(res1, after=epub.documents[0])

        assert epub.documents.index(res1) > 0

        res2 = ContentDocument(b"", "Text/chapter3.xhtml")
        epub.resources.add(res2, after=epub.documents[0].filename)
        assert epub.documents.index(res2) < epub.documents.index(res1)

        res1 = ContentDocument(b"", "Text/chapter4.xhtml")
        epub.resources.add(res1, before=epub.documents[-1])

        assert epub.documents.index(res1) < epub.documents.index(epub.documents[-1])

        res2 = ContentDocument(b"", "Text/chapter5.xhtml")
        epub.resources.add(res2, before=epub.documents[-1].filename)
        assert epub.documents.index(res2) > epub.documents.index(res1)

    def test_add_after_before_error(
        self,
        epub: EPUB,
        resources: Generator[Resource],
    ) -> None:
        resource = next(resources)
        other_resource = next(resources)

        with pytest.raises(EPUBError):
            epub.resources.add(resource, after=other_resource)

        with pytest.raises(EPUBError):
            epub.resources.add(resource, before=other_resource)

    def test_add_to_manifest_errors(self, epub: EPUB, resource: Resource) -> None:
        with pytest.raises(EPUBError):
            epub.resources.add(resource, add_to_manifest=False, add_to_spine=True)

        with pytest.raises(EPUBError):
            epub.resources.add(resource, add_to_manifest=False, add_to_toc=True)

    def test_add_to_manifest(self, epub: EPUB, resource: Resource) -> None:
        resource = create_resource(b"", "Text/chapter2.xhtml")
        pub, manifest_item = epub.resources.add_to_manifest(resource)

        assert pub is resource
        assert epub.manifest.get(resource.filename) is manifest_item

        resource = Resource(b"", "Text/chapter3.xhtml")
        pub, manifest_item = epub.resources.add_to_manifest(resource)
        assert pub is not resource

        pub, manifest_item = epub.resources.add_to_manifest(pub, exists_ok=True)
        with pytest.raises(EPUBError):
            pub, manifest_item = epub.resources.add_to_manifest(pub)

    def test_add_with_position(self, epub: EPUB, resource: Resource) -> None:
        epub.resources.add(resource, position=3)
        assert epub.resources[3] is resource

    def test_add_to_spine(self, epub: EPUB, resource: Resource) -> None:
        epub.resources.add(resource, add_to_spine=True)

        manifest_item = epub.manifest.get(resource.filename)
        assert manifest_item
        assert epub.spine.get(manifest_item.id)

    def test_add_to_spine_with_position(self, epub: EPUB, resource: Resource) -> None:
        epub.resources.add(resource, add_to_spine=True, spine_position=2)

        tag = epub.spine.tag.find_all("itemref")[2]
        assert tag
        assert isinstance(tag, bs4.Tag)
        assert tag["idref"] == epub.manifest[resource.filename].id

    def test_add_cover(self, epub: EPUB, resource: Resource) -> None:
        epub.resources.add(resource, is_cover=True)

        manifest_item = epub.manifest.get(resource.filename)
        assert manifest_item
        assert manifest_item.properties
        assert "cover-image" in manifest_item.properties

    def test_set_cover(self, epub: EPUB, resource: Resource) -> None:
        epub.resources.add(resource)
        epub.resources.set_cover_image(resource)

        manifest_item = epub.manifest.get(resource.filename)
        assert manifest_item
        assert manifest_item.properties
        assert "cover-image" in manifest_item.properties
        assert epub.resources.cover_image is resource

        resource = create_resource(b"", "Images/cover2.jpeg")
        with pytest.raises(EPUBError):
            epub.resources.set_cover_image(resource)

        with pytest.raises(EPUBError):
            epub.resources.set_cover_image(resource.filename)

        doc = create_resource(b"", "Images/chapter15.xhtml")
        epub.resources.add(doc)

        with pytest.raises(EPUBError, match="must be.*image"):
            epub.resources.set_cover_image(doc)

    def test_remove_cover(self, epub: EPUB) -> None:
        cover = epub.resources.cover_image
        assert cover
        assert epub.metadata.get("cover")

        epub.resources.remove(cover)
        assert epub.manifest.cover_image is None
        assert not epub.metadata.get("cover")

    def test_add_to_nav(self, epub: EPUB, resource: Resource) -> None:
        epub.resources.add(resource, add_to_toc=True)

        assert epub.nav.toc.tag.select(f'[href$="{Path(resource.filename).name}"]')

    @pytest.mark.parametrize("n", range(2))
    def test_add_to_nav_with_position(
        self,
        epub: EPUB,
        resource: Resource,
        n: int,
    ) -> None:
        epub.resources.add(resource, add_to_toc=True, toc_position=n)

        assert (
            Path(epub.nav.toc.items[n].href or "").name == Path(resource.filename).name
        )

    @pytest.mark.parametrize("n", range(4))
    def test_resource_removal(self, epub: EPUB, epub_path: Path, n: int) -> None:
        resource = next(
            r
            for r in epub.resources.filter(ContentDocument)
            if not isinstance(r, NavigationDocument)
        )
        if n == 0:
            epub.resources.remove(resource.filename)
        elif n == 1:
            epub.resources.remove(resource)
        elif n == 2:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.remove(item)
        elif n == 3:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.remove(item.id)

        epub.write(epub_path)

        epub = EPUB(epub_path)

        never = epub.resources.get(resource.filename)
        assert never is None

        assert epub.manifest.get(resource.filename) is None
        assert epub.get_spine_item(resource.filename) is None
        assert resource.filename not in epub.nav.content.decode()

        resource = create_resource(b"", "Text/chapter10.xhtml")
        with pytest.raises(EPUBError):
            epub.resources.remove(resource)
        with pytest.raises(EPUBError):
            epub.resources.remove(resource.filename)

    def test_css_removal(self, epub: EPUB, epub_path: Path) -> None:
        resource = next(epub.resources.filter(MediaType.CSS))
        epub.resources.remove(resource)
        epub.write(epub_path)

        epub = EPUB(epub_path)

        never = epub.resources.get(resource.filename)
        assert never is None

        for res in epub.resources.filter(ContentDocument):
            for tag in res.soup.find_all("link", rel="stylesheet", href=True):
                assert isinstance(tag, bs4.Tag)
                relative_href = get_relative_href(res.filename, resource.filename)
                assert tag["href"] != relative_href

    def test_js_removal(self, epub: EPUB, epub_path: Path) -> None:
        resource = next(epub.resources.filter(MediaType.JAVASCRIPT))
        epub.resources.remove(resource)
        epub.write(epub_path)

        epub = EPUB(epub_path)

        never = epub.resources.get(resource.filename)
        assert never is None

        for res in epub.resources.filter(ContentDocument):
            for tag in res.soup.find_all("script", src=True):
                assert isinstance(tag, bs4.Tag)
                relative_href = get_relative_href(res.filename, resource.filename)
                assert tag["src"] != relative_href

    def test_removal_errors(self, epub: EPUB, resource: Resource) -> None:
        with pytest.raises(EPUBError):
            epub.resources.remove(epub.package_document)

        with pytest.raises(EPUBError):
            epub.resources.remove(epub.container_file)

        with pytest.raises(EPUBError):
            epub.resources.remove(resource)

        with pytest.raises(EPUBError):
            existing = next(epub.resources.filter(MediaType.XHTML))
            epub.resources.remove(
                existing,
                remove_css_js_links=True,  # type: ignore[reportArgumentType]
            )

    def _valid_hrefs(self, epub: EPUB) -> None:
        reference_attrs = ["href", "src", "full-path", "xlink:href"]
        selector = ", ".join(f"[{attr.replace(':', '|')}]" for attr in reference_attrs)

        for resource in epub.resources.filter(XMLResource):
            for tag in resource.soup.select(selector):
                for attr in reference_attrs:
                    value = tag.get(attr)
                    if value is not None:
                        ref, identifier = split_fragment(str(value))
                        if ref:
                            if attr == "full-path":
                                absolute_href = ref
                            else:
                                absolute_href = get_absolute_href(
                                    resource.filename,
                                    ref,
                                )
                            if identifier:
                                absolute_href += f"#{identifier}"

                            res, ref_tag = epub.resources.resolve_href(absolute_href)
                            assert res, absolute_href

                            if "#" in value:
                                assert ref_tag

    @pytest.mark.parametrize("n", range(4))
    def test_resource_rename(self, epub: EPUB, epub_path: Path, n: int) -> None:
        self._valid_hrefs(epub)

        resource = next(
            r
            for r in epub.resources.filter(ContentDocument)
            if not isinstance(r, NavigationDocument)
            and Path(r.filename).name in epub.nav.content.decode()
        )

        assert resource.soup.body
        __ = resource.soup.body.append(resource.soup.new_tag("a", attrs={"href": "#"}))
        __ = resource.soup.body.append(
            resource.soup.new_tag("a", attrs={"href": Path(resource.filename).name})
        )
        new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"

        if n == 0:
            epub.resources.rename(resource, new_filename)
        elif n == 1:
            epub.resources.rename(resource.filename, new_filename)
        elif n == 2:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.rename(item, new_filename)
        elif n == 3:
            item = epub.manifest.get(resource)
            assert item
            epub.resources.rename(item.id, new_filename)

        assert epub.manifest.get(new_filename)

        epub.write(epub_path)
        epub = EPUB(epub_path)

        new_resource = epub.resources.get(new_filename)
        assert new_resource
        self._valid_hrefs(epub)

        assert epub.manifest.get(new_filename)
        assert epub.get_spine_item(new_filename)
        assert Path(new_filename).name in epub.nav.content.decode()

        resource = create_resource(b"", "Text/chapter10.xhtml")
        with pytest.raises(EPUBError):
            epub.resources.rename(resource, "something/completely/different.xhtml")
        with pytest.raises(EPUBError):
            epub.resources.rename(
                resource.filename, "something/completely/different.xhtml"
            )

    def test_nav_rename(self, epub: EPUB, epub_path: Path) -> None:
        self._valid_hrefs(epub)
        resource = epub.nav

        new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
        epub.resources.rename(resource, new_filename)
        epub.write(epub_path)
        epub = EPUB(epub_path)

        new_resource = epub.resources.get(new_filename)
        assert new_resource
        self._valid_hrefs(epub)

        assert epub.manifest.get(new_filename)
        assert epub.get_spine_item(new_filename)

    def test_package_document_rename(self, epub: EPUB, epub_path: Path) -> None:
        self._valid_hrefs(epub)
        resource = epub.package_document

        new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
        epub.resources.rename(resource, new_filename)
        epub.write(epub_path)
        epub = EPUB(epub_path)

        new_resource = epub.resources.get(new_filename)
        assert new_resource
        self._valid_hrefs(epub)

    def test_rename_errors(self, epub: EPUB, resource: Resource) -> None:
        with pytest.raises(EPUBError):
            new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
            epub.resources.rename(resource, new_filename)

        with pytest.raises(EPUBError):
            resource = epub.container_file
            new_filename = f"new_folder/new_file{Path(resource.filename).suffix}"
            epub.resources.rename(resource, new_filename)

    def test_generator(self, epub: EPUB) -> None:
        assert epub.metadata.get("generator")
        assert epub.metadata.get("epublib version")

        epub.remove_generator_tag()

        assert not epub.metadata.get("generator")
        assert not epub.metadata.get("epublib version")

    def test_window_managers(self, epub: EPUB) -> None:
        resource = ContentDocument(b"", "text/newest-chapter.xhtml")
        epub.documents.add(resource, add_to_manifest=True, add_to_spine=True)
        assert epub.resources.get(resource.filename)

        assert all(isinstance(res, ContentDocument) for res in epub.documents)
        for i in range(len(epub.documents)):
            assert isinstance(epub.documents[i], ContentDocument)
        assert list(epub.resources.filter(ContentDocument)) == list(epub.documents)
        with pytest.raises(EPUBError):
            new_res = create_resource(b"", "text/another.jpeg")
            epub.documents.add(new_res)  # type: ignore[reportArgumentType]

        new_res = create_resource(b"", "text/another.xhtml")

        assert all(isinstance(res, PublicationResource) for res in epub.images)
        assert all(res.media_type.category is Category.IMAGE for res in epub.images)
        for i in range(len(epub.images)):
            assert isinstance(epub.images[i], PublicationResource)
            assert epub.images[i].media_type.category is Category.IMAGE
        assert list(epub.resources.filter(Category.IMAGE)) == list(epub.images)
        with pytest.raises(EPUBError):
            epub.images.add(new_res)  # type: ignore[reportArgumentType]
        assert epub.images.cover

        assert all(isinstance(res, PublicationResource) for res in epub.scripts)
        assert all(res.media_type.is_js() for res in epub.scripts)
        for i in range(len(epub.scripts)):
            assert isinstance(epub.scripts[i], PublicationResource)
            assert epub.scripts[i].media_type.is_js()
        with pytest.raises(EPUBError):
            epub.scripts.add(new_res)  # type: ignore[reportArgumentType]

        assert all(isinstance(res, PublicationResource) for res in epub.styles)
        assert all(res.media_type.category is Category.STYLE for res in epub.styles)
        for i in range(len(epub.styles)):
            assert isinstance(epub.styles[i], PublicationResource)
            assert epub.styles[i].media_type.category is Category.STYLE
        assert list(epub.resources.filter(Category.STYLE)) == list(epub.styles)
        with pytest.raises(EPUBError):
            epub.styles.add(new_res)  # type: ignore[reportArgumentType]

        assert all(isinstance(res, PublicationResource) for res in epub.fonts)
        assert all(res.media_type.category is Category.FONT for res in epub.fonts)
        for i in range(len(epub.fonts)):
            assert isinstance(epub.fonts[i], PublicationResource)
            assert epub.fonts[i].media_type.category is Category.FONT
        assert list(epub.resources.filter(Category.FONT)) == list(epub.fonts)
        with pytest.raises(EPUBError):
            epub.fonts.add(new_res)  # type: ignore[reportArgumentType]

        assert all(isinstance(res, PublicationResource) for res in epub.audios)
        assert all(res.media_type.category is Category.AUDIO for res in epub.audios)
        for i in range(len(epub.audios)):
            assert isinstance(epub.audios[i], PublicationResource)
            assert epub.audios[i].media_type.category is Category.AUDIO
        assert list(epub.resources.filter(Category.AUDIO)) == list(epub.audios)
        with pytest.raises(EPUBError):
            epub.audios.add(new_res)  # type: ignore[reportArgumentType]

        assert all(isinstance(res, PublicationResource) for res in epub.videos)
        assert all(res.media_type.is_video() for res in epub.videos)
        for i in range(len(epub.videos)):
            assert isinstance(epub.videos[i], PublicationResource)
            assert epub.videos[i].media_type.is_video()
        with pytest.raises(EPUBError):
            epub.videos.add(new_res)  # type: ignore[reportArgumentType]

        assert all(
            isinstance(res, PublicationResource) for res in epub.publication_resources
        )
        assert all(res.media_type for res in epub.publication_resources)
        for i in range(len(epub.publication_resources)):
            assert isinstance(epub.publication_resources[i], PublicationResource)
            assert epub.publication_resources[i].media_type
        with pytest.raises(EPUBError):
            new_res = Resource(b"", "text/another.unknown")
            epub.publication_resources.add(new_res)  # type: ignore[reportArgumentType]

        assert repr(epub.documents)

    def test_manager_operations(self, epub: EPUB) -> None:
        for manager in [
            epub.resources,
            epub.documents,
            epub.images,
            epub.scripts,
            epub.styles,
            epub.fonts,
            epub.audios,
            epub.videos,
        ]:
            if len(manager) < 2:
                continue
            with pytest.raises(KeyError):
                __ = manager["non-existing-file.ext"]

            assert list(reversed(manager)) == list(reversed(list(manager)))

            assert manager.count(manager[0]) == 1  # type: ignore[reportArgumentType]
            for i, item in enumerate(manager):
                assert manager.index(item) == i  # type: ignore[reportArgumentType]

            res_set = set(manager)
            manager[0], manager[1] = manager[1], manager[0]  # type: ignore[reportArgumentType]
            assert set(manager) == res_set

            old_len = len(manager)
            del manager[1]
            assert old_len == len(manager) + 1

    def test_guide(self, epub: EPUB) -> None:
        if epub.guide:
            assert epub.guide
            assert repr(epub.guide)

            for reference in epub.guide.items:
                assert reference.type
                assert reference.title
                assert reference.href
                assert reference.filename
                resource = epub.resources.get(reference.filename)
                assert resource

            item = epub.guide.add("Text/cover.xhtml", "Cover", "cover")
            assert item in epub.guide.items
            assert item.type == "cover"
            assert item.filename == "Text/cover.xhtml"
            assert item.title == "Cover"

    @pytest.fixture
    def future(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class futuredatetime(datetime.datetime):
            @classmethod
            @override
            def now(cls, tz: datetime.tzinfo | None = None) -> datetime.datetime:
                return super().now(tz) + datetime.timedelta(days=100 * 365)

        monkeypatch.setattr(
            epublib.source,
            "datetime",
            futuredatetime,
        )

    def test_zip_info_date(self, future: None) -> None:
        __ = future
        resource = Resource(b"", "text/chapter10.xhtml")
        assert resource.zipinfo.date_time[0] < 2108
        assert resource.zipinfo.date_time[0] > 2106
