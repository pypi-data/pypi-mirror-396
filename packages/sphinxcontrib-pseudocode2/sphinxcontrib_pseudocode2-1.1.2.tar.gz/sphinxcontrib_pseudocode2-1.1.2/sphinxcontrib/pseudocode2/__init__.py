# -*- coding: utf-8 -*-
"""
sphinxcontrib.pseudocode2
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This sphinx extension renders LaTeX-style pseudocode using pseudocode.js.
Compatible with Sphinx 7.1+, supports MathJax 3 and KaTeX, and coexists with sphinx.ext.mathjax.
"""

import json

from docutils import nodes
from docutils.parsers.rst.directives import flag, unchanged
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

from .exceptions import Pseudocode2Error  # noqa: F401
from .version import __version__

logger = logging.getLogger(__name__)


MATH_ENGINE_RESOURCES = {
    "katex": {
        "js": ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/katex.min.js"],
        "css": ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/katex.min.css"],
    },
    "mathjax3": {"js": ["https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"], "css": []},
}

PSEUDOCODE_RESOURCES = {
    "js": ["https://cdn.jsdelivr.net/npm/pseudocode@2.4.1/build/pseudocode.min.js"],
    "css": ["https://cdn.jsdelivr.net/npm/pseudocode@2.4.1/build/pseudocode.min.css"],
}


class PCodeDirective(SphinxDirective):
    """Directive for rendering pseudocode using pseudocode.js"""

    has_content = True
    option_spec = {
        "linenos": flag,
        "indent": unchanged,
        "no-linenos": flag,
        "comment-delimiter": unchanged,
        "line-number-punc": unchanged,
        "no-end": flag,
        "scopelines": flag,
        "no-scopelines": flag,
        "caption-count": unchanged,
        "title-prefix": unchanged,
    }

    def run(self):
        content = "\n".join(self.content)
        container = nodes.container(classes=["pseudocode-container"])
        data_attrs = self._get_data_attributes()

        env = getattr(self, "env", None)
        app = getattr(env, "app", None) if env is not None else None
        global_opts = getattr(app.config, "pseudocode2_options", {}) if app is not None else {}
        global_opts = global_opts if global_opts is not None else {}

        if "no-scopelines" in self.options:
            use_scopelines = False
        elif "scopelines" in self.options:
            use_scopelines = True
        else:
            # fallback to global default
            use_scopelines = bool(global_opts.get("scopeLines", False))
        class_ = "scopeline-pseudocode" if use_scopelines else "pseudocode"
        pre_html = f'<pre class="{class_}" id="pseudocode-{id(self)}" {data_attrs}>'
        pre_node = nodes.raw(text=pre_html, format="html")
        container += pre_node

        escaped_content = self._escape_content(content)
        content_node = nodes.raw(text=escaped_content, format="html")
        container += content_node

        close_node = nodes.raw(text="</pre>", format="html")
        container += close_node

        return [container]

    def _get_data_attributes(self):
        attrs = []
        if "no-linenos" in self.options:
            attrs.append('data-line-number="false"')
        elif "linenos" in self.options:
            attrs.append('data-line-number="true"')

        option_mapping = {
            "indent": ("indent-size", lambda v: v),
            "comment-delimiter": ("comment-delimiter", lambda v: v),
            "line-number-punc": ("line-number-punc", lambda v: v),
            "no-end": ("no-end", lambda v: "true"),
            "caption-count": ("caption-count", lambda v: v),
            "title-prefix": ("title-prefix", lambda v: v),
        }

        for opt_name, (data_name, converter) in option_mapping.items():
            if opt_name in self.options:
                value = self.options[opt_name]
                attrs.append(f'data-{data_name}="{converter(value)}"')

        return " ".join(attrs)

    @staticmethod
    def _escape_content(content):
        """Escape HTML special characters"""
        return (
            content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")
        )


def is_mathjax_enabled(app: Sphinx) -> bool:
    """Check if sphinx.ext.mathjax or sphinx.ext.mathjax3 is enabled"""
    enabled_extensions = app.config.extensions or []
    return any(ext in enabled_extensions for ext in ["sphinx.ext.mathjax", "sphinx.ext.mathjax3"])


def merge_mathjax_config(app: Sphinx) -> str:
    """Merge user config (mathjax3_config) and extension default config, priority: user > default"""
    default_config = {
        "tex": {
            "inlineMath": [["$", "$"], ["\\(", "\\)"]],
            "displayMath": [["$$", "$$"], ["\\[", "\\]"]],
            "processEscapes": True,
            "processEnvironments": True,
            "packages": {"[+]": ["noerrors"]},
        },
        "startup": {"typeset": False},
    }

    user_config = getattr(app.config, "mathjax3_config", {})

    def deep_merge(default, user):
        if isinstance(default, dict) and isinstance(user, dict):
            merged = default.copy()
            for k, v in user.items():
                merged[k] = deep_merge(default.get(k, {}), v)
            return merged
        return user if user is not None else default

    merged_config = deep_merge(default_config, user_config)
    return json.dumps(merged_config)


