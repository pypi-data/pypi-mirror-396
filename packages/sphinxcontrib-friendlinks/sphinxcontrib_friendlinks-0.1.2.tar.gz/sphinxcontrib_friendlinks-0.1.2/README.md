# sphinxcontrib-friendlinks

A Sphinx extension for rendering beautiful friend link cards in your documentation.

## Installation

```bash
pip install sphinxcontrib-friendlinks
```

## Usage

Add the extension to your `conf.py`:

```python
extensions = [
    'sphinxcontrib_friendlinks',
]
```

Then use the `friendlink` directive in your reStructuredText files:

```rst
.. friendlink::
   :name: Example Site
   :link: https://example.com
   :avatar: https://example.com/avatar.png
   :descr: This is an example site description
   :siteshot: https://example.com/screenshot.png
   :rss: https://example.com/rss.xml
```

## Options

| Option | Required | Description |
|--------|----------|-------------|
| `name` | Yes | Site name |
| `link` | Yes | Site URL |
| `avatar` | Yes | Avatar image URL |
| `descr` | Yes | Site description |
| `siteshot` | No | Site screenshot URL |
| `rss` | No | RSS feed URL |

## Features

- Clean card-style layout with avatar, name, description
- Optional site screenshot display
- RSS link with icon
- Responsive design for mobile devices
- Dark mode support (`prefers-color-scheme`)
- XSS protection for user input

## Example

![Friend Link Card Example](https://raw.githubusercontent.com/un4gt/sphinxcontrib-friendlinks/main/docs/_build/html/_static/example.png)

## License

MIT
