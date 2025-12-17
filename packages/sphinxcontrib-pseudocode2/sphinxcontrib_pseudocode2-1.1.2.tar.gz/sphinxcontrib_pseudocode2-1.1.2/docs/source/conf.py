#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -- General configuration ------------------------------------------------

extensions = [
    "sphinx.ext.mathjax",
    "sphinx.ext.autosummary",
    "sphinx_tabs.tabs",
    # "sphinx_copybutton",
    "sphinxcontrib.pseudocode2",
]

templates_path = ["_templates"]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"

project = "sphinxcontrib-pseudocode2"
copyright = "2021, Zeyuan Hu; 2025, WEN Hao"
author = "Zeyuan Hu; WEN Hao"

version = ""
release = ""

language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"
todo_include_todos = False

# -- HTML -----------------------------------------------------------------

# html_theme = "alabaster"
html_theme = "furo"
html_static_path = ["_static"]
html_show_sourcelink = True
htmlhelp_basename = "sphinxcontrib-pseudocode2-doc"

numfig = True

pseudocode2_math_engine = "katex"

pseudocode2_options = {
    "lineNumber": True,  # Global default: enable line numbering
    "lineNumberPunc": " | ",  # Punctuation after line numbers (e.g., "1 | ")
    "commentDelimiter": "#",  # Global default comment delimiter
    "noEnd": False,  # Global default: show no "END" for control blocks
    "titlePrefix": "PseudoCode",  # Global default title prefix (replace "Algorithm")
    "scopeLines": True,  # Global default: enable scope lines
}


def setup(app):
    app.add_js_file("codeblock.js")
    app.add_css_file("codeblock.css")
