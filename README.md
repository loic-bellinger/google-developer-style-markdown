# google-developer-style-markdown

A deterministic, automatically synchronized Markdown mirror of the
[Google developer documentation style guide][guide], published as plain
Markdown files plus an [llms.txt][llmstxt] index.

*   `docs/` — one Markdown file per page of the guide, reproduced verbatim.
*   `llms.txt` — the index: structure and navigation, small enough to keep in
    context, following the [llms.txt][llmstxt] v2 format.
*   `llms-full.txt` — the substance: every page concatenated, ready to drop into
    a context window.

The mirror is refreshed weekly by GitHub Actions. Every run either reproduces
the previous output byte for byte, or produces a diff that shows exactly what
Google changed.

**This project is not affiliated with, sponsored by, or endorsed by Google.**

[guide]: https://developers.google.com/style/
[llmstxt]: https://llmstxt.org/

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
handled with [yarl][yarl] — the same URL type aiohttp speaks — and the pages
are read from the guide's own table of contents — the `ul[menu="_book"]`
navigation DevSite renders on every page. There is no crawl: links are never
followed, so the program cannot wander into the rest of
`developers.google.com`, and new pages are still picked up automatically as
soon as Google lists them.

Each reference is resolved and then either canonicalised or dropped:

| Reference               | Result          | Why                                           |
| ----------------------- | --------------- | --------------------------------------------- |
| `lists`, `/style/lists` | `…/style/lists` | Resolved against the entry page               |
| `/style/lists/`         | `…/style/lists` | Trailing slash removed so `.md.txt` resolves  |
| `/style//lists`         | `…/style/lists` | Empty path segments collapse                  |
| `/style/lists#nested`   | `…/style/lists` | A fragment selects a position, not a document |
| `/style/lists?hl=fr`    | `…/style/lists` | A query selects a locale, not a document      |
| `/style/%2fetc%2f…`     | dropped         | A percent-encoded path is refused, not decoded |
| `/style`, `/style/`     | `…/style`       | The entry page, mirrored as `docs/style.md`   |
| `/terms/site-policies`  | dropped         | Outside `/style`                              |
| `https://example.com/…` | dropped         | Another host                                  |
| `/style/logo.png`       | dropped         | A file, not a page                            |

A page is mirrored under the name Google serves it as, minus the `.txt`:
`…/style/lists.md.txt` becomes `docs/lists.md`, and the guide's entry page,
served at `…/style.md.txt`, becomes `docs/style.md`. There is no naming scheme
to keep in step with anything.

A `Page` refuses at construction any URL that does not name a single, ordinary
file — an empty name, a leading dot, or a separator that a percent-encoded
segment decoded back into — so "this can be written under `docs/`" is true of
every instance rather than checked at each call site. Two pages that would
claim the same file name abort the run.

[selectolax]: https://github.com/rushter/selectolax
[yarl]: https://yarl.aio-libs.org/

### What the mirror changes about Google's Markdown

As little as possible, and only what is deterministic:

*   A single trailing newline is added. The `.md.txt` sources end without one.
*   A YAML front matter block records the page title and its source URL.
*   In `llms-full.txt` only, a page's leading `#` heading is *moved* above the
    source line so each document starts with a title. A heading that wraps onto
    the next line — a few pages of the guide do this — is left where it is, and
    the document is titled with its navigation label instead, so a sentence is
    never split.

