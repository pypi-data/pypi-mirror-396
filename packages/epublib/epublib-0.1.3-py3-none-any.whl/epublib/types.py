from pathlib import Path
from typing import Protocol

from epublib.nav.resource import NavigationDocument
from epublib.ncx.resource import NCXFile
from epublib.package.manifest import BookManifest
from epublib.package.metadata import BookMetadata
from epublib.package.spine import BookSpine
from epublib.resources.manager import ContentDocumentManager, ResourceManager


class BookProtocol(Protocol):
    @property
    def resources(self) -> ResourceManager: ...

    @property
    def documents(self) -> ContentDocumentManager: ...

    @property
    def manifest(self) -> BookManifest: ...

    @property
    def metadata(self) -> BookMetadata: ...

    @property
    def spine(self) -> BookSpine: ...

    @property
    def nav(self) -> NavigationDocument: ...

    @property
    def ncx(self) -> NCXFile | None: ...

    @property
    def base_dir(self) -> Path: ...
