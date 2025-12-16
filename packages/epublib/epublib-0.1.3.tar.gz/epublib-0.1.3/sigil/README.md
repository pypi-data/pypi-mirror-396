# Using EPUBLib within a Sigil plugin

Using EPUBLib from [Sigil](https://sigil-ebook.com) requires some
installation of Python >= 3.13, which is much more recent than the
default one bundled with Sigil. In Sigil's plugin management window
(`Plugins` -> `Manage plugins`) there is an option to specify the path
to the python interpreter executable (you may need to specify a path to
a virtual environment with EPUBLib installed).

If you are unable to do that (e.g. if other plugins in use require the
python executable bundled with Sigil), you can use something like the
example provided here. It may also be useful if you want the plugin to
manage it's own virtual environment.

## What this example does

This plugin will search for a suitable python interpreter in the user's
system, create a virtual environment with it, and install the packages
listed in the `requirements.txt` file (if absent, will only install
EPUBLib). It then proceeds to call another script (called `entrypoint.py`
in this example) with the plugin's origin and destination folders as
arguments. This script will be able to to the heavy lifting with
EPUBLib.

## Using the example

If you have `make` simply `cd` into this folder and do `$ make` (or `$ make
sigil_plugin` from the parent folder). This will generate a zip file.

If not, compress the folder `epublibexample` into a `epublibexample.zip`
file. If you wish to change the name of this file, you will also need to
rename the folder and adjust the plugin name in `plugin.xml`. Note that
the name of the plugin (and hence the name of the file/folder) cannot
have spaces or underscores (see "Anatomy of a plugin" in [Sigil Support
for Plugins](https://sigil-ebook.com/plugin-api-guide/index2.html?epub=epub_content%2Fguide&goto=epubcfi(/6/4!/4/2/1:0))).

Then, add this zip to Sigil (`Plugins` -> `Manage plugins` -> `Add plugin`).

## Compatibility

This example was tested with:

* Debian 13 with Sigil 2.4.2
* Windows ? with Sigil ?
* Mac ? with Sigil ?
