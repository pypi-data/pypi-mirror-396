"""HTML writers for friend link nodes."""

from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.writers.html import HTMLTranslator
    from .nodes import friendlink


def visit_friendlink(self: HTMLTranslator, node: friendlink) -> None:
    """Generate HTML for the friend link card."""
    name = escape(node['name'])
    link = escape(node['link'], quote=True)
    avatar = escape(node['avatar'], quote=True)
    descr = escape(node['descr'])
    siteshot = escape(node['siteshot'], quote=True) if node['siteshot'] else ''
    rss = escape(node['rss'], quote=True) if node['rss'] else ''

    # Determine if we have a siteshot
    has_siteshot = bool(siteshot)
    card_class = 'friendlink-card' + (' has-siteshot' if has_siteshot else '')

    html = f'''<div class="{card_class}">
  <div class="friendlink-left">
    <img class="friendlink-avatar" src="{avatar}" alt="{name}" loading="lazy">
    <div class="friendlink-info">
      <a class="friendlink-name" href="{link}" target="_blank" rel="noopener noreferrer">{name}</a>
      <p class="friendlink-descr">{descr}</p>'''

    if rss:
        html += f'''
      <a class="friendlink-rss" href="{rss}" target="_blank" rel="noopener noreferrer">
        <svg class="friendlink-rss-icon" viewBox="0 0 24 24" width="14" height="14">
          <path fill="currentColor" d="M6.18 15.64a2.18 2.18 0 0 1 2.18 2.18C8.36 19 7.38 20 6.18 20C5 20 4 19 4 17.82a2.18 2.18 0 0 1 2.18-2.18M4 4.44A15.56 15.56 0 0 1 19.56 20h-2.83A12.73 12.73 0 0 0 4 7.27V4.44m0 5.66a9.9 9.9 0 0 1 9.9 9.9h-2.83A7.07 7.07 0 0 0 4 12.93V10.1Z"/>
        </svg>
        RSS
      </a>'''

    html += '''
    </div>
  </div>'''

    if has_siteshot:
        html += f'''
  <div class="friendlink-right">
    <img class="friendlink-siteshot" src="{siteshot}" alt="{name} screenshot" loading="lazy">
  </div>'''

    html += '''
</div>'''

    self.body.append(html)


def depart_friendlink(self: HTMLTranslator, node: friendlink) -> None:
    """No action needed on departure."""
    pass
