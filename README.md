# Google developer documentation style guide as Markdown and llms.txt

[![CI status][badge-ci]][actions-ci]
[![Sync status][badge-sync]][actions-sync]
[![Code license: MIT][badge-mit]](LICENSE)
[![Content license: CC BY 4.0][badge-ccby]][ccby]

This repository mirrors the [Google developer documentation style
guide][guide] page for page, as plain Markdown and [llms.txt][llmstxt]. Every
page is reproduced verbatim and resynchronized every week—what you read is
what Google wrote.

Hand the guide to a large language model (LLM) and style review stops being
guesswork. The model quotes the rule it applies and the page the rule comes
from, instead of paraphrasing the guide from training data. The following
exchange shows the difference:

```text
You:   The guide says em dashes take spaces around them, right?
Model: No—an em dash takes no space before or after it.
       Source: https://developers.google.com/style/dashes
```

You can also distill the guide into a reusable technical-writing skill, or
read and search it offline, one file per page. The following table shows the
three forms the mirror takes:

| File | Size | What it is for |
| ---- | ---- | -------------- |
| [`llms.txt`](llms.txt) | 4&nbsp;KB, ~1k tokens | The index: every page as a link, grouped and ordered the way Google's own table of contents groups and orders it. Read this first. |
| [`llms-full.txt`](llms-full.txt) | 515&nbsp;KB, ~130k tokens | The substance: the whole guide in one file, ready to drop into an LLM's context window or to distill into a skill. |
| [`docs/`](docs) | 70 files | One Markdown file per page, verbatim, each recording the URL it came from. |

Download the files straight from `main`, without cloning:

```bash
BASE=https://raw.githubusercontent.com/loic-bellinger/google-developer-style-markdown/main
curl -O $BASE/llms.txt
curl -O $BASE/llms-full.txt
```

**This project is not affiliated with, sponsored by, or endorsed by Google.**

[guide]: https://developers.google.com/style/
[llmstxt]: https://llmstxt.org/

## Distill it into an Agent Skill

`llms-full.txt` is the file to start from when you write an [Agent
Skill][skill]. It holds the whole guide in reading order, with the source URL
of every page, so a distilled `SKILL.md` can cite the page behind each rule.
Spend the 130k tokens once, keep the few thousand you distill, and point the
skill back here for the rest.

Open an issue to say how you used it, and link your skill or your repository.
If enough people share one, the links move out of this README and into a
`skills/` directory.

[skill]: https://code.claude.com/docs/en/skills

## Why you can trust this mirror

Google already publishes every page of the guide as Markdown: append
`.md.txt` to any page URL and the server returns the source. This mirror
downloads that source, so nothing is scraped, converted, or reconstructed
from HTML.

*   **Verbatim.** Each page is reproduced unchanged: no reflowing, no
    reformatting, no linting, no stripping of notices. The mirror adds only a
    front matter block recording the title and source URL of each page.
*   **A deterministic diff.** Two runs against an unchanged guide produce
    identical bytes. Every diff in this repository is therefore a change
    Google made, never noise from the mirror, so `git log` reads as a
    changelog finer-grained than the guide's own what's-new page.
*   **Refreshed weekly.** GitHub Actions resynchronizes every Monday, only
    after the test suite passes. The run is all-or-nothing—one failed
    download and nothing is written—and it stops instead of pushing if it
    would delete more than a quarter of the pages.

## What the mirror doesn't carry

*   **Images and diagrams.** They aren't covered by the content license, and
    Google's own Markdown carries almost none of them. What survives points
    at Google.
*   **The Android and Cloud markers.** The guide flags platform-specific
    terms with CSS-only icons. The icons carry no text, so Google's own
    Markdown drops them before the mirror ever downloads the page. Check the
    source page when a term's scope matters.
*   **Definition lists.** Markdown has no syntax for them, so the word list
    arrives as prose. Cross-references to a term still work: they point at
    Google, where the anchor exists.
*   **Some page titles.** Of the 70 pages, 19 don't open with a usable
    heading. The navigation label stands in, recorded in each document's
    front matter.
*   **The changelog.** The what's-new page dates superseded wording—advice a
    model shouldn't read alongside the guidance that replaced it—so
    `llms-full.txt` leaves that page out. The page is still mirrored in
    `docs/` and still indexed in `llms.txt`.
*   **Relative links.** Links between pages point at `developers.google.com`,
    because that is what Google's Markdown contains.

This is a mirror, not a fork: report problems with the _content_ to Google,
not here.

## Run the sync yourself

The sync requires [uv][uv] and Python 3.14.

```bash
git clone https://github.com/loic-bellinger/google-developer-style-markdown
cd google-developer-style-markdown
uv sync

uv run gdsm          # refresh docs/, llms.txt, and llms-full.txt
uv run gdsm --help   # options: --output-dir, --concurrency, --timeout
```

A failed run leaves the mirror untouched, so you can always run it again.

[uv]: https://docs.astral.sh/uv/

## License and attribution

Two different things live in this repository, under two different terms.

**The code**—everything under `src/` and `tests/`, and the configuration—is
released under the [MIT License](LICENSE).

**The mirrored guide**—everything under `docs/`, and `llms-full.txt`—is
Google's, not this project's, and is _not_ MIT. Per the
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
[apache]: https://www.apache.org/licenses/LICENSE-2.0

## Contributing

For the two-command setup and the internals—how the sync works, the
architecture, what the mirror changes about Google's Markdown (almost
nothing), and the design decisions behind its limits—see
[CONTRIBUTING.md](CONTRIBUTING.md).

[badge-ci]: https://github.com/loic-bellinger/google-developer-style-markdown/actions/workflows/ci.yml/badge.svg
[badge-sync]: https://github.com/loic-bellinger/google-developer-style-markdown/actions/workflows/sync.yml/badge.svg
[badge-mit]: https://img.shields.io/badge/code-MIT-blue
[badge-ccby]: https://img.shields.io/badge/content-CC%20BY%204.0-blue
[actions-ci]: https://github.com/loic-bellinger/google-developer-style-markdown/actions/workflows/ci.yml
[actions-sync]: https://github.com/loic-bellinger/google-developer-style-markdown/actions/workflows/sync.yml
[ccby]: https://creativecommons.org/licenses/by/4.0/
