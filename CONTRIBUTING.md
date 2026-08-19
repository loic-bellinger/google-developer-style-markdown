# Contributing

Thanks for helping. This is a small project; the whole setup is two commands.

## Getting started

```bash
uv sync
uv run pre-commit install
```

`pre-commit install` is optional but recommended: it installs both the
`pre-commit` and `commit-msg` hooks, which run the same Ruff, rumdl, and
commit-message checks that CI runs, from the versions pinned in `uv.lock`.

## Before opening a pull request

```bash
uv run ruff check
uv run ruff format
uv run rumdl check
uv run pytest
```

## Do not edit the generated files

`docs/`, `llms.txt`, and `llms-full.txt` are written by the synchronizer and
overwritten on every run. Changes to them belong in `src/`. To see the effect
of a change:

```bash
uv run gdsm
git diff
```

Please do not include a full re-sync in a pull request that is about the code —
it buries the change under hundreds of lines. The scheduled workflow will pick
the content up on its own.

## Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: discover pages from the table of contents
fix: keep trailing spaces in mirrored Markdown
docs: explain why .md.txt is used
chore(deps): bump aiohttp
```

Commitizen checks this locally through the `commit-msg` hook, and CI checks
every commit in a pull request. `uv run cz commit` walks you through it if you
would rather not remember the format.

## Releases

Versions follow [semantic versioning](https://semver.org/), driven by the
commit history:

```bash
uv run cz bump   # updates the version, writes CHANGELOG.md, tags
git push --follow-tags
```
