*****************************************
Welcome to sphinxcontrib-pseudocode2 demo
*****************************************

.. toctree::
   :maxdepth: 2
   :caption: Contents:

########
Features
########

Below shows various rendered algorithms, which are copied from corresponding
`pseudocode.js examples <https://github.com/SaswatPadhi/pseudocode.js/blob/master/static/body.html.part>`__.
The source code of those algorithms can be found
`here <https://github.com/xxks-kkk/sphinxcontrib-pseudocode/blob/master/docs/demo.rst>`__.

We can also reference any particular algorithm. For example:

.. - ``:ref:`quick-sort <quick-sort>``` produces :ref:`quick-sort <quick-sort>`
.. - ``:ref:`Here is my algorithm {number} <quick-sort>``` produces :ref:`Here is my algorithm {number} <quick-sort>`

- ``:ref:`test control blocks <test-control-blocks>``` produces :ref:`test control blocks <test-control-blocks>`

.. note::

    We assume each ``pcode`` directive contains exactly one :math:`\LaTeX` algorithmic block::

        \begin{algorithm}
        \caption{Test atoms}
        \begin{algorithmic}
        \STATE my algorithm 1
        \END{ALGORITHMIC}
        \END{ALGORITHM}

    You still can have multiple algorithmic blocks but the numbering might be messed up.

By default, each ``pcode`` is mapped to 'Algorithm %s' when referenced via ``ref``.
You can change this behavior by overriding the corresponding string of ``'pseudocode'`` key in
`numfig_format <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-numfig_format>`_.

Configuration Options
=====================================================

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

Global Configuration via ``pseudocode2_options``
=====================================================

Pseudocode rendering styles can be unified across the entire project using a single global configuration (supports all pseudocode.js native parameters, see the ``Options`` section of [pseudocode.js](https://github.com/SaswatPadhi/pseudocode.js)). The following example shows how to set global options in `conf.py`:

.. code-block:: python

    pseudocode2_options = {
        "lineNumber": True,           # Global default: enable line numbering
        "lineNumberPunc": " | ",      # Punctuation after line numbers (e.g., "1 | ")
        "commentDelimiter": "#",      # Global default comment delimiter
        "noEnd": False,               # Global default: show "END" for control blocks
        "titlePrefix": "PseudoCode",  # Global default title prefix (replace "Algorithm")
        "scopeLines": True,           # Global default: enable scope line highlighting
    }

**Priority Rule**:
Configuration priority (higher priority overrides lower): Directive option (e.g., :linenos: in .rst) > pseudocode2_options (global in conf.py) > pseudocode.js default

Tips
=====================================================

- Custom (Manual) indentation Control: ``pseudocode.js`` and ``algorithmic`` do not have a built-in way (a single command
  or a pair of commands) to set custom indentation levels. However, you can manually adjust indentation by the following
  workaround: use LaTeX's horizontal space command **inside** a math environment. Specifically, use

  ``$\hspace{<length>}$`` where ``<length>`` is a LaTeX length (e.g., ``2em``, ``1cm``, etc.). For example:

  .. code-block:: latex

    \STATE $\hspace{2em}$ This line is indented by 2em

  See also :ref:`this example <test-atoms-algo>`

########
Examples
########

.. include:: demo.rst
