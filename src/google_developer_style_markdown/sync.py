"""Download the guide and write the mirror to disk.

The run is all-or-nothing: nothing is written until every page has been
downloaded successfully. That is what makes it safe for the mirror to delete
documents that are no longer part of the guide -- a network failure can never
be mistaken for a page that Google removed.
"""

import asyncio
import logging
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import aiohttp
from yarl import URL

from . import SyncError, __version__
from .discovery import GUIDE, Page, parse_index
from .render import document, llms_full, llms_txt

__all__ = ['DEFAULT_CONCURRENCY', 'DEFAULT_TIMEOUT', 'Report', 'sync', 'write_mirror']

_LOGGER = logging.getLogger(__name__)

USER_AGENT = (
    f'google-developer-style-markdown/{__version__} '
    '(+https://github.com/loic-bellinger/google-developer-style-markdown)'
)
"""Identifies the mirror to Google, with a page explaining what it does."""

DEFAULT_CONCURRENCY = 8
"""Simultaneous connections. The guide is ~70 pages; there is no hurry."""

DEFAULT_TIMEOUT = 30.0
"""Seconds allowed for a single request, connection and body included."""

DOCS_DIRECTORY = 'docs'
INDEX_FILE = 'llms.txt'
FULL_FILE = 'llms-full.txt'


@dataclass(frozen=True, slots=True, kw_only=True)
class Report:
    """What a completed sync did to the working tree."""

    documents: tuple[Path, ...]
    """Mirrored documents, in file name order."""

    removed: tuple[Path, ...]
    """Documents deleted because the guide no longer lists them."""


async def _fetch(session: aiohttp.ClientSession, url: URL | str) -> str:
    """Return the body of `url` as text, raising on any non-2xx status."""
    _LOGGER.debug('GET %s', url)
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text(encoding='utf-8')


async def fetch_guide(
    *,
    concurrency: int = DEFAULT_CONCURRENCY,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[tuple[Page, str], ...]:
    """Download the entry page, then the Markdown source of every page it lists.

    Concurrency is bounded by the connection pool rather than by a semaphore:
    all requests are scheduled at once and the connector releases them a few at
    a time, which keeps the load on Google's servers modest without any extra
    bookkeeping.

    Args:
        concurrency: Maximum number of simultaneous connections.
        timeout: Seconds allowed for each individual request.

    Returns:
        Each page of the guide paired with its Markdown source, in
        table-of-contents order.

    Raises:
        SyncError: If the entry page or any Markdown source cannot be
            downloaded, or if the table of contents cannot be read.
    """
    session = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=concurrency),
        timeout=aiohttp.ClientTimeout(total=timeout),
        headers={'User-Agent': USER_AGENT},
    )
    async with session:
        try:
            pages = parse_index(await _fetch(session, GUIDE))
        except (TimeoutError, aiohttp.ClientError) as error:
            raise SyncError(f'could not download {GUIDE}: {error}') from error
        _LOGGER.info('discovered %d pages', len(pages))
        bodies = await asyncio.gather(
            *(_fetch(session, page.markdown_url) for page in pages),
            return_exceptions=True,
        )

    failed = [
        f'  {page.markdown_url}: {body}'
        for page, body in zip(pages, bodies, strict=True)
        if isinstance(body, BaseException)
    ]
    if failed:
        listed = '\n'.join(failed)
        raise SyncError(f'could not download {len(failed)} of {len(pages)} pages:\n{listed}')
    return tuple(zip(pages, bodies, strict=True))  # type: ignore[arg-type]


def _write(path: Path, text: str) -> None:
    """Write `text` to `path` as UTF-8 with LF line endings, on any platform."""
    path.write_text(text, encoding='utf-8', newline='\n')


def write_mirror(fetched: Sequence[tuple[Page, str]], root: Path) -> Report:
    """Write `docs/`, `llms.txt` and `llms-full.txt` under `root`.

    Documents the guide no longer lists are deleted, so that `docs/` always
    describes the guide as it is today rather than as it has ever been. Only
    `*.md` files directly inside `docs/` are ever removed.

    `llms.txt` lists the pages in the order Google presents them, and
    `llms-full.txt` concatenates them in file name order.

    Args:
        fetched: Pages paired with their Markdown source, in reading order.
        root: Directory the mirror is written into.

    Returns:
        A description of what changed on disk.
    """
    documents = root / DOCS_DIRECTORY
    documents.mkdir(parents=True, exist_ok=True)

    written = {}
    for page, body in fetched:
        path = documents / page.filename
        _write(path, document(page, body))
        written[path] = (page, body)

    removed = tuple(path for path in sorted(documents.glob('*.md')) if path not in written)
    for path in removed:
        _LOGGER.info('removing %s: no longer part of the guide', path)
        path.unlink()

    # llms.txt follows Google's reading order; llms-full.txt follows file names.
    # Sorting the paths themselves is what makes the second claim true: sorting
    # the URLs instead would put headings before headings-targets, because '.'
    # and '-' do not compare the way the file names do.
    ordered = tuple(sorted(written))
    _write(root / INDEX_FILE, llms_txt(page for page, _ in fetched))
    _write(root / FULL_FILE, llms_full(written[path] for path in ordered))
    return Report(documents=ordered, removed=removed)


async def sync(
    root: Path,
    *,
    concurrency: int = DEFAULT_CONCURRENCY,
    timeout: float = DEFAULT_TIMEOUT,
) -> Report:
    """Mirror the guide into `root`.

    Args:
        root: Directory the mirror is written into.
        concurrency: Maximum number of simultaneous connections.
        timeout: Seconds allowed for each individual request.

    Returns:
        A description of what changed on disk.

    Raises:
        SyncError: If any part of the guide could not be downloaded or read.
    """
    return write_mirror(await fetch_guide(concurrency=concurrency, timeout=timeout), root)
