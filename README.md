# google-developer-style-markdown

The [Google developer documentation style guide][guide] as plain Markdown and
[llms.txt][llmstxt], ready to hand to a model. Reproduced verbatim,
resynchronized every week, byte-identical on every run that finds nothing
changed.

| File | Size | What it is for |
| ---- | ---- | -------------- |
| [`llms.txt`](llms.txt) | 4 KB, ~1k tokens | The index: every page as a link, grouped and ordered the way Google's own table of contents groups and orders it. Read this first. |
| [`llms-full.txt`](llms-full.txt) | 515 KB, ~130k tokens | The substance: the whole guide in one file, ready to drop into a context window. |
| [`docs/`](docs) | 70 files | One Markdown file per page, verbatim, each recording the URL it came from. |

```bash
BASE=https://raw.githubusercontent.com/loic-bellinger/google-developer-style-markdown/main
curl -O $BASE/llms.txt
curl -O $BASE/llms-full.txt
```

**This project is not affiliated with, sponsored by, or endorsed by Google.**

[guide]: https://developers.google.com/style/
[llmstxt]: https://llmstxt.org/

## Why you can trust what you feed the model

*   **Verbatim.** Google publishes every page of the guide as Markdown, and
    this mirror reproduces it unchanged: no reflowing, no reformatting, no
    linting, no stripping of notices. What you read is what Google wrote.
*   **A deterministic diff.** Two runs against an unchanged guide produce
    identical bytes. Every diff in this repository is therefore a change Google
    made, never noise from the mirror, so `git log` reads as the changelog the
    guide does not publish.
*   **Refreshed weekly.** GitHub Actions resynchronizes every Monday, only
    after the test suite passes, and stops rather than push if a run would
    delete more than a quarter of the pages.

## Why `.md.txt` and not scraping

Google already publishes every page of the guide as Markdown. Append `.md.txt`
to any page URL and the server returns the source:

```text
https://developers.google.com/style/markdown
https://developers.google.com/style/markdown.md.txt
```

So there is nothing to scrape. Converting the rendered HTML back into Markdown
would mean guessing at emphasis, tables, admonitions, and code fences that
Google already got right, and every guess would show up as noise in the diff of
the next sync. The only page fetched as HTML is the entry page, and only to
read its table of contents.

## How the sync works

1.  Download the entry page and read its table of contents.
1.  Download the `.md.txt` source of every page it lists, at most eight
    connections at a time, 30 seconds per request.
1.  If *any* page failed, stop. Nothing is written.
1.  Write `docs/<page>.md` for every page.
1.  Delete any `docs/*.md` the guide no longer lists.
1.  Regenerate `llms.txt` and `llms-full.txt` from the same downloads.

Steps 3 and 5 are the interesting pair. Deleting a page is only safe because
the run is all-or-nothing: a page that could not be downloaded aborts the sync,
so a network failure can never be mistaken for a page Google removed.

A single failed request aborts the run, on purpose. A failed run leaves the
mirror untouched; run it again.

## Architecture

Four small modules, each doing one thing:

```text
src/google_developer_style_markdown/
├── discovery.py   entry page HTML -> the pages of the guide
├── sync.py        download every page, write the mirror, delete what is gone
├── render.py      pure functions: a document, llms.txt, llms-full.txt
└── cli.py         argument parsing and exit codes
```

The interesting properties live in two places. `discovery.normalize` decides
what belongs to the guide, and `render` is pure: given the same downloads it
always produces the same bytes.

### Discovery

The entry page is parsed with [selectolax][selectolax] (Lexbor), URLs are
handled with [yarl][yarl]—the same URL type aiohttp speaks—and the pages
are read from the guide's own table of contents—the `ul[menu="_book"]`
navigation DevSite renders on every page. There is no crawl: links are never
followed, so the program cannot wander into the rest of
`developers.google.com`, and new pages are still picked up automatically as
soon as Google lists them.

