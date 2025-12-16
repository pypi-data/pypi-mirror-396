# type: ignore

import filecmp
import os
import shutil
import subprocess as sp
from datetime import datetime
from os.path import expanduser, join
from pathlib import Path

try:
    import sigil_bs4 as bs4
except ImportError:
    import bs4

VENV_DIR = "venv"
MINIMUM_PYTHON3_VERSION = 13
SCRIPT_NAME = "entrypoint.py"
EPUBLIB_VERSION = "epublib @ git+https://gitlab.com/joaoseckler/epublib"


def get_absolute_href(origin_href, href) -> str:
    path = Path(origin_href).parent / Path(href)
    return os.path.normpath(path)


def get_package_path_from_container_file(out_dir) -> Path:
    """
    Parse the container.xml file at the root of the document. Only
    consider the first rootfile. Return also the filename of the package
    document
    """
    with open(Path(out_dir) / "META-INF/container.xml") as container_file:
        container_soup = bs4.BeautifulSoup(container_file)

    rootfile = container_soup.select_one("rootfile")
    assert rootfile, "Can't find rootfile in container.xml"

    return Path(rootfile.attrs.get("full-path", ""))


def get_manifest(out_dir) -> dict[str, str]:
    path = get_package_path_from_container_file(out_dir)

    with open(Path(out_dir) / path) as file:
        soup = bs4.BeautifulSoup(file)

    manifest_tag = soup.manifest
    assert manifest_tag, "Can't find manifest in package ('{}')".format(path)

    filename_to_id = {}
    for item in manifest_tag.find_all("item"):
        assert item.get("href"), "Found item with no href: {}".format(item)
        assert item.get("id"), "Found item with no id: {}".format(item)

        absolute_href = get_absolute_href(path, item["href"])
        filename_to_id[absolute_href] = item["id"]

    return filename_to_id


def mark_changes(wrapper, book_dir, out_dir) -> None:
    infiles = {
        file.relative_to(book_dir) for file in book_dir.rglob("*") if not file.is_dir()
    }
    outfiles = {
        file.relative_to(out_dir) for file in out_dir.rglob("*") if not file.is_dir()
    }
    outfiles -= {Path("sigil.cfg")}

    added = outfiles - infiles
    deleted = outfiles - infiles
    modified_candidates = infiles & outfiles
    modified: set[Path] = set()

    filename_to_id = get_manifest(out_dir)

    for path in modified_candidates:
        if not filecmp.cmp(book_dir / path, out_dir / path, shallow=False):
            modified.add(path)

    for path in modified:
        manifest_id = filename_to_id.get(path)
        if manifest_id:
            wrapper.modified[manifest_id] = "file"
        else:
            wrapper.modified[str(path)] = "file"

    for path in added:
        manifest_id = filename_to_id.get(path)
        if not manifest_id:
            print(
                "Couldn't write the file '%s' because there is no "
                "manifest entry associated" % path
            )
            continue
        wrapper.added.append(manifest_id)

    for path in deleted:
        manifest_id = filename_to_id.get(path)
        if manifest_id:
            wrapper.deleted.append(("other", manifest_id, str(path)))
        else:
            wrapper.deleted.append(("other", str(path), str(path)))

    # Warning: ugly hack ahead
    # We don't want sigil to overwrite our well formed content.opf
    wrapper.old_write_opf = wrapper.write_opf
    wrapper.write_opf = lambda: None


def discover_python() -> str:
    for minor in range(20, MINIMUM_PYTHON3_VERSION, -1):
        executable = shutil.which("python3.%s" % minor)
        if executable:
            return executable

    for template in (
        join(
            expanduser("~"),
            r"\AppData\Local\Programs\Python\Python3%s\python.exe",
        ),
        r"C:\Python3%s\python.exe",
        "/Library/Frameworks/Python.framework/Versions/3.%s/bin/python3",
        "/Library/Frameworks/Python.framework/Versions/3.%s/bin/python3",
        "/usr/bin/python3.%s",
        "/usr/local/bin/python3.%s",
    ):
        for minor in range(30, MINIMUM_PYTHON3_VERSION - 1, -1):
            executable = template % minor
            if Path(executable).is_file() and os.access(executable, os.X_OK):
                return executable

    raise ValueError(
        (
            "Couldn't find compatible python version. Please install"
            "python 3.{} or newer"
        ).format(MINIMUM_PYTHON3_VERSION)
    )


def get_venv_python(venv_folder) -> str:
    venv_python = venv_folder / "bin" / "python"
    if venv_python.is_file():
        return venv_python

    venv_python = venv_folder / "Scripts" / "python.exe"
    if venv_python.is_file():
        return venv_python

    raise ValueError("Couldn't find virtual environment's python executable!")


def create_venv(folder, venv_folder) -> None:
    base_python = discover_python()
    sp.run([base_python, "-m", "venv", venv_folder.name], cwd=folder)


def install_requirements(folder: Path, venv_python) -> None:
    requirements_path = folder / "requirements.txt"
    installed_ts_path = folder / "installed_timestamp"

    installed_ts = None
    if not requirements_path.is_file():
        with open(requirements_path, "w") as file:
            file.write(EPUBLIB_VERSION)
        requirements_ts = datetime.now()
    else:
        requirements_ts = datetime.fromtimestamp(requirements_path.stat().st_mtime)

    if installed_ts_path.is_file():
        with open(installed_ts_path) as file:
            installed_ts = datetime.fromtimestamp(float(file.read().strip()))

    if installed_ts is None or installed_ts < requirements_ts:
        print(" =========== INSTALLING DEPENDENCIES... =============")
        sp.run([venv_python, "-m", "ensurepip"], cwd=folder)
        sp.run(
            [venv_python, "-m", "pip", "install", "-r", str(requirements_path)],
            cwd=folder,
        )

        with open(installed_ts_path, "w") as file:
            file.write(str(datetime.now().timestamp()))


def get_venv(folder) -> str:
    venv_folder = folder / "venv"

    if not venv_folder.is_dir():
        create_venv(folder, venv_folder)

    venv_python = get_venv_python(venv_folder)
    install_requirements(folder, venv_python)

    return venv_python


def run_plugin(book_dir, out_dir) -> None:
    folder = Path(__file__).parent
    script = folder / SCRIPT_NAME

    venv_python = get_venv(folder)
    sp.run([venv_python, str(script), book_dir, out_dir], cwd=folder)


def run(bk) -> int:
    code_dir = Path(
        bk._w.plugin_dir,
        bk._w.plugin_name,
    )

    book_dir = Path(bk._w.ebook_root)
    out_dir = Path(bk._w.outdir)

    assert code_dir.is_dir(), "Couldn't find plugin folder! Tried %s" % code_dir
    assert book_dir.is_dir(), "Couldn't find book folder! Tried %s" % book_dir
    assert out_dir.is_dir(), "Couldn't find outpu folder! Tried %s" % out_dir

    run_plugin(book_dir, out_dir)
    mark_changes(bk._w, book_dir, out_dir)
    return 0
