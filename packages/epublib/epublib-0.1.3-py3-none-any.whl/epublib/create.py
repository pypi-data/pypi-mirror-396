import io
import zipfile
from datetime import datetime
from typing import TypedDict, Unpack

from epublib.exceptions import EPUBError
from epublib.identifier import EPUBId
from epublib.media_type import MediaType
from epublib.package.manifest import ManifestItem
from epublib.package.resource import PackageDocument
from epublib.package.spine import SpineItemRef
from epublib.util import get_epublib_version


class EPUBCreationError(EPUBError):
    pass


mimetype = "application/epub+zip"
container_xml: str = """\
<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="{package_document_path}" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
"""

package_document_skeleton: str = """\
<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="{unique_identifier}">
  <metadata
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:opf="http://www.idpf.org/2007/opf"
  ></metadata>
  <manifest></manifest>
  <spine></spine>
</package>
"""

navigation_document_skeleton: str = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:epub="http://www.idpf.org/2007/ops"
>
  <head>
    <title>{title}</title>
    <meta charset="utf-8"/>
  </head>
  <body>
    <nav epub:type="toc" id="toc" role="doc-toc">
      <h1>{toc_title}</h1>
      <ol>
      <li><a href="#toc">{toc_title}</a></li>
      </ol>
    </nav>
  </body>
</html>
"""


class EPUBCreationOptions(TypedDict, total=False):
    language: str
    book_title: str
    unique_identifier: str
    package_document_path: str
    navigation_document_path: str
    navigation_document_title: str
    toc_title: str
    add_generator_tag: bool


class EPUBCreator:
    def __init__(self, **options: Unpack[EPUBCreationOptions]) -> None:
        self.language: str = options.get("language", "")
        self.book_title: str = options.get("book_title", "")
        self.unique_identifier: str = options.get("unique_identifier", "bookid")
        self.package_document_path: str = options.get(
            "package_document_path",
            "content.opf",
        )
        self.navigation_document_path: str = options.get(
            "navigation_document_path", "Text/nav.xhtml"
        )
        self.navigation_document_title: str = options.get(
            "navigation_document_title",
            "",
        )
        self.toc_title: str = options.get(
            "toc_title",
            "",
        )
        self.add_generator_tag: bool = options.get(
            "add_generator_tag",
            True,
        )

        if not self.package_document_path:
            raise EPUBCreationError("Package document path cannot be empty")

        if not self.package_document_path.endswith(".opf"):
            raise EPUBCreationError("Package document path must end with .opf")

        if not self.navigation_document_path:
            raise EPUBCreationError("Navigation document path cannot be empty")

        if not self.navigation_document_path.endswith(".xhtml"):
            raise EPUBCreationError("Navigation document path must end with .xhtml")

    def new_container_file(self) -> str:
        return container_xml.format(package_document_path=self.package_document_path)

    def new_package_document(self) -> bytes:
        content = package_document_skeleton.format(
            unique_identifier=self.unique_identifier
        )

        resource = PackageDocument(content.encode(), self.package_document_path)

        resource.metadata.identifier = ""
        resource.metadata["identifier"].tag["id"] = self.unique_identifier

        resource.metadata.title = self.book_title
        resource.metadata.language = self.language
        resource.metadata.modified = datetime.now()

        if self.add_generator_tag:
            version = get_epublib_version()
            __ = resource.metadata.add_opf("generator", "Created with epublib")
            if version:
                __ = resource.metadata.add_opf("epublib version", version)

        item = resource.manifest.add_item(
            ManifestItem(
                soup=resource.soup,
                filename=self.navigation_document_path,
                id=EPUBId("nav"),
                media_type=MediaType.XHTML.value,
                properties=["nav"],
                own_filename=self.package_document_path,
            )
        )
        __ = resource.spine.add_item(SpineItemRef(soup=resource.soup, idref=item.id))

        return resource.content

    def new_navigation_document(self) -> str:
        return navigation_document_skeleton.format(
            title=self.navigation_document_title,
            toc_title=self.toc_title,
            language=self.language,
        )

    def to_file(self) -> io.BytesIO:
        file = io.BytesIO()
        with zipfile.ZipFile(file, "w") as zf:
            zf.writestr("mimetype", mimetype)
            zf.writestr("META-INF/container.xml", self.new_container_file())
            zf.writestr(self.package_document_path, self.new_package_document())
            zf.writestr(self.navigation_document_path, self.new_navigation_document())

        __ = file.seek(0)
        return file

    def to_bytes(self) -> bytes:
        return self.to_file().getvalue()
