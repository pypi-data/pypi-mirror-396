import os
import shutil
import sys
import tempfile
import types
from collections.abc import Generator
from pathlib import Path
from typing import TypedDict

import bs4
import pytest as pytest
from sybil import Sybil
from sybil.parsers.markdown import PythonCodeBlockParser

from epublib.package.metadata import GenericMetadataItem, MetadataItem
from tests.conftest import samples


def create_some_custom_item() -> MetadataItem:
    soup = bs4.BeautifulSoup("", "xml")
    return GenericMetadataItem(soup, name="some", value="value")


class NS(TypedDict):
    directories: list[tempfile.TemporaryDirectory[str]]
    old_pwd: str
    sample: Path
    folder: Path


def get_sample(ns: NS) -> None:
    base = tempfile.TemporaryDirectory(delete=False)
    book = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    ns["directories"] = [base, book]
    ns["old_pwd"] = os.getcwd()
    os.chdir(base.name)

    __ = shutil.copy(samples.simple_epub, "book.epub")
    __ = shutil.copy(samples.image, "new-image.jpg")
    __ = shutil.move(samples.get_folder_epub(book.name), "book-folder")

    custom_item = types.ModuleType("custom_item")
    custom_item.create_some_custom_item = create_some_custom_item  # type: ignore[reportAttributeAccessIssue]
    sys.modules["custom_item"] = custom_item
    Path("book-folder-modified").mkdir(exist_ok=True)


def remove_sample(ns: NS) -> None:
    for d in ns["directories"]:
        d.cleanup()
    os.chdir(ns["old_pwd"])


pytest_collect_file = Sybil(
    parsers=[PythonCodeBlockParser()],
    pattern="*.md",
    setup=get_sample,  # type: ignore[reportArgumentType]
    teardown=remove_sample,  # type: ignore[reportArgumentType]
).pytest()


@pytest.fixture(autouse=True)
def add_np(doctest_namespace: NS) -> Generator[None]:
    doctest_namespace["sample"] = samples.simple_epub
    with tempfile.TemporaryDirectory() as folder:
        doctest_namespace["folder"] = Path(folder)
        yield
