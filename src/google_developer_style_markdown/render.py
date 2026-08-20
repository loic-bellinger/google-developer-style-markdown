"""Render the mirrored files.

Everything here is a pure function of its arguments: the same inputs always
produce byte-identical output, which is what makes a sync run idempotent and
its diffs meaningful.

Google's Markdown is reproduced verbatim. Only two things change in a page
body. Trailing whitespace collapses into the single final newline every text
file is expected to end with, because the `.md.txt` sources end without one.
In `llms-full.txt`, a page's leading `#` heading *moves* above the source line,
so that every document starts with a title. No line is ever rewritten,
dropped, or invented.

`docs/<name>.md` and `llms-full.txt` are rendered from the same downloads
rather than the second being parsed back out of the first, so the front matter
is written for whoever reads a mirrored file, not for this program.
"""

from collections.abc import Iterable
from itertools import groupby
from operator import attrgetter

from .discovery import GUIDE, Page

__all__ = ['document', 'llms_full', 'llms_txt']

TITLE = 'Google Developer Documentation Style Guide'

_FRONT_MATTER_FENCE = '---'
_HORIZONTAL_RULE = '---'

_SUMMARY = (
    "> Markdown mirror of Google's developer documentation style guide, reproduced\n"
    f'> verbatim from <{GUIDE}>—work\n'
    '> [created and shared by Google](https://developers.google.com/readme/policies), used\n'
    '> under the [Creative Commons 4.0 Attribution License](https://creativecommons.org/licenses/by/4.0/);\n'
    '> code samples under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).\n'
    '> Not affiliated with, sponsored by, or endorsed by Google.'
)


def _quote(value: str) -> str:
    """Returns `value` as a double-quoted YAML scalar."""
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def document(page: Page, body: str) -> str:
    """Returns the contents of the mirrored document for `page`.

    The body is Google's Markdown unchanged. A YAML front matter block ahead of
    it records where the page came from, which is what lets anyone regenerate,
    audit, and attribute the mirror without a sidecar index.

    Args:
        page: The page the body was downloaded for.
        body: The Markdown served at `Page.markdown_url`.

    Returns:
        The full text of the mirrored document, ending in a single newline.
    """
    fence = _FRONT_MATTER_FENCE
    front_matter = f'{fence}\ntitle: {_quote(page.title)}\nsource: {page.url}\n{fence}'
    return f'{front_matter}\n\n{body.rstrip()}\n'


def llms_txt(pages: Iterable[Page]) -> str:
    """Returns the `llms.txt` index, in the llmstxt.org v2 format.

    The file stays an index: a title, a summary, and one link list per
    table-of-contents section, in the order Google presents them, grouped the
    way the navigation groups them. The content itself lives behind the links,
    as the convention intends.

    Args:
        pages: The pages of the guide, in table-of-contents order.

    Returns:
        The full text of `llms.txt`, ending in a single newline.
    """
    blocks = [f'# {TITLE}', _SUMMARY]
    # groupby only groups neighbours, which is exactly the intent: the sections
    # are the ones the table of contents draws, in the order it draws them, and
    # a section Google split in two would be mirrored as two sections.
    for section, listed in groupby(pages, key=attrgetter('section')):
        entries = '\n'.join(f'- [{page.title}](docs/{page.filename})' for page in listed)
        blocks.append(f'## {section}\n\n{entries}')
    blocks.append(
        '## Full documentation\n\n- [llms-full.txt](llms-full.txt): every page above, concatenated into one file'
    )
    return '\n\n'.join(blocks) + '\n'


def llms_full(documents: Iterable[tuple[Page, str]]) -> str:
    """Returns `llms-full.txt`: every mirrored document, concatenated.

    Documents come out in the order given, separated by a horizontal rule, each
    introduced by its title and the URL it was reproduced from. A page that
    opens with a standalone `#` heading keeps that heading as its title. Any
    other page—one with no heading, or one whose heading wraps onto the
    following line, as a few pages of the guide do—is titled with its
    navigation label, and its body is left strictly untouched, so that a wrapped
    sentence is never split across the source line.

    Args:
        documents: The pages paired with their Markdown source, in a stable
            order.

    Returns:
        The full text of `llms-full.txt`, ending in a single newline.
    """
    blocks = [f'# {TITLE}', _SUMMARY]
    for page, markdown in documents:
        heading, _, rest = markdown.rstrip().partition('\n')
        if heading.startswith('# ') and not rest.partition('\n')[0].strip():
            title = heading
        else:
            title, rest = f'# {page.title}', markdown.rstrip()
        blocks.append(_HORIZONTAL_RULE)
        blocks.append(f'{title}\n\nSource: <{page.url}>')
        if content := rest.strip('\n'):
            blocks.append(content)
    return '\n\n'.join(blocks) + '\n'
