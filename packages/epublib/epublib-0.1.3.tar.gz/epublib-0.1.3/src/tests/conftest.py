import tempfile
from pathlib import Path

import pytest

from epublib import EPUB
from epublib.resources.create import create_resource_from_path

from . import samples


@pytest.fixture
def epub():
    with EPUB(samples.epub) as epub:
        yield epub


@pytest.fixture
def folder_epub():
    with tempfile.TemporaryDirectory() as dir:
        with EPUB(samples.get_folder_epub(dir)) as epub:
            yield epub


@pytest.fixture
def resource():
    return create_resource_from_path(samples.image)


@pytest.fixture
def epub_path(tmp_path: Path) -> Path:
    return tmp_path / "tmp.epub"


@pytest.fixture
def resources():
    def yield_resources():
        while True:
            yield create_resource_from_path(samples.image)

    return yield_resources()
