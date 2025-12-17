extensions = ["sphinxcontrib.pseudocode2"]

pseudocode2_math_engine = "unknown"

pseudocode2_options = {
    "linenos": True,
    "no-end": True,
    "caption-count": 99,
    "title-prefix": "Demo",
    "scopeLines": True,
}
html_static_path = ["_static"]

mathjax3_config = {
    "tex": {
        "inlineMath": [["\\(", "\\)"]],
        "displayMath": [["\\[", "\\]"]],
        "packages": {"[+]": ["ams"]},
    },
    "startup": {"typeset": True},
}
