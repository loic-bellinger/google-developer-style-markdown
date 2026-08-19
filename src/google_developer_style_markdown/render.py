"""Render the mirrored files.

Everything here is a pure function of its arguments: the same inputs always
produce byte-identical output, which is what makes a sync run idempotent and
its diffs meaningful.

Google's Markdown is reproduced verbatim. The only changes made to a page body
are that trailing whitespace collapses into the single final newline every text
file is expected to end with (the ``.md.txt`` sources end without one), and that
in ``llms-full.txt`` a page's leading ``#`` heading is *moved* above the source
line so that every document starts with a title. No line is ever rewritten,
dropped, or invented.
"""

from collections.abc import Iterable, Mapping

from . import SyncError
from .discovery import INDEX_URL, Page

__all__ = ['document', 'llms_full', 'llms_txt', 'parse_document']

TITLE = 'Google Developer Documentation Style Guide'

_FRONT_MATTER_FENCE = '---'
_HORIZONTAL_RULE = '---'

_SUMMARY = (
    "> Automatically synchronized Markdown mirror of Google's developer documentation\n"
    '> style guide, reproduced from the Markdown sources published under\n'
    f'> {INDEX_URL}'
)

_FULL_SUMMARY = (
    '> Full text of the mirrored guide: every page under `docs/`, concatenated in file\n'
    '> name order. Read `llms.txt` first if you only need the index.'
)

_ATTRIBUTION = (
    'Portions of this file are reproduced from work created and\n'
    '[shared by Google](https://developers.google.com/readme/policies) and used according to\n'
    'terms described in the\n'
    '[Creative Commons 4.0 Attribution License](https://creativecommons.org/licenses/by/4.0/);\n'
    'code samples are licensed under the\n'
    '[Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). This mirror is not\n'
    'affiliated with, sponsored by, or endorsed by Google, and every document records the\n'
    'URL it was reproduced from.'
)


def _quote(value: str) -> str:
    """Return ``value`` as a double-quoted YAML scalar."""
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def _unquote(value: str) -> str:
    """Return the text of a YAML scalar written by :func:`_quote`."""
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return value


def document(page: Page, body: str) -> str:
    """Return the contents of ``docs/<slug>.md`` for ``page``.

    The body is Google's Markdown unchanged. It is preceded by a YAML front
    matter block recording where the page came from, which is what lets the
    mirror be regenerated, audited, and attributed without a side-car index.

    Args:
        page: Page the body was downloaded for.
        body: Markdown served at :attr:`Page.markdown_url`.

    Returns:
        The full text of the mirrored document, ending in a single newline.
    """
    fence = _FRONT_MATTER_FENCE
    front_matter = f'{fence}\ntitle: {_quote(page.title)}\nsource: {page.url}\n{fence}'
    return f'{front_matter}\n\n{body.rstrip()}\n'


def parse_document(text: str) -> tuple[Mapping[str, str], str]:
    """Split a mirrored document into its front matter and its body.

    Args:
        text: Contents of a file written by :func:`document`.

    Returns:
        The front matter fields, and the body with no leading blank line.

    Raises:
        SyncError: If ``text`` has no front matter block.
    """
    opening = f'{_FRONT_MATTER_FENCE}\n'
    closing = f'\n{_FRONT_MATTER_FENCE}\n'
    if not text.startswith(opening) or (end := text.find(closing, len(opening))) < 0:
        raise SyncError('document has no front matter block: it was not written by this tool')
    fields = {}
    for line in text[len(opening) : end].splitlines():
        key, separator, value = line.partition(':')
        if separator:
            fields[key.strip()] = _unquote(value.strip())
    return fields, text[end + len(closing) :].lstrip('\n')


def llms_txt(pages: Iterable[Page]) -> str:
    """Return the ``llms.txt`` index, in the llmstxt.org v2 format.

    The file stays an index: a title, a summary, and one link list per
    table-of-contents section, in the order Google presents them. The content
    itself lives behind the links, as the convention intends.

    Args:
        pages: Pages of the guide, in table-of-contents order.

    Returns:
        The full text of ``llms.txt``, ending in a single newline.
    """
    sections: dict[str, list[Page]] = {}
    for page in pages:
        sections.setdefault(page.section, []).append(page)

    blocks = [f'# {TITLE}', _SUMMARY, _ATTRIBUTION]
    for section, listed in sections.items():
        entries = '\n'.join(f'- [{page.title}](docs/{page.slug}.md)' for page in listed)
        blocks.append(f'## {section}\n\n{entries}')
    blocks.append(
        '## Full documentation\n\n- [llms-full.txt](llms-full.txt): every page above, concatenated into one file'
    )
    return '\n\n'.join(blocks) + '\n'


def llms_full(documents: Iterable[str]) -> str:
    """Return ``llms-full.txt``: every mirrored document, concatenated.

    Documents are emitted in the order given, separated by a horizontal rule,
    and each is introduced by its title and the URL it was reproduced from. A
    page that opens with a standalone ``#`` heading keeps that heading as its
    title. Any other page -- one with no heading, or one whose heading wraps
    onto the following line, which a few pages of the guide do -- is titled with
    its navigation label and its body is left strictly untouched, so that a
    wrapped sentence is never split across the source line.

    Args:
        documents: Contents of the ``docs/`` files, in a stable order.

    Returns:
        The full text of ``llms-full.txt``, ending in a single newline.

    Raises:
        SyncError: If a document is not in the format written by
            :func:`document`.
    """
    blocks = [
        f'# {TITLE}',
        _FULL_SUMMARY,
        _ATTRIBUTION,
    ]
    for text in documents:
        fields, body = parse_document(text)
        heading, _, rest = body.partition('\n')
        if heading.startswith('# ') and not rest.partition('\n')[0].strip():
            title = heading
        else:
            title, rest = f'# {fields.get("title", "")}'.rstrip(), body
        blocks.append(_HORIZONTAL_RULE)
        blocks.append(f'{title}\n\nSource: <{fields.get("source", "")}>')
        if content := rest.strip('\n'):
            blocks.append(content)
    return '\n\n'.join(blocks) + '\n'
