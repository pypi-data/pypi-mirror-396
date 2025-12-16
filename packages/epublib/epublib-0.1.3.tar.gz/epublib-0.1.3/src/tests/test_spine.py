import enum
from pathlib import Path
from typing import final

import bs4
import pytest

from epublib import EPUB
from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.package.spine import SpineItemRef
from tests import shuffled


@final
class TestEPUBSpine:
    def test_spine(self, epub: EPUB) -> None:
        assert epub.spine
        assert epub.package_document.spine
        assert repr(epub.spine)

    def test_read(self, epub: EPUB) -> None:
        assert any(epub.spine.get(item.id) for item in epub.manifest.items)

    def test_edit(self, tmp_path: Path, epub: EPUB) -> None:
        item = epub.spine.items[0]
        item.linear = not item.linear

        outfn = tmp_path / "tmp.epub"
        epub.write(outfn)
        epub = EPUB(outfn)

        new_item = epub.spine.items[0]
        assert new_item == item

    def test_get_spine_item(self, epub: EPUB) -> None:
        assert epub.spine

        for item in epub.spine.items:
            manifest_item = epub.manifest[item.idref]
            assert manifest_item
            assert item is epub.get_spine_item(manifest_item.filename)

        assert epub.get_spine_item("xpto.xpto") is None

        res = epub.resources[epub.spine[0]]

        s = {
            item.idref if item else None
            for item in (
                epub.get_spine_item(res),
                epub.get_spine_item(res.filename),
                epub.get_spine_item(Path(res.filename)),
                epub.get_spine_item(epub.spine[0].idref),
                epub.get_spine_item(epub.spine[0]),
                epub.get_spine_item(epub.manifest[res.filename]),
            )
        }

        assert None not in s
        assert len(s) == 1

    def test_get_spine_item_by_index(self, epub: EPUB) -> None:
        assert epub.spine
        for i in range(len(epub.spine.items)):
            assert epub.spine[i]

    def test_get_spine_position(self, epub: EPUB) -> None:
        assert epub.spine

        for item in epub.spine.items:
            manifest_item = epub.manifest[item.idref]
            assert manifest_item
            resource = epub.resources.get(manifest_item)
            assert resource
            position = epub.get_spine_position(resource)
            assert position is not None
            assert epub.get_spine_position(resource.filename) == position

        assert epub.get_spine_position("xpto.xpto") is None

    class SpineItemRefReference(enum.Enum):
        BY_INDEX = enum.auto()
        BY_IDREF = enum.auto()
        BY_ITEM = enum.auto()

        def get(self, index: int, item: SpineItemRef) -> int | str | SpineItemRef:
            match self:
                case self.BY_ITEM:
                    return item
                case self.BY_IDREF:
                    return item.idref
                case self.BY_INDEX:
                    return index

    @pytest.mark.parametrize("reference", list(SpineItemRefReference))
    def test_move_item(
        self,
        epub: EPUB,
        epub_path: Path,
        reference: SpineItemRefReference,
    ):
        assert epub.spine
        assert len(epub.spine.items) > 1, (
            "SAMPLE ERROR: Not enough items in spine to test move"
        )

        first_item = epub.spine[0]
        second_item = epub.spine[1]

        epub.spine.move_item(reference.get(0, first_item), 1)
        assert epub.spine.items[0] == second_item
        assert epub.spine.items[1] == first_item

        epub.write(epub_path)
        epub = EPUB(epub_path)

        assert epub.spine
        assert epub.spine.items[0].idref == second_item.idref
        assert epub.spine.items[1].idref == first_item.idref

    @pytest.mark.parametrize("reference", list(SpineItemRefReference))
    def test_move_item_index_error(
        self,
        epub: EPUB,
        reference: SpineItemRefReference,
    ):
        assert epub.spine
        assert len(epub.spine.items) > 1, (
            "SAMPLE ERROR: Not enough items in spine to test move"
        )

        first_item = epub.spine[0]

        with pytest.raises(IndexError):
            epub.spine.move_item(
                reference.get(0, first_item),
                len(epub.spine.items) + 1,
            )
        with pytest.raises(IndexError):
            epub.spine.move_item(
                reference.get(0, first_item),
                -len(epub.spine.items) - 1,
            )

    def test_move_item_error(
        self,
        epub: EPUB,
    ):
        item = SpineItemRef(
            soup=bs4.BeautifulSoup("", "xml"),
            idref=EPUBId("xpto.xpto"),
        )

        with pytest.raises(EPUBError):
            epub.spine.move_item(item, 0)

    def test_reorder_items(
        self,
        epub: EPUB,
        epub_path: Path,
    ):
        assert epub.spine
        assert len(epub.spine.items) > 1, (
            "SAMPLE ERROR: Not enough items in spine to test move"
        )

        items = shuffled(list(epub.spine.items))
        epub.spine.reorder(items)

        assert list(epub.spine.items) == list(items)

        epub.write(epub_path)
        epub = EPUB(epub_path)

        assert [old.idref == new.idref for old, new in zip(epub.spine.items, items)]

    def test_reorder_items_errors(
        self,
        epub: EPUB,
    ):
        assert epub.spine
        assert len(epub.spine.items) > 1, (
            "SAMPLE ERROR: Not enough items in spine to test move"
        )

        items = shuffled(list(epub.spine.items))
        erroring = items + items[:1]

        with pytest.raises(EPUBError):
            epub.spine.reorder(erroring)

        erroring = items
        __ = erroring.pop(2)
        with pytest.raises(EPUBError):
            epub.spine.reorder(erroring)

        foreign_item = SpineItemRef(
            epub.package_document.soup,
            idref=EPUBId("xpto.xpto"),
        )
        erroring = items
        erroring[1] = foreign_item
        with pytest.raises(EPUBError):
            epub.spine.reorder(erroring)
