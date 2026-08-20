"""Deterministic Markdown mirror of Google's developer documentation style guide.

Google serves every page of the guide, published at
<https://developers.google.com/style/>, as plain Markdown at the same URL with a
`.md.txt` suffix. This package therefore never reconstructs Markdown from HTML:
it parses the entry page only to read the table of contents, then downloads the
Markdown Google already publishes.
"""

from importlib.metadata import version

__all__ = ['SyncError', '__version__']

__version__ = version(__name__)
"""Read from the installed package, so pyproject.toml stays the only copy."""


class SyncError(RuntimeError):
    """The guide could not be mirrored.

    Raised for every failure the user can act on: an unreachable page, an entry
    page whose structure is no longer recognized, or a mirrored document that
    can't be read back.
    """
