"""Sphinx directives for friend links."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .nodes import friendlink

if TYPE_CHECKING:
    from docutils.nodes import Node


class FriendLinkDirective(SphinxDirective):
    """Directive to create a friend link card.

    Usage::

        .. friendlink::
           :name: Example Site
           :link: https://example.com
           :avatar: https://example.com/avatar.png
           :descr: This is an example site
           :siteshot: https://example.com/screenshot.png
           :rss: https://example.com/rss.xml
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    option_spec = {
        'name': directives.unchanged_required,
        'link': directives.uri,
        'avatar': directives.uri,
        'descr': directives.unchanged_required,
        'siteshot': directives.uri,
        'rss': directives.uri,
    }

    def run(self) -> List[Node]:
        """Process the directive and return nodes."""
        # Validate required options
        for required in ('name', 'link', 'avatar', 'descr'):
            if required not in self.options:
                raise self.error(f':{required}: option is required')

        node = friendlink()
        node['name'] = self.options['name']
        node['link'] = self.options['link']
        node['avatar'] = self.options['avatar']
        node['descr'] = self.options['descr']
        node['siteshot'] = self.options.get('siteshot', '')
        node['rss'] = self.options.get('rss', '')

        return [node]
