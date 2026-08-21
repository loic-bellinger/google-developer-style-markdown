# Contributing

Thanks for helping. This is a small project; the whole setup is two commands.
This page also holds everything the README keeps out of a newcomer's way: how
the sync works, the architecture, and the design decisions behind the
mirror's limits.

## Get started

```bash
uv sync
uv run pre-commit install
```

`pre-commit install` is optional. Run it to catch locally what CI would catch
later: it installs the `pre-commit` and `commit-msg` hooks from the versions
pinned in `uv.lock`, and they run the same Ruff, rumdl, and commit-message
checks.

## Before opening a pull request

```bash
uv run ruff check
uv run ruff format
uv run rumdl check
uv run pytest
```

## Don't edit the generated files

`docs/`, `llms.txt`, and `llms-full.txt` are written by the synchronizer and
overwritten on every run. Changes to them belong in `src/`. To see the effect
of a change:

```bash
uv run gdsm
git diff
```

Don't include a full resync in a pull request that is about the code—it buries
the change under hundreds of lines. The scheduled workflow picks the content up
on its own.

## Commit messages

Commit messages follow
[Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: discover pages from the table of contents
fix: keep trailing spaces in mirrored Markdown
docs: explain why .md.txt is used
chore(deps): bump aiohttp
```

Commitizen checks this format locally through the `commit-msg` hook, and CI checks
every commit in a pull request. If you would rather not remember the format,
`uv run cz commit` prompts for each part of the message.

## Releases

Versions follow [semantic versioning](https://semver.org/), driven by the
commit history:

```bash
uv run cz bump   # updates the version, writes CHANGELOG.md, tags
git push --follow-tags
```

## How the sync works

1.  Download the entry page and read its table of contents.
1.  Download the `.md.txt` source of every page it lists, at most 8
    connections at a time, 30 seconds per request.
1.  If _any_ page failed, stop. Nothing is written.
1.  Write `docs/<page>.md` for every page.
1.  Delete any `docs/*.md` the guide no longer lists.
1.  Regenerate `llms.txt` and `llms-full.txt` from the same downloads.

Steps 3 and 5 are the pair that matters. Deleting a page is only safe because
the run is all-or-nothing: a page that can't be downloaded stops the sync, so
a network failure can never be mistaken for a page Google removed. A failed
run leaves the mirror untouched. Run it again.

## Why `.md.txt` sources and not scraping

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

Discovery parses the entry page with [selectolax][selectolax] (Lexbor),
handles URLs with [yarl][yarl]—the same URL type aiohttp speaks—and reads the
pages from the guide's own table of contents, the `ul[menu="_book"]`
navigation DevSite renders on every page. There is no crawl: links are never
followed, so the sync can't reach the rest of `developers.google.com`, and it
picks up a page Google adds later as soon as the table of contents lists it.

Each reference is resolved against the entry page and then either canonicalized
or dropped. It is kept when the same host serves it, it lives under `/style`,
and it doesn't name a file. Trailing slashes, empty segments, fragments, and
query strings collapse, so `/style/lists/`, `/style//lists`, and
`/style/lists#nested` all arrive as one entry. The exhaustive table is the
`test_normalize` test, which CI runs on every push.

A page is mirrored under the name Google serves it as, minus the `.txt`:
`/style/lists.md.txt` becomes `docs/lists.md`, and the guide's entry page,
served at `/style.md.txt`, becomes `docs/style.md`. There is no naming scheme
to keep in step with anything.

Scope is decided on the _encoded_ path and the encoding is carried through, so
a page whose name legitimately contains one is kept: `/style/caf%C3%A9` would
be mirrored as `docs/café.md`. Decoding before that decision is what lets
`%2F` and `%2E%2E` become separators again inside a single segment, so that
`/style/%2e%2e%2fetc` reads as a page of the guide and then turns out to be
`/etc`.

What a name decodes into is settled one step later. A `Page` object rejects at
construction any URL that doesn't name a single, ordinary file—an empty name,
a leading dot, or a separator—so "this can be written under `docs/`" is true
of every instance rather than checked at each call site. Two pages that would
claim the same filename stop the run.

[selectolax]: https://github.com/rushter/selectolax
[yarl]: https://yarl.aio-libs.org/

### What the mirror changes about Google's Markdown

The mirror changes as little as possible, and only what is deterministic:

*   A single trailing newline is added. The `.md.txt` sources end without one.
*   A YAML front matter block records the page title and its source URL.
*   In `llms-full.txt` only, a page's leading `#` heading is _moved_ ahead of
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

## Repository layout

The following table shows where everything lives:

| Path | Contents |
| ---- | -------- |
| [`docs/`](docs) | The mirrored guide, one file per page (generated) |
| [`llms.txt`](llms.txt) | Index, llms.txt v2 format (generated) |
| [`llms-full.txt`](llms-full.txt) | Every page but the changelog, concatenated (generated) |
| [`src/`](src/google_developer_style_markdown) | The synchronizer |
| [`tests/`](tests) | URL handling, naming, rendering, deletion |
| [`.github/workflows/`](.github/workflows) | `ci.yml` and `sync.yml` |
| [`.rumdl.toml`](.rumdl.toml) | Markdown style for the files written by hand |

## GitHub Actions

**CI** (`ci.yml`) runs on every push and pull request: Ruff, rumdl, and the
tests. On pull requests it also checks that commit messages follow
Conventional Commits.

**Sync** (`sync.yml`) runs every Monday at 06:17 UTC, and on demand. It does the
cheap, safe things first, so that an automated run can never publish a broken
commit:

1.  Run the full CI workflow. Broken code never reaches the mirror.
1.  Fetch the guide and regenerate everything.
1.  Refuse to continue if the run would delete more than a quarter of the
    documents. Losing a few pages is normal; losing a quarter of them means
    something is wrong upstream, and a human has to look.
1.  Commit and push _only if_ something actually changed, as
    `github-actions[bot]`, with no empty commit and no secrets beyond the
    default `GITHUB_TOKEN`.

To trigger the sync yourself, select **Actions > Sync > Run workflow**, or
run the following command:

```bash
gh workflow run sync.yml
```

## Design decisions behind the limits

The README lists what the mirror doesn't carry. These are the decisions
behind that list, and the evidence for them:

*   **Text only.** Images and other assets aren't covered by the content
    license, and Google's own Markdown carries almost none of them—5 image
    references against 56 `<img>` elements in the rendered HTML.
*   **CSS-only markers are lost upstream.** The Android-specific and
    Cloud-specific markers are empty `<span class="icon-android">` elements
    styled entirely in CSS. They carry no text, so Google's own Markdown has
    nothing to convert and drops them: 26 Android and 8 Cloud markers
    disappear from the word list. This happens before the mirror sees the
    page, and putting the markers back would mean inventing content.
*   **Definition lists don't survive.** The guide uses `<dl>` for
    term-and-definition pairs: 31 in the rendered HTML, none in the Markdown.
    Inside `docs/` there is nothing for a term's fragment anchor to attach to,
    which is why cross-references keep pointing at Google.
*   **Titles live outside the Markdown.** Of the 70 pages, 19 don't open with
    a usable heading, and 15 of them carry no `#` heading anywhere: DevSite
    renders the title from page metadata the `.md.txt` doesn't include. The
    navigation label stands in.
*   **No retries.** A single failed request stops the run, on purpose: the
    all-or-nothing rule is what makes deletion safe.
*   **No conditional requests.** Google serves the guide with
    `Cache-Control: no-cache` and no `ETag`, so every run downloads every
    page. It's about 800&nbsp;KB.
*   **Coupled to the DevSite navigation.** Discovery reads the
    `ul[menu="_book"]` list. If Google redesigns it, the sync fails loudly
    rather than silently mirroring less. The pages the guide links to in its
    prose are deliberately not followed, and nothing is lost by it. Of the 17
    such URLs absent from the table of contents, 16 are `301` redirects to
    pages already mirrored, and the last is a broken link in Google's own
    documentation. Sixteen of the 17 have no `.md.txt` at all.
