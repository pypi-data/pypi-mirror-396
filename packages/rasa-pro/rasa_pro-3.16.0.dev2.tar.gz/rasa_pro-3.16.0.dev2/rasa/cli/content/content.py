"""Content command registration and subparser setup."""

import argparse
from typing import List

import rasa.cli.content.fetch
import rasa.cli.content.push
import rasa.cli.content.rename
import rasa.cli.content.seed
from rasa.cli import SubParsersAction


def add_subparser(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add content command parser with subcommands.

    Args:
        subparsers: Subparser we are going to attach to.
        parents: Parent parsers, needed to ensure tree structure in argparse.
    """
    content_parser = subparsers.add_parser(
        "content",
        help="Manage bot responses with Strapi CMS.",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Create subparsers for content subcommands
    content_subparsers = content_parser.add_subparsers()

    # Add subcommands
    rasa.cli.content.seed.add_subparser(content_subparsers, parents)
    rasa.cli.content.push.add_subparser(content_subparsers, parents)
    rasa.cli.content.fetch.add_subparser(content_subparsers, parents)
    rasa.cli.content.rename.add_subparser(content_subparsers, parents)
