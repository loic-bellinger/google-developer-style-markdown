"""Discover the pages of the style guide from its entry page.

Discovery is deliberately narrow. The only page fetched as HTML is

`GUIDE`; every link is then taken from the guide's own table of contents
(the `_book` navigation menu that DevSite renders on every page). There is no
recursive crawl, and nothing outside `GUIDE` is ever considered.
"""

from dataclasses import dataclass
from pathlib import PurePosixPath

from selectolax.lexbor import LexborHTMLParser
from yarl import URL

from . import SyncError

__all__ = ['GUIDE', 'Page', 'normalize', 'parse_index']

GUIDE = URL('https://developers.google.com/style/')
"""Entry point of the guide, and the only URL fetched as HTML.

Everything the mirror treats as in scope is derived from this one URL: the host
a page has to be served from, and the path it has to live under.
"""

_SCOPE = PurePosixPath(GUIDE.raw_path)
"""Path every page of the guide lives under, derived from `GUIDE`."""

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

        The name goes straight into a path under `docs/`, and it is the
        decoded form of a URL segment, which is where percent-encoding can turn
        back into a separator. `normalize` deliberately leaves that to be
        settled here, so that an encoded name a page can legitimately have is
        kept while one that cannot be written is refused.

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

        Taken from the URL Google actually serves, minus its `.txt`: the file
        is called whatever the source is called, so there is no naming scheme
        to keep in step with anything. The guide's entry page is served at
        `/style.md.txt` and is therefore mirrored as `style.md`.
        """
        return URL(self.markdown_url).name.removesuffix('.txt')


def normalize(href: str) -> str | None:
    """Return the canonical guide URL for `href`, or `None` if out of scope.

    Relative references are resolved against `GUIDE`, which also resolves any
    `..` before the result is inspected. Fragments and query strings are
    dropped: on DevSite they select a position or a locale, never a different
    document, so keeping them would only produce duplicates. Trailing and
    doubled slashes are collapsed, so that `/style/lists`, `/style/lists/`
    and `/style//lists` become one entry -- and so that appending `.md.txt`
    yields the URL Google actually serves.

    A reference is rejected when it points at another host, when it falls
    outside `GUIDE`, or when it looks like a file rather than a page (its
    name has a suffix), which is what keeps assets such as images and archives
    out of the mirror.

    That last rule is why this takes the address of a *page*. A `.md.txt`
    address is a file by the same test and would be rejected, which is
    harmless only because the Markdown form is never discovered: it is derived
    from a page that has already come through here, by
    `Page.markdown_url`. Anything that starts finding pages somewhere
    other than the table of contents -- a sitemap, a link in the prose -- has
    to keep that separation or drop every address it is looking for.

    Args:
        href: Address of a page of the guide, absolute or relative.

    Returns:
        The canonical `https` URL of an in-scope page, or `None`.
    """
    candidate = GUIDE.join(URL(href.strip()))
    if candidate.scheme not in {'http', 'https'} or candidate.host != GUIDE.host:
        return None
    # Scope is decided on the encoded path, and the encoding is carried through.
    # join has already decoded `%2E` and resolved the dot segments, but `%2F` is
    # reserved and survives: `/style/%2e%2e%2fetc` arrives as the single segment
    # `..%2Fetc`, inside the guide, and is refused by `Page` once the name
    # decodes into `../etc`. Encoding is not refused outright, because a page
    # could legitimately have one in its name.
    path = PurePosixPath(candidate.raw_path)
    if not path.is_relative_to(_SCOPE) or path.suffix:
        return None
    # with_path drops the query and the fragment, and PurePosixPath has already
    # collapsed trailing and doubled slashes.
    return str(GUIDE.with_path(str(path), encoded=True))


def parse_index(markup: str) -> tuple[Page, ...]:
    """Extract the table of contents from the HTML of the entry page.

    The navigation is a flat list in which section headings and page links are
    siblings, so the pages are walked in document order and each one is
    attributed to the most recent heading. Reading order is preserved: it is
    Google's own, and it is what `llms.txt` presents to a reader.

    Args:
        markup: HTML of the entry page.

    Returns:
        The pages of the guide, in table-of-contents order.

    Raises:
        SyncError: If the navigation is missing, empty, lists a page that
            cannot be named, or maps two pages onto the same file name.
    """
    navigation = LexborHTMLParser(markup).css_first('ul[menu="_book"]')
    if navigation is None:
        raise SyncError(
            f'no table of contents in {GUIDE}: the page layout changed, the `ul[menu="_book"]` navigation is gone'
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
        if (url := normalize(href)) is None:
            continue
        page = Page(title=text, url=url, section=section)
        if (previous := seen.get(page.filename)) is not None:
            if previous == url:
                continue
            raise SyncError(f'{previous} and {url} both map to docs/{page.filename}')
        seen[page.filename] = url
        pages.append(page)

    if not pages:
        raise SyncError(f'no pages found in the table of contents of {GUIDE}')
    return tuple(pages)
