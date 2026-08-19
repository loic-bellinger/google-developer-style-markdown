"""Tests for the parts of the mirror that must never drift.

URL handling, file naming, rendering, and the deletion of pages the guide has
dropped.
"""

import pytest

from google_developer_style_markdown import SyncError
from google_developer_style_markdown.discovery import Page, normalize, parse_index, slug_for
from google_developer_style_markdown.render import document, llms_full, llms_txt
from google_developer_style_markdown.sync import write_mirror

INDEX = 'https://developers.google.com/style'


def nav(*items: str) -> str:
    return f'<html><body><ul menu="_book">{"".join(items)}</ul></body></html>'


def heading(text: str) -> str:
    return (
        '<li class="devsite-nav-item devsite-nav-heading">'
        f'<div class="devsite-nav-title"><span class="devsite-nav-text">{text}</span></div></li>'
    )


def link(href: str, text: str) -> str:
    return (
        '<li class="devsite-nav-item">'
        f'<a href="{href}" class="devsite-nav-title">'
        f'<span class="devsite-nav-text">{text}</span></a></li>'
    )


def page(slug: str, *, title: str = 'Title', section: str = 'Documentation') -> Page:
    url = INDEX if slug == 'index' else f'{INDEX}/{slug}'
    return Page(slug=slug, title=title, url=url, section=section)


@pytest.mark.parametrize(
    ('href', 'expected'),
    [
        ('/style/lists', f'{INDEX}/lists'),
        ('lists', f'{INDEX}/lists'),
        ('/style/lists/', f'{INDEX}/lists'),
        ('/style/lists#nested', f'{INDEX}/lists'),
        ('/style/lists?hl=fr', f'{INDEX}/lists'),
        ('http://developers.google.com/style/lists', f'{INDEX}/lists'),
        ('  /style/lists  ', f'{INDEX}/lists'),
        ('/style', INDEX),
        ('/style/', INDEX),
        ('#anchor', INDEX),
        # Out of scope: another section, another host, a file, a foreign scheme.
        ('/terms/site-policies', None),
        ('/stylesheets/main', None),
        ('https://example.com/style/lists', None),
        ('/style/logo.png', None),
        ('mailto:someone@example.com', None),
        ('../../etc/passwd', None),
        ('/style/../../etc/passwd', None),
        ('//other.example.com/style/lists', None),
        ('/style//lists', f'{INDEX}/lists'),
    ],
)
def test_normalize(href, expected):
    assert normalize(href) == expected


@pytest.mark.parametrize(
    ('url', 'expected'),
    [
        (f'{INDEX}/lists', 'lists'),
        (INDEX, 'index'),
        (f'{INDEX}/word-list', 'word-list'),
        (f'{INDEX}/nested/page', 'nested-page'),
        # Only names that read as a slug are accepted. Scope is normalize's
        # job, so slug_for is only ever given a URL that already passed it.
        (f'{INDEX}/Lists', None),
        (f'{INDEX}/a_b', None),
    ],
)
def test_slug_for(url, expected):
    assert slug_for(url) == expected


@pytest.mark.parametrize(
    'href',
    [
        '/style/%2e%2e%2fetc',
        '/style/%2fetc%2fpasswd',
        '/style/%2e%2e%2f%2e%2e%2fterms/site-policies',
        '/style/lists%2f..%2f..%2fetc',
    ],
)
def test_normalize_never_leaves_the_scope_through_percent_encoding(href):
    # Reading the decoded path segments turns %2F and %2E%2E back into
    # separators inside one segment. That passed the scope test and then
    # escaped it when the URL was rebuilt, or raised out of yarl outright.
    url = normalize(href)
    assert url is None or url.startswith(f'{INDEX}/')


def test_parse_index_keeps_reading_order_and_sections():
    pages = parse_index(
        nav(
            heading('Introduction'),
            link('/style', 'About this guide'),
            heading('Punctuation'),
            link('/style/commas', 'Commas'),
            link('/style/commas#serial', 'Commas'),  # same page, already listed
            link('https://example.com/other', 'Elsewhere'),  # off-site
            link('/style/logo.png', 'Asset'),  # not a page
        )
    )
    assert [(p.slug, p.title, p.section) for p in pages] == [
        ('index', 'About this guide', 'Introduction'),
        ('commas', 'Commas', 'Punctuation'),
    ]
    assert pages[1].markdown_url == f'{INDEX}/commas.md.txt'


def test_parse_index_rejects_a_page_it_cannot_name_safely():
    with pytest.raises(SyncError, match='no pages found'):
        parse_index(nav(link('/style/Word_List', 'Word list')))


def test_parse_index_rejects_an_unrecognisable_page():
    with pytest.raises(SyncError, match='no table of contents'):
        parse_index('<html><body>redesigned</body></html>')


