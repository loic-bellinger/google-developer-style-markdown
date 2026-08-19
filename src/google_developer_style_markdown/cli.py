"""Command line entry point."""

import argparse
import asyncio
import logging
from collections.abc import Sequence
from pathlib import Path

from . import SyncError, __version__
from .sync import DEFAULT_CONCURRENCY, DEFAULT_TIMEOUT, sync

__all__ = ['main']

_LOGGER = logging.getLogger(__name__)


def _positive(text: str) -> int:
    """Parse a strictly positive integer argument."""
    if (value := int(text)) < 1:
        raise argparse.ArgumentTypeError(f'must be at least 1, got {value}')
    return value


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog='gdsm',
        description=(
            "Mirror Google's developer documentation style guide as Markdown, "
            'and regenerate llms.txt and llms-full.txt from it.'
        ),
    )
    parser.add_argument(
        '-o',
        '--output-dir',
        type=Path,
        default=Path(),
        metavar='DIR',
        help='directory to write docs/, llms.txt and llms-full.txt into (default: .)',
    )
    parser.add_argument(
        '-c',
        '--concurrency',
        type=_positive,
        default=DEFAULT_CONCURRENCY,
        metavar='N',
        help=f'simultaneous connections (default: {DEFAULT_CONCURRENCY})',
    )
    parser.add_argument(
        '-t',
        '--timeout',
        type=float,
        default=DEFAULT_TIMEOUT,
        metavar='SECONDS',
        help=f'time allowed for each request (default: {DEFAULT_TIMEOUT:g})',
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='log every request')
    parser.add_argument('--version', action='version', version=__version__)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run a sync and report what changed.

    Args:
        argv: Command line arguments, or ``None`` to read ``sys.argv``.

    Returns:
        ``0`` on success, ``1`` if the guide could not be mirrored.
    """
    arguments = _parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if arguments.verbose else logging.INFO,
        format='%(message)s',
    )
    try:
        report = asyncio.run(
            sync(
                arguments.output_dir,
                concurrency=arguments.concurrency,
                timeout=arguments.timeout,
            )
        )
    except SyncError as error:
        _LOGGER.error('%s', error)
        return 1
    _LOGGER.info(
        'mirrored %d documents into %s, removed %d',
        len(report.documents),
        arguments.output_dir / 'docs',
        len(report.removed),
    )
    return 0
