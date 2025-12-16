from pathlib import Path
from typing import final

from epublib import EPUB
from epublib.identifier import EPUBId
from epublib.resources import ContentDocument, PublicationResource, XMLResource
from epublib.resources.create import create_resource, create_resource_from_path
from epublib.util import attr_to_str, get_absolute_href, strip_fragment

from . import has_epubcheck, is_full_test, run_epubcheck, samples


def new_name(name: str) -> Path:
    return Path(*Path(name).parts[:-1], f"new-{Path(name).name}")


@final
class TestEPUBEndToEnd:
    """
    End-to-end tests here meaning to get a well formed EPUB, mess
    around with it using EPUBLib, and see if it still is well formed.
    Use EPUBCheck to check validity.
    """

    def mess_with_resources(self, book: EPUB) -> None:
        for item in book.documents:
            book.resources.rename(item, new_name(item.filename))

        for item in book.manifest.items:
            book.rename_id(item.id, EPUBId(f"new-{item.id}"))

        candidates = [
            res
            for res in book.resources.filter(PublicationResource)
            if not isinstance(res, ContentDocument) and res is not book.ncx
        ]

        for i in range(2, 4):
            if len(candidates) <= 2:
                break
            index = len(candidates) // i
            filename = candidates[index].filename
            book.resources.remove(candidates[index])
            for _, tag in book.resources.tags_referencing(
                filename,
                ignore_fragment=True,
            ):
                tag.decompose()

        candidates = [res for res in book.documents if res is not book.nav]
        for i in range(2, 4):
            if len(candidates) <= 2:
                break
            index = len(candidates) // i
            filename = candidates[index].filename
            book.resources.remove(candidates[index])
            for _, tag in book.resources.tags_referencing(
                filename,
                ignore_fragment=True,
            ):
                tag.decompose()

    def test_epub_end_to_end(self, epub: EPUB, epub_path: Path) -> None:
        self.mess_with_resources(epub)
        assert epub.manifest.nav

        epub.resources.add(create_resource_from_path(samples.image))
        epub.resources.add(create_resource(b"p { color: red; }", "styles.css"))
        epub.resources.add(
            create_resource(
                b"console.log('xpto')",
                "path/to/scripts/script.js",
            )
        )
        epub.reset_toc(title="Table of contents")
        epub.reset_landmarks()
        epub.reset_page_list()
        __ = epub.reset_ncx()
        assert epub.nav.toc.items

        self.mess_with_resources(epub)

        assert epub.nav.toc.items

        epub.update_manifest_properties()

        for resource in epub.resources.filter(XMLResource):
            for attr in ("src", "href", "src", "xml:href"):
                for tag in resource.soup.find_all(attrs={attr: True}):
                    relative = attr_to_str(tag[attr])
                    absolute = get_absolute_href(resource.filename, relative)
                    assert epub.resources.get(strip_fragment(absolute)), absolute

            for tag in resource.soup.find_all(attrs={"id": True}):
                assert EPUBId.is_valid(attr_to_str(tag["id"]))

        if has_epubcheck() and is_full_test():
            epub.write(epub_path)
            assert run_epubcheck(epub_path)