Each reference is resolved against the entry page and then either canonicalized
or dropped. It is kept when the same host serves it, it lives under `/style`,
and it does not name a file. Trailing slashes, empty segments, fragments, and
query strings collapse, so `/style/lists/`, `/style//lists`, and
`/style/lists#nested` all arrive as one entry. The exhaustive table is
`test_normalize`, which CI keeps honest.

A page is mirrored under the name Google serves it as, minus the `.txt`:
`…/style/lists.md.txt` becomes `docs/lists.md`, and the guide's entry page,
served at `…/style.md.txt`, becomes `docs/style.md`. There is no naming scheme
to keep in step with anything.

Scope is decided on the *encoded* path and the encoding is carried through, so
a page whose name legitimately contains one is kept: `/style/caf%C3%A9` would
be mirrored as `docs/café.md`. Decoding before that decision is what lets
`%2F` and `%2E%2E` become separators again inside a single segment, so that
`/style/%2e%2e%2fetc` reads as a page of the guide and then turns out to be
`/etc`.

What a name decodes into is settled one step later. A `Page` refuses at
construction any URL that does not name a single, ordinary file—an empty
name, a leading dot, or a separator—so "this can be written under `docs/`"
is true of every instance rather than checked at each call site. Two pages that
would claim the same file name abort the run.

[selectolax]: https://github.com/rushter/selectolax
[yarl]: https://yarl.aio-libs.org/

### What the mirror changes about Google's Markdown

As little as possible, and only what is deterministic:

*   A single trailing newline is added. The `.md.txt` sources end without one.
*   A YAML front matter block records the page title and its source URL.
*   In `llms-full.txt` only, a page's leading `#` heading is *moved* ahead of
    the source line so each document starts with a title. A heading that wraps
    onto the next line—a few pages of the guide do this—is left where it is,
    and the document is titled with its navigation label instead, so a sentence
    is never split.

