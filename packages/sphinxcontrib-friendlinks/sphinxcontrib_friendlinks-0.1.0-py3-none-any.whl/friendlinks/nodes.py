"""Custom docutils nodes for friend links."""

from __future__ import annotations

from docutils import nodes


class friendlink(nodes.General, nodes.Element):
    """Node representing a single friend link card."""
    pass
