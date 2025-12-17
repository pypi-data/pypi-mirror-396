# SPDX-FileCopyrightText: 2025 wmj <wmj.py@gmx.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "interregnum"
copyright = "2025, wmj <wmj.py@gmx.com>"
author = "wmj <wmj.py@gmx.com>"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "myst_parser",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.napoleon",
    # "sphinx.ext.inheritance_diagram",
    # 'sphinx.ext.graphviz',
]

autoclass_content = 'both'

autodoc_typehints = "description"
autodoc_member_order = "groupwise"
autodoc_default_options = {
    "special-members": "__call__, __str__, __invert__, __contains__, __getitem__, __deltitem__",
    "private-members": "_make_result_",
}
napoleon_numpy_docstring = True

templates_path = ["_templates"]
exclude_patterns = []


myst_enable_extensions = ["dollarmath", "colon_fence", "attrs_inline"]




# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
html_logo = "interregnum-logo.svg"

html_theme_options = {
    "show_relbars": True,
}
