"""Discover the pages of the style guide from its entry page.

Discovery is deliberately narrow. The only page fetched as HTML is
:data:`INDEX_URL`; every link is then taken from the guide's own table of
contents (the ``_book`` navigation menu that DevSite renders on every page).
There is no recursive crawl, and nothing outside ``developers.google.com/style``
is ever considered.
"""

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit, urlunsplit

from selectolax.lexbor import LexborHTMLParser

from . import SyncError

__all__ = ['INDEX_URL', 'Page', 'normalize', 'parse_index']

INDEX_URL = 'https://developers.google.com/style/'
"""Entry point of the guide, and the only URL fetched as HTML."""

_HOST = 'developers.google.com'
_SCOPE = '/style'

# Slugs are used as file names, so they are restricted to a shape that cannot
# escape the output directory: lowercase words joined by single hyphens. No
# dots, no separators, nothing to normalise away.
_SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')

_DEFAULT_SECTION = 'Documentation'


@dataclass(frozen=True, slots=True, kw_only=True)
class Page:
    """One page of the guide, as advertised by the table of contents."""

    slug: str
    """File name stem under ``docs/``, derived from the URL path."""

    title: str
    """Navigation label Google gives the page. Not always its heading."""

    url: str
    """Canonical page URL, without a trailing slash."""

    section: str
    """Table-of-contents section the page is listed under."""

    @property
    def markdown_url(self) -> str:
        """URL of the Markdown source Google publishes for this page."""
        return f'{self.url}.md.txt'


def normalize(href: str, *, base: str = INDEX_URL) -> str | None:
    """Return the canonical guide URL for ``href``, or ``None`` if out of scope.

    Relative references are resolved against ``base``. Fragments and query
    strings are dropped: on DevSite they select a position or a locale, never a
    different document, so keeping them would only produce duplicates. Trailing
    slashes are removed so that ``/style/lists`` and ``/style/lists/`` collapse
    to one entry, and so that appending ``.md.txt`` yields the URL Google
    serves.

    A reference is rejected when it points at another host, at a path outside
    ``/style``, or at something that looks like a file rather than a page (its
    last segment contains a dot), which is what keeps assets such as images and
    archives out of the mirror.

    Args:
        href: Reference to resolve, absolute or relative.
        base: URL that relative references are resolved against.

    Returns:
        The canonical ``https`` URL of an in-scope page, or ``None``.
    """
    parts = urlsplit(urljoin(base, href.strip()))
    if parts.scheme not in {'http', 'https'} or parts.hostname != _HOST:
        return None
    path = parts.path.rstrip('/')
    if path != _SCOPE and not path.startswith(f'{_SCOPE}/'):
        return None
    if '.' in path.rpartition('/')[2]:
        return None
    return urlunsplit(('https', _HOST, path, '', ''))


def slug_for(url: str) -> str | None:
    """Return the ``docs/`` file name stem for ``url``, or ``None`` if unusable.

    The guide's entry page has no path below ``/style``, so it becomes
    ``index``. Nested paths are flattened with hyphens; the result must match
    :data:`_SLUG`, which makes path traversal and surprising file names
    impossible by construction rather than by escaping.
    """
    relative = urlsplit(url).path.removeprefix(_SCOPE).strip('/')
    slug = relative.replace('/', '-') or 'index'
    return slug if _SLUG.fullmatch(slug) else None


def parse_index(markup: str, *, base: str = INDEX_URL) -> tuple[Page, ...]:
    """Extract the table of contents from the HTML of the entry page.

    The navigation is a flat list in which section headings and page links are
    siblings, so the pages are walked in document order and each one is
    attributed to the most recent heading. Reading order is preserved: it is
    Google's own, and it is what ``llms.txt`` presents to a reader.

    Args:
        markup: HTML of the entry page.
        base: URL that relative references are resolved against.

    Returns:
        The pages of the guide, in table-of-contents order.

    Raises:
        SyncError: If the navigation is missing, empty, or maps two pages onto
            the same file name.
    """
    navigation = LexborHTMLParser(markup).css_first('ul[menu="_book"]')
    if navigation is None:
        raise SyncError(
            f'no table of contents in {base}: the page layout changed, the `ul[menu="_book"]` navigation is gone'
        )

    pages: list[Page] = []
    seen: dict[str, str] = {}
    section = _DEFAULT_SECTION

    for item in navigation.css('li.devsite-nav-item'):
        label = item.css_first('span.devsite-nav-text')
        if label is None:
            continue
        text = ' '.join(label.text().split())
        if 'devsite-nav-heading' in (item.attributes.get('class') or ''):
            section = text or section
            continue
        link = item.css_first('a.devsite-nav-title')
        if link is None or (href := link.attributes.get('href')) is None:
            continue
        if (url := normalize(href, base=base)) is None:
            continue
        if (slug := slug_for(url)) is None:
            continue
        if (previous := seen.get(slug)) is not None:
            if previous == url:
                continue
            raise SyncError(f'{previous} and {url} both map to docs/{slug}.md')
        seen[slug] = url
        pages.append(Page(slug=slug, title=text, url=url, section=section))

    if not pages:
        raise SyncError(f'no pages found in the table of contents of {base}')
    return tuple(pages)
