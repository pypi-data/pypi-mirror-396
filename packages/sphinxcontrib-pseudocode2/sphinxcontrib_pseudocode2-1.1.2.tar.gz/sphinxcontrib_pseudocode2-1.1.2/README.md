# sphinxcontrib-pseudocode2

[![pytest](https://github.com/DeepPSP/sphinxcontrib-pseudocode2/actions/workflows/run-pytest.yml/badge.svg)](https://github.com/DeepPSP/sphinxcontrib-pseudocode2/actions/workflows/run-pytest.yml)
[![codecov](https://codecov.io/gh/DeepPSP/sphinxcontrib-pseudocode2/branch/master/graph/badge.svg?token=4IQD228F7L)](https://codecov.io/gh/DeepPSP/sphinxcontrib-pseudocode2)
[![PyPI](https://img.shields.io/pypi/v/sphinxcontrib-pseudocode2?style=flat-square)](https://pypi.org/project/sphinxcontrib-pseudocode2/)
[![RTD Status](https://readthedocs.org/projects/sphinxcontrib-pseudocode2/badge/?version=latest)](https://pcode2.readthedocs.io/en/latest/?badge=latest)
[![gh-page status](https://github.com/DeepPSP/sphinxcontrib-pseudocode2/actions/workflows/docs-publish.yml/badge.svg?branch=doc)](https://github.com/DeepPSP/sphinxcontrib-pseudocode2/actions/workflows/docs-publish.yml)
<!-- [![downloads](https://img.shields.io/pypi/dm/sphinxcontrib-pseudocode2?style=flat-square)](https://pypistats.org/packages/sphinxcontrib-pseudocode2) -->
[![PyPI Downloads](https://static.pepy.tech/badge/sphinxcontrib-pseudocode2/month)](https://pepy.tech/projects/sphinxcontrib-pseudocode2)
[![license](https://img.shields.io/github/license/DeepPSP/sphinxcontrib-pseudocode2?style=flat-square)](LICENSE.rst)
![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/DeepPSP/sphinxcontrib-pseudocode2)
![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/DeepPSP/sphinxcontrib-pseudocode2/latest)

This is a fork of the original [sphinxcontrib-pseudocode project](https://github.com/xxks-kkk/sphinxcontrib-pseudocode/),
updated to support Sphinx 7.1+ and 8.x, and modern [pseudocode.js](https://github.com/SaswatPadhi/pseudocode.js).

## Installation

```bash
pip install sphinxcontrib-pseudocode2
```

## Quick Start

Enable the extension in your Sphinx `conf.py`:

```python
extensions = [
    ...,
    "sphinxcontrib.pseudocode2",
]

# -------------------------- Optional Configuration --------------------------
# 1. Specify math engine (default: "mathjax3", alternative: "katex")
pseudocode2_math_engine = "mathjax3"

# 2. Global pseudocode.js configuration (pseudocode2_options)
#    All parameters are directly passed to pseudocode.renderClass()
#    Covers all pseudocode.js native options (unified project-wide style)
pseudocode2_options = {
    "lineNumber": True,           # Global default: enable line numbering
    "lineNumberPunc": " | ",      # Punctuation after line numbers (e.g., "1 | ")
    "commentDelimiter": "#",      # Global default comment delimiter
    "noEnd": False,               # Global default: show "END" for control blocks
    "titlePrefix": "PseudoCode",  # Global default title prefix (replace "Algorithm")
    "scopeLines": True,           # Global default: enable scope line highlighting
}
```

Write LaTeX-like pseudocode in an `.. pcode::` directive:

```text
.. pcode::
   :linenos:

   \begin{algorithm}
   \caption{Quicksort}
   \begin{algorithmic}
   \PROCEDURE{Quicksort}{$A, p, r$}
     \IF{$p < r$}
       \STATE $q = $ \CALL{Partition}{$A, p, r$}
       \STATE \CALL{Quicksort}{$A, p, q - 1$}
       \STATE \CALL{Quicksort}{$A, q + 1, r$}
     \ENDIF
   \ENDPROCEDURE
   \end{algorithmic}
   \end{algorithm}
```

## Configuration Options

Pseudocode rendering is extended with practical options (all compatible with pseudocode.js native capabilities):

- ``linenos``: Enable line numbering
- ``no-linenos``: Disable line numbering
- ``indent``: Set indentation (working only for ``em``, no other units) for code blocks, default: ``1.2em``
- ``comment-delimiter``: Customize comment delimiters, default: ``//``
- ``line-number-punc``: Set line number punctuation, default: ``:``
- ``no-end``: Omit the ``END`` keyword for control blocks
- ``title-prefix``: Customize the algorithm title prefix (e.g., ``PseudoCode`` instead of default ``Algorithm``)
- ``caption-count``: Reset the caption counter to this number
- ``scopelines``: Highlight scope lines (those with control block starters like IF, FOR, WHILE, etc.)
- ``no-scopelines``: Disable scope line highlighting

### Global Configuration via ``pseudocode2_options``

Pseudocode rendering styles can be unified across the entire project using a single global configuration (supports all pseudocode.js native parameters, see the ``Options`` section of [pseudocode.js](https://github.com/SaswatPadhi/pseudocode.js)). See also the example in the [Quick Start section](#quick-start).

**Priority Rule**:
Configuration priority (higher priority overrides lower): Directive option (e.g., :linenos: in .rst) > pseudocode2_options (global in conf.py) > pseudocode.js default.

## Tips

- Custom (Manual) indentation Control: ``pseudocode.js`` and ``algorithmic`` do not have a built-in way (a single command
  or a pair of commands) to set custom indentation levels. However, you can manually adjust indentation by the following
  workaround: use LaTeX's horizontal space command **inside** a math environment. Specifically, use

  ``$\hspace{<length>}$`` where ``<length>`` is a LaTeX length (e.g., ``2em``, ``1cm``, etc.). For example:

  ```text
  \STATE $\hspace{2em}$ This line is indented by 2em
  ```