def test_parse_index_reports_a_file_name_collision():
    with pytest.raises(SyncError, match='both map to docs/a-b.md'):
        parse_index(nav(link('/style/a-b', 'One'), link('/style/a/b', 'Two')))


def test_document_keeps_the_body_and_records_its_source():
    text = document(page('lists', title='Lists: "and" more'), 'Body\ntext\n\n\n')
    assert text == (
        '---\ntitle: "Lists: \\"and\\" more"\nsource: https://developers.google.com/style/lists\n---\n\nBody\ntext\n'
    )


def test_llms_txt_is_an_index_grouped_the_way_google_groups_it():
    text = llms_txt(
        [
            page('index', title='About this guide', section='Introduction'),
            page('commas', title='Commas', section='Punctuation'),
            page('dashes', title='Dashes', section='Punctuation'),
        ]
    )
    assert text.startswith('# Google Developer Documentation Style Guide\n\n> ')
    assert '\n## Introduction\n\n- [About this guide](docs/index.md)\n' in text
    assert '\n## Punctuation\n\n- [Commas](docs/commas.md)\n- [Dashes](docs/dashes.md)\n' in text
    assert text.endswith('- [llms-full.txt](llms-full.txt): every page above, concatenated into one file\n')
    # An index, not a copy of the content.
    assert len(text.splitlines()) < 60


def test_llms_full_titles_every_document_without_rewriting_it():
    text = llms_full(
        [
            (page('markdown', title='Markdown versus HTML'), '# Markdown versus HTML\n\nUse either.'),
            (page('abbreviations', title='Abbreviations'), '# Abbreviations include acronyms and\nmore.'),
            (page('index', title='About this guide'), 'This guide provides guidelines.'),
        ]
    )

    # A standalone heading becomes the document title and is not repeated.
    assert f'\n# Markdown versus HTML\n\nSource: <{INDEX}/markdown>\n\nUse either.\n' in text
    assert text.count('# Markdown versus HTML') == 1
    # A heading that wraps stays glued to its continuation line.
    assert f'\n# Abbreviations\n\nSource: <{INDEX}/abbreviations>\n' in text
    assert '# Abbreviations include acronyms and\nmore.' in text
    # A page with no heading is titled from its navigation label.
    assert f'\n# About this guide\n\nSource: <{INDEX}>\n\nThis guide provides guidelines.\n' in text
    # Documents are separated, and the order given is the order emitted.
    assert text.count('\n---\n') == 3
    assert text.index('Use either.') < text.index('more.') < text.index('This guide provides')


def test_write_mirror_is_idempotent_and_drops_pages_the_guide_no_longer_lists(tmp_path):
    stale = tmp_path / 'docs' / 'removed-last-year.md'
    stale.parent.mkdir(parents=True)
    stale.write_text('---\ntitle: "Gone"\nsource: x\n---\n\nGone.\n', encoding='utf-8')
    keep_note = tmp_path / 'docs' / 'README.txt'
    keep_note.write_text('not a mirrored page', encoding='utf-8')

    fetched = [(page('lists', title='Lists'), '# Lists\n\nBody.'), (page('index', title='About'), 'Intro.')]
    report = write_mirror(fetched, tmp_path)

    assert report.removed == (stale,)
    assert not stale.exists()
    assert keep_note.exists()
    assert [path.name for path in report.documents] == ['index.md', 'lists.md']
    assert (tmp_path / 'llms.txt').exists()

    snapshot = {path: path.read_bytes() for path in tmp_path.rglob('*') if path.is_file()}
    assert write_mirror(fetched, tmp_path).removed == ()
    assert {path: path.read_bytes() for path in tmp_path.rglob('*') if path.is_file()} == snapshot


def test_llms_full_follows_file_name_order_not_slug_order(tmp_path):
    # headings-targets.md sorts before headings.md, because '-' precedes '.'.
    # Sorting the slugs instead reverses the pair, so the order is asserted on
    # a case where the two disagree.
    fetched = [
        (page('headings', title='Headings'), 'About headings.'),
        (page('headings-targets', title='Targets'), 'About targets.'),
    ]
    write_mirror(fetched, tmp_path)

    text = (tmp_path / 'llms-full.txt').read_text(encoding='utf-8')
    assert text.index('# Targets') < text.index('# Headings')


def test_write_mirror_writes_lf_endings_and_a_final_newline(tmp_path):
    write_mirror([(page('lists', title='Lists'), 'Body.')], tmp_path)
    for name in ('docs/lists.md', 'llms.txt', 'llms-full.txt'):
        raw = (tmp_path / name).read_bytes()
        assert b'\r' not in raw
        assert raw.endswith(b'\n') and not raw.endswith(b'\n\n')
