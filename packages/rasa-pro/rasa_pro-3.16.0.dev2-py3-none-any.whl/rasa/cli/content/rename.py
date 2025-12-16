"""Rename bot response keys in Strapi CMS."""

import argparse
import asyncio
import sys

import aiohttp
import structlog

import rasa.shared.utils.cli
from rasa.cli import SubParsersAction

from .utils import StrapiClient, StrapiConfig, add_common_strapi_arguments

structlogger = structlog.getLogger(__name__)


def add_subparser(
    subparsers: SubParsersAction, parents: list[argparse.ArgumentParser]
) -> None:
    """Add rename subcommand parser.

    Args:
        subparsers: Subparser we are going to attach to.
        parents: Parent parsers, needed to ensure tree structure in argparse.
    """
    rename_parser = subparsers.add_parser(
        "rename",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Rename a bot response key in CMS.",
    )

    add_arguments(rename_parser)
    rename_parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for rename command.

    Args:
        parser: Argument parser to add arguments to.
    """
    parser.add_argument(
        "old_key",
        type=str,
        help="Current response key in CMS to rename (e.g., 'utter_greet').",
    )

    parser.add_argument(
        "new_key",
        type=str,
        help="New response key name (e.g., 'utter_welcome').",
    )

    add_common_strapi_arguments(parser)


async def rename_response_key(
    client: StrapiClient,
    old_key: str,
    new_key: str,
) -> bool:
    """Rename a response key in Strapi CMS.

    Args:
        client: Strapi client instance.
        old_key: Current response key to rename.
        new_key: New response key name.

    Returns:
        True if rename was successful, False otherwise.
    """
    async with aiohttp.ClientSession() as session:
        # Check if old key exists
        structlogger.info("cli.rename.finding_old_key", response_key=old_key)
        old_entry = await client.find_response_by_key(session, old_key)

        if not old_entry:
            structlogger.error(
                "cli.rename.old_key_not_found",
                response_key=old_key,
                event_info=f"Response '{old_key}' not found in CMS.",
            )
            return False

        # Check if new key already exists
        structlogger.info("cli.rename.checking_new_key", response_key=new_key)
        new_exists = await client.check_response_exists(session, new_key)

        if new_exists:
            structlogger.error(
                "cli.rename.new_key_exists",
                response_key=new_key,
                event_info=(
                    f"Response '{new_key}' already exists in CMS. Cannot rename."
                ),
            )
            return False

        # Update the response key
        structlogger.info(
            "cli.rename.updating_cms",
            old_key=old_key,
            new_key=new_key,
        )

        success = await client.update_response(
            session, old_entry, {"responseKey": new_key}
        )

        return success


def run(args: argparse.Namespace) -> None:
    """Execute the rename command.

    Args:
        args: Command-line arguments.
    """
    # Validate configuration
    config = StrapiConfig.from_args(args)
    config.validate()

    old_key = args.old_key
    new_key = args.new_key

    # Validate keys are different
    if old_key == new_key:
        structlogger.error(
            "cli.rename.same_keys",
            event_info="Old key and new key are the same. Nothing to rename.",
        )
        sys.exit(1)

    structlogger.info(
        "cli.rename.starting",
        old_key=old_key,
        new_key=new_key,
    )

    # Run the async rename operation
    client = StrapiClient(config)
    success = asyncio.run(rename_response_key(client, old_key, new_key))

    if not success:
        structlogger.error("cli.rename.cms_failed")
        sys.exit(1)

    rasa.shared.utils.cli.print_success(f"✓ Renamed '{old_key}' to '{new_key}' in CMS")
    structlogger.info("cli.rename.complete")
