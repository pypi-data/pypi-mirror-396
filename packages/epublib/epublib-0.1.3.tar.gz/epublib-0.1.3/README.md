# EPUBLib

A spec compliant, memory efficient EPUB3 library. Designed for editing
EPUBs, but can also create them.

* Spec compliant: code aims at being compliant with the
[EPUB 3.3 specification](https://www.w3.org/TR/epub-33/) (although it
does not attempt to validate the EPUB. Use
[Ace by Daisy](https://daisy.org/activities/software/ace/) and
[EPUBCheck](https://www.w3.org/publishing/epubcheck/) for that);
* Memory efficient: leverages python standard library's zipfile module to
  load data into memory as needed only;
* Designed for editing: handles EPUBs non intrusively (e.g. won't
  recreate the manifest and the metadata).

## Installation

```bash
pip install epublib
```

### Dependencies

Installing EPUBLib will also install its dependencies:

* BeautifulSoup (`pip install beautifulsoup`)
* lxml (`pip install lxml`)

## Contributing

1. Clone from
   [gitlab.com/joaoseckler/epublib](https://gitlab.com/joaoseckler/epublib).
2. Use [`uv`](https://docs.astral.sh/uv/) to manage development dependencies.
   Sync with `uv sync --all-packages`
3. `pre-commit install`
4. Use `basedpyright` to type check your contribution. There is currently no
   pre-commit rule for it, but contributions are expected not to introduce any
   type checking errors or warnings.

## Related

* [Ebooklib](https://github.com/aerkalov/ebooklib)
* [Sigil](https://sigil-ebook.com/)

## Usage

### Basic usage

```python
from epublib import EPUB

with EPUB("book.epub") as book:
    book.metadata.title = "New title"

    for doc in book.documents:
        new_script = doc.soup.new_tag("script", attrs={"src": "../Misc/myscript.js"})
        doc.soup.head.append(new_script)

        new_heading = doc.soup.new_tag("h1", string="New heading")
        doc.soup.body.insert(0, new_heading)

    book.update_manifest_properties()
    book.write("book-modified.epub")
```

### Reading, writing and creating

```python
from epublib import EPUB

# From path
with EPUB("book.epub") as book:
    book.write("book-modified.epub")

# From file
with open("book.epub", "rb") as read_file:
    with EPUB(read_file) as book, open("book-modified.epub", "wb") as f:
            book.write(f)

# Read from folder path (unzipped EPUB)
with EPUB("book-folder/") as book:
    book.write_to_folder("book-folder-modified/")

# Create new EPUB
with EPUB() as book:
    book.metadata.title = "A new book"
    book.metadata.identifier = "urn:uuid:123e4567-e89b-12d3-a456-426614174000"
    book.metadata.language = "en"
    book.nav.soup.title.string = "Navigation title"

    # the default TOC comes with one single self referential item
    book.nav.toc.text = "Toc title" # Title of the toc
    item_referencing_toc = next(book.nav.toc.items_referencing(book.nav.filename))
    item_referencing_toc.text = "Toc title"
```

EPUBLib does not guarantee the validity of the EPUB resulting from
calling `EPUB()`. It is the user's responsability to add, at least:

* a title (`book.metadata.title = <title>`)
* an identifier (`book.metadata.identifier = <id>`)
* a language (`book.metadata.language = <language>`)
* A title for the navigation document (`book.nav.soup.title.string = <title>`)
* A title for the elements of the table of contents (see example above
  for one way of doing it)

### Accessing resources

Each resource corresponds to a file in the EPUB archive.

```python
import zipfile

from epublib import EPUB
from epublib.media_type import MediaType, Category

with EPUB("book.epub") as book:
    book.resources #  all resources
    print([resource.filename for resource in book.resources])
    # [
    #     "mimetype",
    #     "META-INF/container.xml",
    #     "content.opf",
    #     "Text/chapter1.xhtml",
    #     "Images/image.png",
    #     ...,
    # ]

    resource = book.resources.get("Text/chapter1.xhtml")

    assert resource.filename == "Text/chapter1.xhtml"
    assert isinstance(resource.content, bytes)
    assert isinstance(resource.zipinfo, zipfile.ZipInfo)

    documents = book.documents # All XHTML and SVG resources
    images = book.images # All image resources
    scripts = book.scripts # All JavaScript resources
    styles = book.styles # All style resources

    assert book.resources.get("Text/chapter1.xhtml") # ContentDocument(Text/chapter1.xhtml)
    assert book.documents.get("Text/chapter1.xhtml") is book.resources.get("Text/chapter1.xhtml")
    assert book.images.get("Text/chapter1.xhtml") is None
    assert book.resources.get("Images/image.png") # PublicationResource(Images/image.png)

    pngs = book.resources.filter(MediaType.IMAGE_PNG) # All PNG images
    assert all(img.media_type is MediaType.IMAGE_PNG for img in pngs)

    images = book.resources.filter(Category.IMAGE) # All images. Same as book.images()
    assert all(img.media_type.category is Category.IMAGE for img in images)
```

#### Creating

```python
from epublib import EPUB
from epublib.identifier import EPUBId
from epublib.resources import PublicationResource, ContentDocument
from epublib.resources.create import create_resource_from_path, create_resource

with EPUB("book.epub") as book:
    # Create a new resource from filesystem path
    new_resource = create_resource_from_path("new-image.jpg", "Images/name-in-epub.jpg")
    assert isinstance(new_resource, PublicationResource)
    book.resources.add(resource=new_resource)

    # Create a new resource from content

    xhtml = """
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE html>
    <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
    <head>
      <title>A Small Document</title>
    </head>
    <body>
      <p>A simple page!</p>
    </body>
    </html>
    """

    new_resource = create_resource(xhtml.encode(), "Text/Chapter4.xhtml")
    assert isinstance(new_resource, ContentDocument)
    book.resources.add(resource=new_resource)

    # More options when adding are available (see full signature in the API
    # documentation)
    new_resource = create_resource(xhtml.encode(), "Text/Chapter5.xhtml")
    book.resources.add(
        resource=new_resource,
        is_cover = False,
        position = 0, # position in book.resources list
                      # (and thus in archive). Default: None
        after = "Text/Chapter1.xhtml", # insert after this resource, default: None
        before = None,                 # insert before this resource

        # if None, it will be added unless it is the mimetype or the container.xml
        # file. caution: setting this to False or True may yield invalid EPUBs
        add_to_manifest = None,

        add_to_spine = None,
        spine_position = None,
        linear = None,
        add_to_toc = None,
        toc_position = None,
    )
```

#### Removing

```python
from epublib import EPUB
from epublib.identifier import EPUBId

with EPUB("book.epub") as book:
    resource = book.resources.get("Text/chapter1.xhtml")
    book.resources.remove(resource)

    # It is possible to use the filename directly
    book.resources.remove("Images/image.png")

    # or the manifest item id
    book.resources.remove(EPUBId("image2"))

    # If it is a CSS or JS file, you can set the remove_css_js_links flag
    # To remove any <link rel="stylesheet"> or <script> tags pointing to it
    book.resources.remove("Styles/style.css", remove_css_js_links=True)

    # If it has any other type, you'll have to individually remove any
    # references to it
```

#### Renaming

```python
from epublib import EPUB
from epublib.identifier import EPUBId

with EPUB("book.epub") as book:
    resource = book.resources.get("Text/chapter1.xhtml")
    book.resources.rename(resource, "Text/chapter-one.xhtml")

    # The same can be achieved by
    book.resources.rename("Text/chapter-one.xhtml", "Text/chapter1.xhtml")

    # or
    book.resources.rename(EPUBId("chapter1"), "Text/chapter-one.xhtml")
```

By default, renaming a resource will update all references to it in the
rest of the book -- namely, in every `XMLResource` (see
[below](#internal-representation)). If you want to rename
a resource without updating references to it, you can set the
`update_references` flag to `False`:

```python
from epublib import EPUB

with EPUB("book.epub") as book:
    book.resources.rename(
        "Text/chapter1.xhtml",
        "Text/chapter-one.xhtml",
        update_references=False,
    )
```

By default, these references are looked up by using the following XML
attributes: `["href", "src", "full-path", "xlink:href"]`. If you want to
use a different set of attributes, you can pass them as a list to the
`reference_attrs` parameter:

```python
from epublib import EPUB

with EPUB("book.epub") as book:
    book.resources.rename(
        "Text/chapter1.xhtml",
        "Text/chapter-one.xhtml",
        reference_attrs=["data-src", "href"],
    )
```

#### Internal representation

Resources are represented by instances of `epublib.resources.Resource`
or one of its subclasses, depending on the type of resource:

* `Resource`: generic resource. Usually, the only file in the EPUB that is
  represented by a generic Resource is
  [the `mimetype` file](https://www.w3.org/TR/epub-33/#sec-zip-container-mime);

* `XMLResource`: XML resources (XHTML, SVG, XML). Provides a `soup`
  attribute representing the content as a BeautifulSoup object.
  Subclasses `Resource`;

* `PublicationResource`: A resource that contributes to the logic and
  rendering of the publication. This includes CSS files, fonts, images,
  JavaScript files, XHTML and SVG (although the last two have their own
  specific subclass: see below). All publication resources should have a
  manifest entry associated to them. Provides a `media_type: MediaType`
  (more on media types [below](#media-types)). Subclasses `Resource`;

* `ContentDocument`: A XHTML or SVG document. Subclasses `XMLResource` and
  `PublicationResource`;

* `PackageDocument`: The package document (content.opf). Subclasses
  `XMLResource`. More about the package document [below](#the-package-document);

* `NavigationDocument`: A XHTML or SVG document that represents the
  navigation document of the EPUB (the one with `properties="nav"` in
  the manifest). Subclasses `ContentDocument`. More about the navigation
  document [below](#navigation-document).

* `NCXFile`: A XML document that represents the NCX file of the EPUB
  (if it exists). Subclasses `PublicationResource` and `XMLResource`. More
  about the NCX file [below](#ncx-file).

The class hierarchy is as follows:

```text
                     ┌────────┐
                ┌────│Resource│───────┐
                │    └────────┘       │
                │                     │
                │                     │
                │                     │
           ┌────▼──────┐    ┌───────────────────┐
      ┌────│XMLResource│──┬─│PublicationResource│
      │    └───────────┘  │ └───────────────────┘
      │                   │
      │                   ├─────────────┐
      │                   │             │
┌─────▼─────────┐ ┌───────▼───────┐ ┌───▼───┐
│PackageDocument│ │ContentDocument│ │NCXFile│
└───────────────┘ └───────────────┘ └───────┘
                         │
                         │
                 ┌───────▼──────────┐
                 │NavigationDocument│
                 └──────────────────┘
```

### The package document

The package document (sometimes referred to as OPF or `content.opf`) is
"an XML document that consists of a set of elements that each
encapsulate information about a particular aspect of an EPUB
publication" (from [the spec](https://www.w3.org/TR/epub-33/#sec-package-intro)).
It contains:

* Metadata: title, author, language, date, etc;
* Manifest: list of all resources in the EPUB;
* Spine: reading order of resources;
* Collections (optional): groupings of resources;
* Manifest fallback chains (optional): define equivalence of resources
  to be used as fallbacks.

EPUBLib has specific features for handling the first three elements.
Further reading  at the [spec section about the package
document](https://www.w3.org/TR/epub-33/#sec-package-doc). The package
document itself is a resource from the epub and is available at
`book.package_document`.

#### Metadata

```python
from datetime import datetime
from epublib import EPUB

with EPUB("book.epub") as book:
    print(book.metadata) # BookMetadata(10 items)

    # book.metadata is an alias of book.package_document.metadata
    assert book.metadata is book.package_document.metadata

    # Mandatory metadata fields are available as attributes of convenient types
    assert isinstance(book.metadata.title, str)
    assert isinstance(book.metadata.language, str)
    assert isinstance(book.metadata.modified, datetime)
    book.metadata.title = "New title"
    book.metadata.modified = datetime.now()

    # Access as item (read-only) yields internal representation
    print(book.metadata["title"])
    # DublinCoreMetadataItem(
    #     name='title',
    #     tag=<dc:title>New title</dc:title>,
    #     value='New title',
    #     id=None,
    #     dir=None,
    #     lang=None
    # )

```

##### Adding metadata

```python
from epublib import EPUB
from epublib.package.metadata import (
    GenericMetadataItem,
    DublinCoreMetadataItem,
)

with EPUB("book.epub") as book:
    new_item = book.metadata.add("pageBreakSource", "Our print version, 1976")
    new_item_dc = book.metadata.add_dc("rights", "© 1976 Our Publisher")

    assert isinstance(new_item, GenericMetadataItem)
    assert isinstance(new_item_dc, DublinCoreMetadataItem)

    print(new_item)
    # GenericMetadataItem(name='pageBreakSource',
    #     tag=<meta property="pageBreakSource">Our print version,
    #     1976</meta>,
    #     value='Our print version,
    #     1976',
    #     id=None,
    #     dir=None,
    #     lang=None,
    #     refines=None,
    #     scheme=None
    # )

    print(new_item_dc)
    # DublinCoreMetadataItem(
    #     name='rights',
    #     tag=<dc:rights>© 1976 Our Publisher</dc:rights>,
    #     value='© 1976 Our Publisher',
    #     id=None,
    #     dir=None,
    #     lang=None
    # )
```

##### Adding other types of metadata

```python
from epublib import EPUB
from epublib.package.metadata import MetadataItem, LinkMetadataItem

with EPUB("book.epub") as book:
    link_item = LinkMetadataItem(
        soup=book.package_document.soup,
        href="front.xhtml#meta-json",
        rel="record",
        media_type="application/xhtml+xml",
        hreflang="en",
    )
    book.metadata.add_item(link_item)

    # You can also create your own custom metadata items by subclassing MetadataItem
    from custom_item import create_some_custom_item

    custom_item = create_some_custom_item()
    assert isinstance(custom_item, MetadataItem)
    book.metadata.add_item(custom_item)
```

##### Getting all metadata

```python
from epublib import EPUB

with EPUB("book.epub") as book:
    book.metadata.items # Each item in internal representation
    book.metadata.tag # The full metadata tag as an bs4.Tag element
```

#### Manifest

From the [spec](https://www.w3.org/TR/epub-33/#sec-manifest-elem), the
manifest "provides an exhaustive list of publication resources used
in the rendering of the content." Each of its items needs to have:

* an href, a relative path to the resource in the archive;
* a media-type (see [media types](#media-types) below);
* a unique identifier;

and can optionally have:

* properties (see [manifest properties](#manifest-properties) below);
* a fallback;
* a media-overlay.

The manifest is internally represented by `BookManifest`, and each item
by `ManifestItem`. Instead of the relative path, we primarily use the
absolute path of each resource to identify it in the EPUB (corresponding
to the `href` and `filename` attributes of `ManifestItem`,
respectivelly). If you whish to use the identifier instead, you can
signal that by using `EPUBId`, a `str` subclass, to wrap the identifier
string.

```python
from epublib import EPUB
from epublib.package.manifest import BookManifest, ManifestItem
from epublib.identifier import EPUBId

with EPUB("book.epub") as book:
    # book.manifest is an alias of book.package_document.manifest
    assert book.manifest is book.package_document.manifest

    print(book.manifest) # BookManifest(4 items)
    assert all(isinstance(item, ManifestItem) for item in book.manifest.items)

    # Get manifest item by filename (absolute path). Raise KeyError if not found
    item = book.manifest["Text/chapter1.xhtml"]
    assert item

    # Get manifest item, return None if not found
    item = book.manifest.get("Text/chapter99.xhtml")
    assert item is None

    # Get manifest item by identifier (EPUBId)
    nav_item = book.manifest[EPUBId("nav")]
    assert nav_item
```

Adding and removing manifest items are normally done when adding or
removing resources (see [above](#accessing-resources)), which is done
under the hood by `EPUB.resources`. If you need custom control of
manifest items regardless of their resource counterparts, you can use
the `add_item`, `insert_item` and `remove_item` methods of
`BookManifest`. Caution is advised, as this may result in invalid EPUBs.

##### Manifest properties

Each manifest item can have a set of properties, which convey additional
information about the resource (read more [in the
spec](https://www.w3.org/TR/epub-33/#sec-item-resource-properties)). A
non-exhaustive list of properties follows:

* nav (mandatory and unique, sets the navigation document)
* cover-image
* [mathml](https://www.w3.org/TR/epub-33/#sec-mathml)
* [remote-resources](https://www.w3.org/TR/epub-33/#sec-remote-resources)
* [scripted](https://www.w3.org/TR/epub-33/#sec-scripted)
* [svg](https://www.w3.org/TR/epub-33/#sec-svg)
* [switch](https://www.w3.org/TR/epub-33/#sec-switch)

```python
from epublib import EPUB
from epublib.identifier import EPUBId

with EPUB("book.epub") as book:
    item = book.manifest.get("Text/chapter1.xhtml")

    # Only do this if there are external links in chapter 1
    item.add_property("remote-resources")
    # Only do this if there are math expressions in chapter 1
    item.add_property("mathml")

    item.remove_property("remote-resources")

    assert item.has_property("mathml")
    assert not item.has_property("remote-resources")

    # There are shortcuts to the nav item and the cover image item.
    assert book.manifest.nav is book.manifest[EPUBId("nav")]

    # Get the manifest item corresponding to the cover image. Currently,
    # there is no cover.
    assert book.manifest.cover_image is None

    # Promote some image to cover image
    book.resources.set_cover_image("Images/image.png")

    assert book.manifest.cover_image is book.manifest["Images/image.png"]
    assert book.resources.cover_image is book.resources["Images/image.png"]
```

#### Spine

The spine defines the default reading order of the publication. Each
spine item conveys the following information:

* idref (required): the identifier of the corresponding manifest item;
* linear: whether the item is part of the default reading order or not;
* properties (optional): additional information about the item;
* id: an identifier for the spine item itself.

Only the first one is mandatory. The spine is internally represented by
`BookSpine` (found at `book.spine`, an alias of
`book.package_document.spine`), and each item by `SpineItemRef`.
Different than manifest items, spine items are primarily identified by
their `idref` (their only required attribute).

```python
from epublib import EPUB
import random

with EPUB("book.epub") as book:
    print(book.spine) # BookSpine(2 items)

    assert book.spine["nav"]
    assert book.spine["chapter1"]

    # Getting spine item by position
    assert book.spine[0] is book.spine["chapter1"]

    # If you need to get a spine item by its filename, go through the
    # manifest first (since the filename information is not stored in the spine):
    item = book.spine[book.manifest["Text/chapter1.xhtml"].id]

    # To reorder the spine, you can use the move_item method:
    book.spine.move_item("nav", 0) # Move nav to the beginning of the spine
    assert book.spine[0].idref == "nav"

    # Or completely reorder the spine
    new_order = list(book.spine.items)
    random.shuffle(new_order)

    book.spine.reorder(new_order)
    assert list(book.spine.items) == new_order
```

As with the manifest, adding and removing spine items are normally done
when adding or removing resources (see [above](#accessing-resources)).
Refer to the following parameters of the `EPUB.resources.add` method:

* `after` and `before`;
* `add_to_spine`;
* `spine_position`;
* `linear`.

If you need custom control of spine items the `add_item`, `insert_item`
and `remove_item` methods of `BookSpine`. Caution is advised, as this
may result in invalid EPUBs.

### Navigation document

The navigation document is a special XHTML document that contains
"human- and machine-readable global navigation information." (from [the
spec](https://www.w3.org/TR/epub-33/#dfn-epub-navigation-document)). In
other words, it is a regular XHTML file with some extra requirements:

* Must include exactly one `nav` html element with `epub:type="toc"`
  (the table of contents);
* All `nav` html elements with a `epub:type` attribute, including the
  table of contents, must follow a [specific
  structure](https://www.w3.org/TR/epub-33/#sec-nav-def-model), using
  only ordered lists (`ol`, possibly nested), list items (`li`), spans
  (`span`) and anchors (`a`);

There may also exist other `nav` elements with different `epub:type`
attributes. The spec talks about two other types:

* `page-list`: a list of links to the locations in the publication
  that correspond to page numbers in a print edition of the work;
* `landmarks`: a list of links to important locations in the
  publication, such as the title page, table of contents, main
  content, bibliography, etc.

This requirements allow EPUBLib to provide specific features for
handling the navigation document, which is represented by
a `NavigationDocument` resource, available at `book.nav`.
There are features for handling the table of contents, page list and
landmarks.

```python
from epublib import EPUB
from epublib.resources import ContentDocument

with EPUB("book.epub") as book:
    # Table of contents
    book.reset_toc(
        targets_selector = "h1, h2, h3",  # defaults to all headings, in which case
                                          # a nested toc is created
        include_filenames = False,        # Whether to include filenames in TOC entries
                                          # (i.e. hrefs with no fragments)
        spine_only = True,                # Only read from resources in the spine
                                          # (yields correctly orderered TOC)
        resource_class = ContentDocument, # Only consider resources of this class
        title="Table of contents",        # Title of the TOC
    )

    # Landmarks
    book.create_landmarks(
        include_toc = True,                          # Include TOC in landmarks
        targets_selector = "#landmark1, #landmark2", # Defaults to None,
                                                     # selecting no landmark
    )

    # This will error if a landmarks list already exists. Use the following
    # to force recreation
    book.reset_landmarks()


    # Page list
    book.create_page_list(
        id_format = "page_{page}", # If a page breaks is identified but has
                                   # no id, use this format to attribute one
        label_format = "{page}",   # Format for page label, shown in the page list
        pagebreak_selector = '[role="doc-pagebreak"], [epub|type="pagebreak"]',
    )

    # This will error if a toc already exists. Use the following to force recreation
    book.reset_page_list()
```

### NCX file

The NCX file is an XML file used in EPUB 2 publications to define the
table of contents. It has been superseded by the [navigation
document](#navigation-document), but may optionally be included in EPUB
3 publications for backwards compatibility with EPUB 2 readers. There
are several features of the NCX format, only part of which are
represented in EPUBLib:

* `head` element contains metadata, some of which are required (`uid`,
  `depth`, `totalPageCount`, `maxPageNumber`);
* `docTitle` element contains the title of the publication;
* `docAuthor` elements contain the authors of the publication;
* `navMap` element contains the actual table of contents;
* `pageList` element contains the list of pages.
* `navList` elements (any number of them) can contains other lists of
  points of interest.

Currentrly, epublib does not handle any features of the NCX related to
SMIL and doesn't not handle audio and image tags inside `navPoint`s or
`pageTarget`'s.

Refer to the
[specification](https://daisy.org/activities/standards/daisy/daisy-3/z39-86-2005-r2012-specifications-for-the-digital-talking-book/#NCX)
for more details.

```python
from epublib import EPUB
from epublib.ncx import NCXHead, NCXNavMap, NCXPageList

with EPUB("book.epub") as book:
    book.generate_ncx() # use reset_ncx if one already exists
    assert book.ncx
    assert book.ncx.nav_map
    assert book.ncx.head


    assert isinstance(book.ncx.head, NCXHead)
    assert isinstance(book.ncx.nav_map, NCXNavMap)
    assert book.ncx.page_list is None # No page list yet!

    item = book.ncx.nav_map.items[0]

    assert item.href == "Text/chapter1.xhtml"
    assert item.text == "Start"

    # Will recreate the nav_map unless reset_ncx is False or there is no NCX file
    book.reset_toc(reset_ncx=True)

    # Will recreate the page_list unless reset_ncx is False or there is no NCX file
    book.reset_page_list(reset_ncx=True)
    assert isinstance(book.ncx.page_list, NCXPageList)


    # To synchronize specific parts of the NCX file with the rest of the book:
    book.ncx.sync_head(book.metadata)
    book.ncx.sync_toc(book.nav)
    book.ncx.sync_page_list(book.nav)

    # Update metadata numbers in the head of the NCX which are calculated
    # (depth, total page count, max page number and play order)
    book.ncx.update_numbers()

    # Use reset_ncx to do all of the above at once
    book.reset_ncx()
```

### Soup and internal representations

> tl;dr: If possible, do not alter the `soup` attribute of
> `PackageDocument`, `NavigationDocument` or `NCXFile` directly. If you
> do need to alter them, make sure to call
> `book.package_document.on_soup_change()` or
> `book.nav.on_soup_change()` and `book.ncx.on_soup_change()`
> afterwards.

The features described above for handling the package document, the
navigation document and the NCX file involve parsing the corresponding
XML/XHTML files and building a internal representation of their content.
These representations are built lazily (i.e., the parsing only occurs
when some of the representation is accessed). Due to the mutable nature
of BeautifulSoup objects, the user may inadvertently introduce
discrepancies between them and the internal representation, which may
lead to errors. For example, if a user adds an item tag directly to the
soup of the package document, there is no way for EPUBLib to know about
the new item and add it to the `BookManifest` object.

If you do need to alter the `soup` attribute of these resources (or the
`tag` attributes of the internal representations), there may be two
scenarios:

1. You don't need the internal representation, so we're all good.

    ```python
    from epublib import EPUB

    with EPUB("book.epub") as book:
        new_tag = book.package_document.soup.new_tag(
            "item",
            attrs={"href": "file.txt", "media-type": "text/plain", "id": "file"},
        )
        book.manifest.tag.append(new_tag)
        book.write("book-modified.epub") # All good
    ```

2. You do need the internal representation. In this case, you need to call
   the `on_soup_change` method of the corresponding resource after
   altering its soup.

    ```python
    from epublib import EPUB

    with EPUB("book.epub") as book:
        new_tag = book.package_document.soup.new_tag(
            "item",
            attrs={"href": "file.txt", "media-type": "text/plain", "id": "file"},
        )
        book.package_document.soup.manifest.append(new_tag)

        # Mark the internal representation for reparsing
        book.package_document.on_soup_change()

        # Internal representation is up to date
        assert book.manifest.get("file.txt")
    ```

Note that the internal representation reflect its changes to the soup,
so you don't need to do anything to see the changes there.

```python
from epublib import EPUB
from epublib.resources.create import create_resource

with EPUB("book.epub") as book:
    book.resources.add_to_manifest(
        create_resource(b"Some text content", "Text/file.txt"),
        identifier="new-item"
    )

    assert book.package_document.soup.find(id="new-item")
```

If you completely overwrite the `soup` attribute of these resources,
there is also no need to call `on_soup_change`, as the property setter
will already do that for you. This is why there is no similar issue
with the `contents` attribute: since bytes are immutable, every change
to it will trigger a reparse from the property setter.

### Media types

Media types (also known as MIME types or content types) are strings that
represent the format of a file. They are used in EPUBs to describe the
format of each resource, and are required in every manifest item.

EPUBLib provides a `MediaType` class that represents media types, both
core and foreign.

We also introduce a helper class called `Category`, which represents the
main category of a media type. For example, the media type
`image/png` (`MediaType.IMAGE_PNG`) has the category `Category.IMAGE`.

```python
from epublib.media_type import MediaType, Category

# From filename
assert MediaType.from_filename("image.png") is MediaType.IMAGE_PNG
assert MediaType.from_filename("image.jpg") is MediaType.IMAGE_JPEG
assert MediaType.from_filename("audio.ogg") is MediaType.AUDIO_OGG

# From mimetype string
assert MediaType("font/ttf") is MediaType.FONT_TTF
assert MediaType("text/css") is MediaType.CSS

# Utilities
assert MediaType.from_filename("script.js").is_js()
assert MediaType.from_filename("style.css").is_css()

# The category and mimetype are available as a properties in MediaType instances
media_type = MediaType.from_filename("image.png")
assert media_type.category is Category.IMAGE
assert media_type.value == "image/png"
```

The `MediaType` is a "flexible" enum, meaning you can instantiate it
with any string value. This implementation comes from the non
restrictive nature of the spec regargind media types. Any valid mime
type is allowed, even if not listed as one the ["core media
types"](https://www.w3.org/TR/epub-33/#sec-core-media-types). In this
case, the resource in question is called a foreign resource.

```python
from epublib.media_type import MediaType, Category

media_type = MediaType("application/x-zerosize")
assert media_type.value == "application/x-zerosize"
assert media_type.category is Category.FOREIGN
assert media_type == MediaType("application/x-zerosize")

media_type = MediaType.from_filename("file.jar")
assert media_type.value == "application/java-archive"
assert media_type.category == Category.FOREIGN
```

### Utilities

#### Relative path resolution

When dealing with EPUBs it is often necessary to, given a relative path
(e.g. in an `href` or `src` attribute), find the full path of the
referred file. The other way around may also be necessary: given the
absolute filename, find the relative path from some resource to that
filename. Two helper functions are provided for this:

```python
from epublib.util import get_absolute_href, get_relative_href
from epublib import EPUB

with EPUB("book.epub") as book:
    href = book.nav.soup.select_one("a")["href"] # "chapter1.xhtml"
    absolute_path = get_absolute_href(
        origin_href=book.nav.filename, # "Text/nav.xhtml"
        href=href,                     # "chapter1.xhtml"
    )

    assert absolute_path == "Text/chapter1.xhtml"

    # Vice versa:
    relative_path = get_relative_href(
        relative_to=book.nav.filename, # "Text/nav.xhtml"
        absolute_href="Text/chapter1.xhtml",
    )

    assert relative_path == "chapter1.xhtml"
```

At a higher level, the `EPUB.resources` provides a method for resolving a
string representing an href (possibly with a fragment) to the actual
resource it refers to (and optionally to the tag is refers to):
`resolve_href`.

```python
import bs4
from epublib import EPUB

with EPUB("book.epub") as book:
    resource = book.resources.resolve_href("Text/chapter1.xhtml#section1", with_tag=False)
    assert resource is book.resources.get("Text/chapter1.xhtml")

    # If the href is found inside some resource, you can use the
    # `relative_to` parameter
    resource = book.resources.resolve_href(
        "../Text/chapter1.xhtml#section1",
        with_tag=False,
        relative_to="Styles/style.css",
    )
    assert resource is book.resources.get("Text/chapter1.xhtml")

    # To capture the tag the href refers to, use the `with_tag` parameter:
    resource, tag = book.resources.resolve_href(
        "../Text/nav.xhtml#toc",
        with_tag=True,
        relative_to="Styles/style.css",
    )
    assert resource.filename == "Text/nav.xhtml"
    assert isinstance(tag, bs4.Tag)
    assert tag["id"] == "toc"
```
