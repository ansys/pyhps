# Sphinx documentation configuration file
from datetime import datetime
import os
import sys

from ansys_sphinx_theme import pyansys_logo_black as logo

from ansys.rep.client import __company__, __external_version__, __version__, __version_no_dots__

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# -- Project information -----------------------------------------------------

# General information about the project.
project = "Ansys pyrep"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = __company__

# The short X.Y version
release = version = __version__

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.extlinks",
    # "sphinx.ext.viewcode", # to show pytho source code
    "sphinxcontrib.httpdomain",
    "sphinxcontrib.globalsubs",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinxnotes.strike",
]


# autodoc/autosummary flags
autoclass_content = "both"
# autodoc_default_flags = ["members"]
autosummary_generate = True


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# Allow markdown includes (so releases.md can include CHANGLEOG.md)
# http://www.sphinx-doc.org/en/master/markdown.html
# source_parsers = {".md": "recommonmark.parser.CommonMarkParser"}

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = [".rst"]
# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = "en"

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False


# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

html_theme = "ansys_sphinx_theme"

# only for  sphinx_rtd_theme
html_theme_options = {
    "github_url": "https://github.com/pyansys/pyrep",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "collapse_navigation": True,
    "navigation_depth": 4,
}

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = html_title = "PyREP"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = logo

# Favicon
html_favicon = "favicon.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# Output file base name for HTML help builder.
htmlhelp_basename = "pyrepdoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "ansys-rep-client.tex",
        "REP Python Client Documentation",
        author,
        "manual",
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ("index", "ansys-rep-client", "REP Python Client Documentation", ["ANSYS Switzerland Gmbh"], 1)
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "ansys-rep-client",
        "REP Python Client Documentation",
        "ANSYS Switzerland Gmbh",
        "DCP",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

global_substitutions = {
    "client_version": __version__,
    "version_no_dots": __version_no_dots__,
    "external_version": __external_version__,
}

# numpydoc configuration
numpydoc_show_class_members = False
numpydoc_xref_param_type = True

# Consider enabling numpydoc validation. See:
# https://numpydoc.readthedocs.io/en/latest/validation.html#
numpydoc_validate = True
numpydoc_validation_checks = {
    "GL06",  # Found unknown section
    "GL07",  # Sections are in the wrong order.
    "GL08",  # The object does not have a docstring
    "GL09",  # Deprecation warning should precede extended summary
    "GL10",  # reST directives {directives} must be followed by two colons
    "SS01",  # No summary found
    "SS02",  # Summary does not start with a capital letter
    # "SS03", # Summary does not end with a period
    "SS04",  # Summary contains heading whitespaces
    # "SS05", # Summary must start with infinitive verb, not third person
    "RT02",  # The first line of the Returns section should contain only the
    # type, unless multiple values are being returned"
}

extlinks = {
    "ansys_rep_help": (
        """https://ansyshelp.ansys.com/account/
        secured?returnurl=/Views/Secured/corp/v231/en/rep_ug/%s.html""",
        "ANSYS Help - ",
    ),
    "ansys_dcs_tutorial": (
        """https://ansyshelp.ansys.com/account/
        secured?returnurl=/Views/Secured/corp/v231/en/dcs_tut/%s.html""",
        "REP Tutorial - ",
    ),
}