Nothing else is touched: no reflowing, no reformatting, no removal of trailing
spaces (Google's Markdown uses significant ones), no stripping of notices.
No linter or formatter in this repository ever touches them, for the same
reason — see [Markdown quality](#markdown-quality).

## Installation

Requires [uv][uv] and Python 3.14.

```bash
git clone https://github.com/loic-bellinger/google-developer-style-markdown
cd google-developer-style-markdown
uv sync
```

[uv]: https://docs.astral.sh/uv/

## Local commands

```bash
uv run gdsm                 # refresh docs/, llms.txt and llms-full.txt
uv run gdsm --help          # options: --output-dir, --concurrency, --timeout
uv run gdsm -v              # log every request
uv run pytest               # tests
uv run ruff check           # lint Python
uv run ruff format          # format Python
uv run rumdl check          # lint the hand-written Markdown
uv run pre-commit install   # optional: run all of the above before each commit
```

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

The result is idempotent. Two runs against an unchanged guide produce identical
bytes: UTF-8, LF endings, one trailing newline, stable ordering (`llms.txt`
follows Google's table of contents, `llms-full.txt` follows file name order).

There are no retries yet. A failed run leaves the mirror untouched; run it
again.

## Repository layout

```text
docs/                    the mirrored guide, one file per page (generated)
llms.txt                 index, llms.txt v2 format (generated)
llms-full.txt            every page concatenated (generated)
src/…/                   the synchronizer
tests/                   tests for URL handling, naming, rendering, deletion
.github/workflows/       ci.yml and sync.yml
.rumdl.toml              Markdown style for the hand-written files
```

## GitHub Actions

Two workflows:

*   **CI** (`ci.yml`) runs on every push and pull request: Ruff, rumdl, and the
    tests. On pull requests it also checks that commit messages follow
    [Conventional Commits][conventional].
*   **Sync** (`sync.yml`) runs every Monday at 06:17 UTC, and on demand.

Sync deliberately does the cheap, safe things first, so that a broken commit
can never be published by a robot:

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

## Markdown quality

[rumdl][rumdl] enforces [Google's own Markdown style][docguide] on the files
this repository writes by hand. `docs/` is excluded in `.rumdl.toml`, and the
numbers say why: linting it reports 4465 violations across the 70 files, and
`rumdl fmt` rewrites 67 of them. Among other things it reads the front matter
`title:` as a top-level heading, so it demotes every page's real `#` heading to
`##` — a silent rewrite of someone else's document structure.

Exclusions are used rather than an allowlist, so a new hand-written file is
linted by default instead of being silently skipped. `llms.txt` and
`llms-full.txt` need no entry: rumdl only discovers `.md` and `.markdown` files.

Ruff is scoped for the same reason, and it is not theoretical: `ruff format`
formats Python code blocks inside Markdown files, so a plain `ruff format .`
rewrites Google's code samples in *our* style — including our quote preference.
`docs/` is therefore listed in `extend-exclude`. (The guide happens to contain
no Python samples today; the exclusion is what keeps that from becoming a
problem the week it does.)

Inside our own Markdown the two tools have to be made to agree, because both
have an opinion about Python code blocks. Ruff formats them to 120 columns,
while rumdl's line-length rule checks code blocks at 80, so code blocks are
exempted from `MD013` — which leaves the 80-column rule where the docguide means
it, on prose.

Then rumdl is handed the blocks outright, through its `code-block-tools`
feature:

```toml
[code-block-tools.languages.python]
lint = ["ruff:check"]
format = ["ruff:format"]
```

This is not redundant with the Ruff hook. `ruff check` cannot see code blocks at
all — it reports *No Python files found* for a Markdown file — so an unused
import or a syntax error in a documented example would otherwise ship unnoticed.
The formatting side runs `ruff format -`, which resolves this project's
configuration and therefore produces exactly what `ruff format README.md` would;
the two cannot disagree.

One sharp edge is worth knowing: `on-missing-tool-binary` defaults to `ignore`,
which silently turns the whole feature off when `ruff` is not on `PATH`. It is
set to `fail` here, and the rumdl pre-commit hook carries its own pinned copy of
Ruff, so the checks cannot quietly stop running.

[rumdl]: https://github.com/rvben/rumdl
[docguide]: https://google.github.io/styleguide/docguide/style.html

## Licensing and attribution

Two different things live in this repository, under two different terms.

**The code** — everything under `src/` and `tests/`, and the configuration — is
released under the [MIT License](LICENSE).

**The mirrored guide** — everything under `docs/`, and `llms-full.txt` — is
Google's, not ours, and is *not* MIT. Per the
[Google Developers Site Policies][policies], the content of those pages is
licensed under [CC BY 4.0][ccby] and the code samples under
[Apache 2.0][apache]. Google's trademarks and brand features are not included
in that licence.

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

*   **Text only.** Images, diagrams, and other assets referenced by the guide
    are not mirrored — they are not covered by the content licence. Links to
    them still point at Google.
*   **Absolute cross-references.** Links between pages point at
    `developers.google.com`, because that is what Google's Markdown contains.
    Rewriting them to point inside `docs/` would be a change to the content.
*   **No retries.** A single failed request aborts the run, on purpose. Retries
    and backoff are the next thing to add.
*   **Coupled to the DevSite navigation.** Discovery reads the
    `ul[menu="_book"]` list. If Google redesigns it, the sync fails loudly
    rather than silently mirroring less. The pages the guide links to in its
    prose are deliberately not followed: all 17 such URLs that are absent from
    the table of contents turn out to be `301` redirects to pages already
    mirrored, and 16 of them have no `.md.txt` at all.
*   **No conditional requests.** Google serves the guide with
    `Cache-Control: no-cache` and no `ETag`, so every run downloads every page.
    It is about 800 KB.
*   **Not a fork.** This is a mirror. Report problems with the *content* to
    Google, not here.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
