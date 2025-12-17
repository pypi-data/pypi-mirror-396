"""sphinxcontrib-friendlinks: A Sphinx extension for friend links."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict

from .directives import FriendLinkDirective
from .nodes import friendlink
from .writers import depart_friendlink, visit_friendlink

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__version__ = "0.1.2"


def _add_static_path(app: "Sphinx") -> None:
    """Add the static path to the Sphinx configuration."""
    static_path = os.path.join(os.path.dirname(__file__), "static")
    app.config.html_static_path.append(static_path)


def setup(app: "Sphinx") -> Dict[str, Any]:
    """Setup the sphinxcontrib-friendlinks extension."""
    # Register the custom node
    app.add_node(
        friendlink,
        html=(visit_friendlink, depart_friendlink),
    )

    # Register the directive
    app.add_directive("friendlink", FriendLinkDirective)

    # Add static files (CSS)
    app.connect("builder-inited", _add_static_path)
    app.add_css_file("friendlinks.css")

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
