"""Sphinx documentation configuration file."""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import sphinx
from ansys_sphinx_theme import ansys_favicon, get_version_match, pyansys_logo_black

from ansys.hps.client import __version__

# Constants declaration
EXAMPLES = {
    "mapdl_motorbike_frame": [
        "project_setup.py",
        "project_query.py",
        "exec_mapdl.py",
        "motorbike_frame_results.txt",
        "motorbike_frame.mac",
    ],
    "mapdl_tyre_performance": [
        "project_setup.py",
        "tire_performance_simulation.mac",
        "2d_tire_geometry.iges",
    ],
    "mapdl_linked_analyses": [
        "project_setup.py",
        "prestress.dat",
        "modal.dat",
        "harmonic.dat",
    ],
    "lsdyna_cylinder_plate": [
        "lsdyna_job.py",
        "cylinder_plate.k",
        "postprocess.cfile",
    ],
    "python_two_bar_truss_problem": [
        "project_setup.py",
        "exec_python.py",
        "evaluate.py",
        "input_parameters.json",
    ],
    "fluent_2d_heat_exchanger": [
        "project_setup.py",
        "heat_exchanger.jou",
        "heat_exchanger.cas.h5",
    ],
    "fluent_nozzle": [
        "project_setup.py",
        "solve.jou",
        "nozzle.cas",
    ],
    "cfx_static_mixer": [
        "project_setup.py",
        "exec_cfx.py",
        "runInput.ccl",
        "StaticMixer_001.cfx",
        "StaticMixer_001.def",
    ],
    "python_uv": ["project_setup.py", "exec_script.py", "eval.py"],
    "python_pyansys_cantilever": [
        "project_setup.py",
        "exec_scripts/exec_combined.py",
        "exec_scripts/exec_geometry.py",
        "exec_scripts/exec_mesh.py",
        "exec_scripts/exec_mapdl.py",
        "eval_scripts/eval_combined.py",
        "eval_scripts/eval_geometry.py",
        "eval_scripts/eval_mesh.py",
        "eval_scripts/eval_mapdl.py",
    ],
}

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# -- Project information -----------------------------------------------------

# General information about the project.
project = "Ansys pyhps"
copyright = f"(c) {datetime.now().year} ANSYS, Inc. All rights reserved"
author = "ANSYS Inc."
cname = os.getenv("DOCUMENTATION_CNAME", "hps.docs.pyansys.com")
switcher_version = get_version_match(__version__)
"""The canonical name of the webpage hosting the documentation."""

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
    "sphinx_autodoc_typehints",
    "numpydoc",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_jinja",
]

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.11", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "pyvista": ("https://docs.pyvista.org/version/stable", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
    "pint": ("https://pint.readthedocs.io/en/stable", None),
    "beartype": ("https://beartype.readthedocs.io/en/stable/", None),
    "docker": ("https://docker-py.readthedocs.io/en/stable/", None),
    "pypim": ("https://pypim.docs.pyansys.com/version/stable", None),
    "ansys.hps.client": (f"https://hps.docs.pyansys.com/version/{switcher_version}", None),
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
    # "GL08",  # The object does not have a docstring
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

# autodoc/autosummary flags
autoclass_content = "both"
# autodoc_default_flags = ["members"]
autosummary_generate = True


def prepare_jinja_env(jinja_env) -> None:
    """Customize the jinja env.

    Notes
    -----
    See https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Environment

    """
    jinja_env.globals["project_name"] = project


autoapi_prepare_jinja_env = prepare_jinja_env

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
    "github_url": "https://github.com/ansys/pyhps",
    "show_prev_next": False,
    "show_breadcrumbs": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
    ],
    "collapse_navigation": True,
    "navigation_depth": 5,
    "check_switcher": False,
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
    },
    "navbar_end": ["version-switcher", "theme-switcher", "navbar-icon-links"],
}

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = html_title = "PyHPS"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = pyansys_logo_black

# Favicon
html_favicon = ansys_favicon

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
htmlhelp_basename = "pyhpsdoc"


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
        "ansys-hps-client.tex",
        "Ansys HPS Python Client Documentation",
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
    ("index", "ansys-hps-client", "Ansys HPS Python Client Documentation", ["ANSYS, Inc."], 1)
]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
# texinfo_documents = [
#     (
#         "index",
#         "ansys-hps-client",
#         "Ansys HPS Python Client Documentation",
#         "ANSYS, Inc.",
#         "JMS",
#         "One line description of project.",
#         "Miscellaneous",
#     ),
# ]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False

# disabled because of side effects
# rst_prolog = f"""
# .. |ansys_version| replace:: {__ansys_apps_version__}
# """

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
        secured?returnurl=/Views/Secured/hpcplat/v000/en/rep_ug/%s.html""",
        "ANSYS Help - ",
    ),
}

# Configuration for Sphinx Design
# -----------------------------------------------------------------------------
suppress_warnings = [
    "design.fa-build",
]


def archive_examples(app: sphinx.application.Sphinx) -> None:
    """Create a zip archive for each listed example included in the examples folder.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx application instance containing the all the doc build configuration.

    """
    source_dir = Path(app.srcdir)
    root_path = source_dir.parent.parent

    # Create zip files for each example
    build_path = root_path / "build"
    build_path.mkdir(exist_ok=True)
    for name, files in EXAMPLES.items():
        with ZipFile(build_path / f"{name}.zip", "w") as zip_archive:
            for file in files:
                zip_archive.write(root_path / "examples" / name / file, file)

    with ZipFile(build_path / "pyhps_examples.zip", "w") as zip_archive:
        for name, files in EXAMPLES.items():
            for file in files:
                zip_archive.write(root_path / "examples" / name / file, Path(name) / file)

    # Copy zipped example files to target directory at build time
    download_files_dir = source_dir.parent / "_build" / "html" / "_downloads"
    download_files_dir.mkdir(exist_ok=True)
    for file_path in build_path.glob("*"):
        if file_path.is_file():
            shutil.copy(file_path, download_files_dir)


def setup(app: sphinx.application.Sphinx) -> None:
    """Run hook function(s) during the documentation build.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Sphinx application instance containing the all the doc build configuration.

    """
    app.connect("builder-inited", archive_examples)
