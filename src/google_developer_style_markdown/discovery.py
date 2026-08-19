"""Discover the pages of the style guide from its entry page.

Discovery is deliberately narrow. The only page fetched as HTML is

:data:`GUIDE`; every link is then taken from the guide's own table of contents
(the ``_book`` navigation menu that DevSite renders on every page). There is no
recursive crawl, and nothing outside :data:`GUIDE` is ever considered.
"""

from dataclasses import dataclass

from selectolax.lexbor import LexborHTMLParser
from yarl import URL

from . import SyncError

__all__ = ['GUIDE', 'Page', 'normalize', 'parse_index']

GUIDE = URL('https://developers.google.com/style/')
"""Entry point of the guide, and the only URL fetched as HTML.

Everything the mirror treats as in scope is derived from this one URL: the host
a page has to be served from, and the path it has to live under.
"""

_SCOPE = tuple(part for part in GUIDE.raw_parts[1:] if part)

_DEFAULT_SECTION = 'Documentation'


@dataclass(frozen=True, slots=True, kw_only=True)
class Page:
    """One page of the guide, as advertised by the table of contents."""

    title: str
    """Navigation label Google gives the page. Not always its heading."""

    url: str
    """Canonical page URL, without a trailing slash."""

    section: str
    """Table-of-contents section the page is listed under."""

    def __post_init__(self) -> None:
        """Refuse a page that cannot be given a plain file name.

        The name goes straight into a path under ``docs/``, and percent-encoded
        segments decode into separators, so this is checked once here rather
        than trusted at every call site.

        Raises:
            SyncError: If the URL does not name a single, ordinary file.
        """
        name = self.filename
        if not name or name.startswith('.') or set(name) & set('/\\'):
            raise SyncError(f'{self.url} does not name a file that can live in docs/')

    @property
    def markdown_url(self) -> str:
        """URL of the Markdown source Google publishes for this page."""
        return f'{self.url}.md.txt'

    @property
    def filename(self) -> str:
        """Name this page is mirrored under.

        Taken from the URL Google actually serves, minus its ``.txt``: the file
        is called whatever the source is called, so there is no naming scheme
        to keep in step with anything. The guide's entry page is served at
        ``/style.md.txt`` and is therefore mirrored as ``style.md``.
        """
        return URL(self.markdown_url).name.removesuffix('.txt')


def normalize(href: str, *, base: URL = GUIDE) -> str | None:
    """Return the canonical guide URL for ``href``, or ``None`` if out of scope.

    Relative references are resolved against ``base``, which also resolves any
    ``..`` before the result is inspected. Fragments and query strings are
    dropped: on DevSite they select a position or a locale, never a different
    document, so keeping them would only produce duplicates. The path is then
    reduced to its non-empty segments, which collapses trailing and doubled
    slashes so that ``/style/lists``, ``/style/lists/`` and ``/style//lists``
    become one entry -- and so that appending ``.md.txt`` yields the URL Google
    actually serves.

    A reference is rejected when it points at another host, at a path outside
    :data:`GUIDE`, or at something that looks like a file rather than a page
    (its last segment has a suffix), which is what keeps assets such as images
    and archives out of the mirror.

    Args:
        href: Reference to resolve, absolute or relative.
        base: URL that relative references are resolved against.

    Returns:
        The canonical ``https`` URL of an in-scope page, or ``None``.
    """
    candidate = base.join(URL(href.strip()))
    if candidate.scheme not in {'http', 'https'} or candidate.host != GUIDE.host:
        return None
    # raw_parts leaves the segments percent-encoded. Reading the decoded ones
    # instead would let `%2F` and `%2E%2E` become separators again inside a
    # single segment, which passes the scope test and then escapes it when the
    # path is rebuilt -- `/style/%2e%2e%2fetc` would come back as `/etc`.
    segments = tuple(part for part in candidate.raw_parts[1:] if part)
    if segments[: len(_SCOPE)] != _SCOPE:
        return None
    page = GUIDE.origin().joinpath(*segments, encoded=True)
    return None if page.suffix else str(page)


def parse_index(markup: str, *, base: URL = GUIDE) -> tuple[Page, ...]:
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
        SyncError: If the navigation is missing, empty, lists a page that
            cannot be named, or maps two pages onto the same file name.
    """
    navigation = LexborHTMLParser(markup).css_first('ul[menu="_book"]')
    if navigation is None:
        raise SyncError(
            f'no table of contents in {base}: the page layout changed, the `ul[menu="_book"]` navigation is gone'
        )

    pages: list[Page] = []
    seen: dict[str, str] = {}
    section = _DEFAULT_SECTION

    for item in navigation.css('li'):
        link = item.css_first('a')
        if link is None:
            # An entry with no link is one of the group headings the navigation
            # is divided by. Reading it from the shape of the list rather than
            # from a DevSite class name leaves the menu selector above as the
            # only thing here that knows how the site is built.
            section = ' '.join(item.text().split()) or section
            continue
        if (href := link.attributes.get('href')) is None:
            continue
        text = ' '.join(link.text().split())
        if (url := normalize(href, base=base)) is None:
            continue
        page = Page(title=text, url=url, section=section)
        if (previous := seen.get(page.filename)) is not None:
            if previous == url:
                continue
            raise SyncError(f'{previous} and {url} both map to docs/{page.filename}')
        seen[page.filename] = url
        pages.append(page)

    if not pages:
        raise SyncError(f'no pages found in the table of contents of {base}')
    return tuple(pages)
