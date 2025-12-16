import re as re
from pathlib import Path as Path

from bs4 import BeautifulSoup as BeautifulSoup

from epublib import EPUB as EPUB
from epublib.nav.resource import NavigationDocument as NavigationDocument
from epublib.ncx.resource import NCXFile as NCXFile
from epublib.package.manifest import ManifestItem as ManifestItem
from epublib.package.metadata import (
    DublinCoreMetadataItem as DublinCoreMetadataItem,
)
from epublib.package.metadata import GenericMetadataItem as GenericMetadataItem
from epublib.package.metadata import LinkMetadataItem as LinkMetadataItem
from epublib.package.resource import PackageDocument as PackageDocument
from epublib.package.spine import SpineItemRef as SpineItemRef
from epublib.resources import ContentDocument as ContentDocument
from epublib.resources import PublicationResource as PublicationResource
from epublib.resources import Resource as Resource
from epublib.resources import XMLResource as XMLResource
from epublib.resources.create import create_resource as create_resource
from epublib.resources.create import (
    create_resource_from_path as create_resource_from_path,
)
from tests import samples

book = EPUB(samples.epub)
