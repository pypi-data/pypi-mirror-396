# Configuration file for the Sphinx documentation builder.

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../src"))
from sphinx_pyproject import SphinxConfig

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# https://github.com/sphinx-toolbox/sphinx-pyproject
config = SphinxConfig("../../pyproject.toml", globalns=globals())
project = "EPUBLib"
year = "2025"
if datetime.now().year > 2025:
    year = f"2025 - {datetime.now().year}"
copyright = f"{year} João Seckler"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration


extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "myst_parser",
    "sphinxext.opengraph",
    "sphinx_copybutton",
]

html_theme = "furo"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ["_static"]
html_favicon = "_static/favicon.svg"

myst_heading_anchors = 5
maximum_signature_line_length = 72
autodoc_member_order = "bysource"
add_module_names = False

html_theme_options = {
    "navigation_with_keys": True,
}