Nothing else is touched: no reflowing, no reformatting, no removal of trailing
spaces (Google's Markdown uses significant ones), no stripping of notices. No
linter runs on it either: [rumdl][rumdl] enforces [Google's own Markdown
style][docguide] on the files this repository writes by hand, and `docs/` is
excluded in `.rumdl.toml`, because `rumdl fmt` would rewrite bullet characters,
list spacing, the trailing spaces Google uses as line breaks, and the
indentation inside its code samples. Ruff is scoped the same way, for the same
reason.

[rumdl]: https://github.com/rvben/rumdl
[docguide]: https://google.github.io/styleguide/docguide/style.html

## Run it yourself

Requires [uv][uv] and Python 3.14.

```bash
git clone https://github.com/loic-bellinger/google-developer-style-markdown
cd google-developer-style-markdown
uv sync

uv run gdsm                 # refresh docs/, llms.txt and llms-full.txt
uv run gdsm --help          # options: --output-dir, --concurrency, --timeout
uv run gdsm -v              # log every request
uv run pytest               # tests
uv run ruff check           # lint Python
uv run rumdl check          # lint the hand-written Markdown
uv run pre-commit install   # optional: run every check here before each commit
```

[uv]: https://docs.astral.sh/uv/

## Repository layout

| Path | Contents |
| ---- | -------- |
| [`docs/`](docs) | The mirrored guide, one file per page (generated) |
| [`llms.txt`](llms.txt) | Index, llms.txt v2 format (generated) |
| [`llms-full.txt`](llms-full.txt) | Every page but the changelog, concatenated (generated) |
| [`src/`](src/google_developer_style_markdown) | The synchronizer |
| [`tests/`](tests) | URL handling, naming, rendering, deletion |
| [`.github/workflows/`](.github/workflows) | `ci.yml` and `sync.yml` |
| [`.rumdl.toml`](.rumdl.toml) | Markdown style for the hand-written files |

## GitHub Actions

**CI** (`ci.yml`) runs on every push and pull request: Ruff, rumdl, and the
tests. On pull requests it also checks that commit messages follow
[Conventional Commits][conventional].

**Sync** (`sync.yml`) runs every Monday at 06:17 UTC, and on demand. It does the
cheap, safe things first, so that a robot can never publish a broken commit:

1.  Run the full CI workflow. Broken code never gets to touch the mirror.
1.  Fetch the guide and regenerate everything.
1.  Refuse to continue if the run would delete more than a quarter of the
    documents. Losing a few pages is normal; losing a quarter of them means
    something is wrong upstream and a human should look.
1.  Commit and push **only if** something actually changed, as
    `github-actions[bot]`, with no empty commit and no secrets beyond the
    default `GITHUB_TOKEN`.

To trigger it yourself: **Actions → Sync → Run workflow**, or

```bash
gh workflow run sync.yml
```

[conventional]: https://www.conventionalcommits.org/

## Licensing and attribution

Two different things live in this repository, under two different terms.

**The code**—everything under `src/` and `tests/`, and the configuration—is
released under the [MIT License](LICENSE).

**The mirrored guide**—everything under `docs/`, and `llms-full.txt`—is
Google's, not ours, and is *not* MIT. Per the
[Google Developers Site Policies][policies], the content of those pages is
licensed under [CC BY 4.0][ccby] and the code samples under
[Apache 2.0][apache]. Google's trademarks and brand features are not included
in that license.

Every mirrored document records the URL it was reproduced from in its front
matter, and `llms.txt` and `llms-full.txt` carry the attribution notice Google
asks for. If you reuse this content, keep the attribution and the links back to
the source pages.

This project is not affiliated with, sponsored by, or endorsed by Google.
"Google" is a trademark of Google LLC.

[policies]: https://developers.google.com/terms/site-policies
[ccby]: https://creativecommons.org/licenses/by/4.0/
[apache]: https://www.apache.org/licenses/LICENSE-2.0

## Known limitations

*   **Text only.** Images, diagrams, and other assets are not mirrored: they
    are not covered by the content license, and Google's own Markdown carries
    almost none of them either—five image references against 56 `<img>`
    elements in the rendered HTML. What survives points at Google.
*   **CSS-only markers are lost upstream.** The guide flags Android-specific
    and Cloud-specific guidance with small logos, which the HTML renders as
    empty `<span class="icon-android">` elements styled entirely in CSS. They
    carry no text, so Google's own Markdown has nothing to convert and drops
    them: 26 Android and eight Cloud markers disappear from the word list, and
    the sentences introducing them on the entry page now begin *"precedes terms
    and guidelines specific to…"* with nothing in front. This happens before
    the mirror sees the page, and putting the markers back would mean inventing
    content. Check the source page when a term's scope matters.
*   **Definition lists do not survive.** The guide uses `<dl>` for
    term-and-definition pairs, and the word list is one long example. Markdown
    has no syntax for them: 31 in the rendered HTML, none in the Markdown, so
    the terms arrive as prose. Cross-references to a term still work, because
    they point at Google where the anchor exists; inside `docs/` there is
    nothing for a fragment to attach to.
*   **Titles live outside the Markdown.** 19 of the 70 pages do not open with
    a usable heading, and 15 of them carry no `#` heading anywhere: DevSite
    renders the title from page metadata the `.md.txt` does not include. The
    navigation label stands in, recorded in the front matter of every document
    and used as the heading in `llms-full.txt`.
*   **Absolute cross-references.** Links between pages point at
    `developers.google.com`, because that is what Google's Markdown contains.
    Rewriting them to point inside `docs/` would be a change to the content.
*   **No retries.** A single failed request aborts the run, on purpose.
*   **Coupled to the DevSite navigation.** Discovery reads the
    `ul[menu="_book"]` list. If Google redesigns it, the sync fails loudly
    rather than silently mirroring less. The pages the guide links to in its
    prose are deliberately not followed, and nothing is lost by it. Of the 17
    such URLs absent from the table of contents, 16 are `301` redirects to
    pages already mirrored and the last is a broken link in Google's own
    documentation. Sixteen of the 17 have no `.md.txt` at all.
*   **No conditional requests.** Google serves the guide with
    `Cache-Control: no-cache` and no `ETag`, so every run downloads every page.
    It is about 800 KB.
*   **Not a fork.** This is a mirror. Report problems with the *content* to
    Google, not here.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
