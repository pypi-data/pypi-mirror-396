import os
import random
import shutil
import subprocess
from pathlib import Path
from typing import final
from zipfile import ZipFile

from epublib import EPUB

SAMPLES_DIR = Path(__file__).parent / "samples"


def is_full_test():
    return bool(os.environ.get("EPUBLIB_TEST_FULL"))


def has_epubcheck():
    return bool(shutil.which("epubcheck"))


def run_epubcheck(epub: Path | str) -> bool:
    epub = Path(epub)
    os.chdir(epub.parent)

    result = subprocess.run(
        ["epubcheck", epub.name],
    )
    return result.returncode == 0


@final
class Samples:
    _epub = SAMPLES_DIR / "sample.epub"
    simple_epub = SAMPLES_DIR / "simple.epub"
    image = SAMPLES_DIR / "image.jpg"
    page = SAMPLES_DIR / "page.xhtml"
    _tmp_dir = SAMPLES_DIR / "tmp"

    @property
    def epub(self) -> Path:
        sample = os.environ.get("EPUBLIB_EPUB_SAMPLE")
        if sample:
            return Path(sample)
        return self._epub

    @property
    def tmp_dir(self) -> Path:
        if self._tmp_dir.is_dir():
            shutil.rmtree(self._tmp_dir)

        self._tmp_dir.mkdir(parents=True, exist_ok=True)
        return SAMPLES_DIR / "tmp"

    def get_folder_epub(self, folder: Path | str) -> Path:
        with EPUB(self.epub) as epub:
            assert isinstance(epub.source, ZipFile)
            epub.source.extractall(folder)

        return Path(folder)


samples = Samples()


def view_epub(file: str | Path | EPUB) -> None:
    if isinstance(file, EPUB):
        filename = samples.tmp_dir / "tmp.epub"
        file.write(filename)
    else:
        filename = file
    __ = subprocess.call(["xdg-open", str(filename)])


def shuffled[T](lst: list[T]) -> list[T]:
    """
    Return a shuffled copy of a list, making sure it is different from
    the original. The seed is used for reproducibility.
    """

    if len(lst) < 2:
        return lst[:]

    new_list = lst[:]
    i = 100
    seed = 42
    rng = random.Random()

    while new_list == lst and i > 0:
        rng.seed(seed)
        rng.shuffle(new_list)
        seed += 1
        i -= 1

    if i == 0:
        raise RuntimeError("Could not shuffle the list")

    return new_list