def setup_math_engine(app: Sphinx):
    """Setup math engine"""
    math_engine = app.config.pseudocode2_math_engine
    user_has_mathjax = is_mathjax_enabled(app)

    if math_engine not in MATH_ENGINE_RESOURCES:
        logger.warning(f"Unsupported math engine: {math_engine}. Falling back to 'mathjax3'.")
        math_engine = "mathjax3"

    if math_engine == "mathjax3":
        if user_has_mathjax:
            logger.info("pseudocode2: Reusing existing MathJax from sphinx.ext.mathjax")
            merged_config = merge_mathjax_config(app)
            app.add_js_file(None, body=f"MathJax.config = Object.assign(MathJax.config, {merged_config});")
        else:
            resources = MATH_ENGINE_RESOURCES[math_engine]
            for js in resources["js"]:
                app.add_js_file(js)
            for css in resources["css"]:
                app.add_css_file(css)

            merged_config = merge_mathjax_config(app)
            app.add_js_file(None, body=f"MathJax = {merged_config};")

        app.add_js_file(
            None,
            body="""
            if (window.pseudocode && !window.pseudocode.mathRenderer) {
                window.pseudocode.mathRenderer = 'mathjax';
            }
        """,
        )

    elif math_engine == "katex":
        resources = MATH_ENGINE_RESOURCES[math_engine]
        for js in resources["js"]:
            app.add_js_file(js)
        for css in resources["css"]:
            app.add_css_file(css)
        app.add_js_file(
            None,
            body="""
            if (window.pseudocode && !window.pseudocode.mathRenderer) {
                window.pseudocode.mathRenderer = 'katex';
            }
        """,
        )


def setup_pseudocode_resources(app: Sphinx):
    """Load pseudocode.js core resources"""
    for js in PSEUDOCODE_RESOURCES["js"]:
        app.add_js_file(js)
    for css in PSEUDOCODE_RESOURCES["css"]:
        app.add_css_file(css)


def add_rendering_script(app: Sphinx):
    """Core rendering logic: ensure MathJax is fully ready, then render pseudocode, and force render formulas"""
    global_opts = app.config.pseudocode2_options or {}
    js_opts = []
    js_opts_scopelines = []
    for k, v in global_opts.items():
        if isinstance(v, bool):
            js_opts.append(f"{k}: {str(v).lower()}")
        elif isinstance(v, str):
            js_opts.append(f'{k}: "{v}"')
        else:
            js_opts.append(f"{k}: {v}")
        if k != "scopeLines":
            js_opts_scopelines.append(js_opts[-1])
        else:
            # remove scopeLines option for pseudocode class
            js_opts.pop()
    js_opts_scopelines = js_opts + ["scopeLines: true"]
    js_opts_str = "{" + ", ".join(js_opts) + "}" if js_opts else ""
    js_opts_scopelines_str = "{" + ", ".join(js_opts_scopelines) + "}" if js_opts_scopelines else ""

    app.add_js_file(
        None,
        body=f"""
        async function renderPseudocodeWithMath() {{
            try {{
                if (window.MathJax) {{
                    await MathJax.startup.promise;
                    console.log("pseudocode2: MathJax is ready");
                }}

                pseudocode.renderClass('pseudocode', {js_opts_str});
                pseudocode.renderClass("scopeline-pseudocode", {js_opts_scopelines_str});
                console.log("pseudocode2: Pseudocode rendered");

                if (window.MathJax) {{
                    const pseudocodeBlocks = document.querySelectorAll('.pseudocode-container');
                    MathJax.typesetPromise(pseudocodeBlocks).then(() => {{
                        console.log("pseudocode2: MathJax typeset completed for pseudocode");
                    }}).catch(err => {{
                        console.warn("pseudocode2: MathJax typeset failed:", err);
                    }});
                }}
            }} catch (err) {{
                console.error("pseudocode2: Render failed:", err);
            }}
        }}

        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', renderPseudocodeWithMath);
        }} else {{
            renderPseudocodeWithMath();
        }}
    """,
    )


def setup(app: Sphinx):
    """Sphinx extension entry point"""
    app.add_config_value("pseudocode2_math_engine", "katex", "html", types=[str])
    app.add_config_value("pseudocode2_options", None, "html", types=[dict])

    app.add_directive("pcode", PCodeDirective)

    app.connect("builder-inited", setup_math_engine)
    app.connect("builder-inited", setup_pseudocode_resources)
    app.connect("builder-inited", add_rendering_script)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
