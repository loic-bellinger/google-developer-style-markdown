"""Deterministic Markdown mirror of Google's developer documentation style guide.

The guide is published at https://developers.google.com/style/. Every page is
also served as plain Markdown at the same URL with a `.md.txt` suffix, so this
package never has to reconstruct Markdown from HTML: it parses the entry page
only to discover the table of contents, then downloads the Markdown Google
already publishes.
"""

from importlib.metadata import version

__all__ = ['SyncError', '__version__']

__version__ = version(__name__)
"""Read from the installed package, so pyproject.toml stays the only copy."""


class SyncError(RuntimeError):
    """The guide could not be mirrored.

    Raised for every failure the user can act on: an unreachable page, an entry
    page whose structure is no longer recognised, or a mirrored document that
    cannot be read back.
    """
