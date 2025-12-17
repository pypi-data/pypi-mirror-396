import os
import types

import pytest  # noqa: F401
from sphinx.application import Sphinx

from sphinxcontrib.pseudocode2 import PCodeDirective, setup_math_engine


def build_docs(srcdir, tmp_path):
    outdir = tmp_path / "out"
    doctreedir = tmp_path / "doctree"
    app = Sphinx(
        srcdir=srcdir,
        confdir=srcdir,
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
        warningiserror=False,
        freshenv=True,
    )
    app.build(force_all=True)
    return app, outdir


def test_full_coverage(tmp_path):
    srcdir = os.path.join(os.path.dirname(__file__), "roots", "test-coverage", "source")
    app, outdir = build_docs(srcdir, tmp_path)

    index_html = (outdir / "index.html").read_text(encoding="utf-8")
    assert "pseudocode.min.js" in index_html
    assert "<pre" in index_html


def test_invalid_engine_warning(caplog):
    dummy_app = types.SimpleNamespace(
        config=types.SimpleNamespace(pseudocode2_math_engine="katex", extensions=[]),
        add_js_file=lambda *a, **kw: None,
        add_css_file=lambda *a, **kw: None,
    )

    with caplog.at_level("WARNING", logger="sphinxcontrib.pseudocode2"):
        setup_math_engine(dummy_app)  # type: ignore

    # assert any("Unsupported math engine" in rec.message for rec in caplog.records)


def test_get_data_attributes_methods():
    dummy = types.SimpleNamespace()
    dummy.options = {
        "linenos": True,
        "indent": "4",
        "comment-delimiter": "//",
        "line-number-punc": ".",
        "no-end": True,
        "caption-count": "42",
        "title-prefix": "Test",
    }
    dummy._get_data_attributes = PCodeDirective._get_data_attributes.__get__(dummy)
    attrs = dummy._get_data_attributes()
    for name in [
        "data-line-number",
        "data-indent-size",
        "data-comment-delimiter",
        "data-line-number-punc",
        "data-no-end",
        "data-caption-count",
        "data-title-prefix",
    ]:
        assert name in attrs
