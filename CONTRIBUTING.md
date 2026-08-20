# Contributing

Thanks for helping. This is a small project; the whole setup is two commands.

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

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: discover pages from the table of contents
fix: keep trailing spaces in mirrored Markdown
docs: explain why .md.txt is used
chore(deps): bump aiohttp
```

Commitizen checks this locally through the `commit-msg` hook, and CI checks
every commit in a pull request. If you would rather not remember the format,
`uv run cz commit` prompts for each part of the message.

## Releases

Versions follow [semantic versioning](https://semver.org/), driven by the
commit history:

```bash
uv run cz bump   # updates the version, writes CHANGELOG.md, tags
git push --follow-tags
```
