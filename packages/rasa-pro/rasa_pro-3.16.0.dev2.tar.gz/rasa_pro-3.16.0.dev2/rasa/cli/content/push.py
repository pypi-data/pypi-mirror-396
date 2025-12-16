"""Push missing bot response keys to Strapi CMS as drafts."""

import argparse
import asyncio
import sys
from typing import Any, Dict, List

import aiohttp
import structlog

from rasa.cli import SubParsersAction
from rasa.cli.arguments.default_arguments import add_domain_param
from rasa.cli.validation.config_path_validation import get_validated_path
from rasa.shared.constants import DEFAULT_DOMAIN_PATHS

from .transform import ResponseTransformer
from .utils import (
    DomainLoader,
    StrapiClient,
    StrapiConfig,
    add_common_strapi_arguments,
)

structlogger = structlog.getLogger(__name__)


def add_subparser(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add push subcommand parser.

    Args:
        subparsers: Subparser we are going to attach to.
        parents: Parent parsers, needed to ensure tree structure in argparse.
    """
    push_parser = subparsers.add_parser(
        "push",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Push missing response keys to CMS as drafts.",
    )

    add_arguments(push_parser)
    push_parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for push command.

    Args:
        parser: Argument parser to add arguments to.
    """
    add_domain_param(parser, default="domain/original_domain_with_responses")
    add_common_strapi_arguments(parser)

    parser.add_argument(
        "--placeholder",
        type=str,
        default="To be updated by content team",
        help="Placeholder text for draft responses.",
    )


async def scaffold_missing_responses(
    domain_responses: Dict[str, Any],
    client: StrapiClient,
    placeholder_text: str,
) -> Dict[str, int]:
    """Create missing response keys in Strapi.

    Args:
        domain_responses: Dictionary of responses from domain files.
        client: Strapi client instance.
        placeholder_text: Placeholder text for draft responses.

    Returns:
        Dictionary with counts of created and failed responses.
    """
    counts = {"created": 0, "failed": 0}

    async with aiohttp.ClientSession() as session:
        structlogger.info("cli.push.fetching_existing")
        existing_keys = await client.get_existing_response_keys(session)

        structlogger.info(
            "cli.push.found_existing",
            count=len(existing_keys),
        )

        domain_keys = set(domain_responses.keys())
        missing_keys = domain_keys - existing_keys

        if not missing_keys:
            structlogger.info("cli.push.no_missing")
            return counts

        structlogger.info(
            "cli.push.found_missing",
            count=len(missing_keys),
        )

        for response_key in sorted(missing_keys):
            structlogger.info("cli.push.creating_draft", response_key=response_key)
            variations = domain_responses.get(response_key)
            if variations:
                draft_data = ResponseTransformer.rasa_to_strapi(
                    response_key, variations
                )
            else:
                draft_data = {
                    "responseKey": response_key,
                    "variations": [{"text": placeholder_text}],
                    "publishedAt": None,
                }

            success = await client.create_response(session, draft_data, publish=False)

            if success:
                structlogger.info(
                    "cli.push.created",
                    response_key=response_key,
                )
                counts["created"] += 1
            else:
                structlogger.error(
                    "cli.push.failed",
                    response_key=response_key,
                )
                counts["failed"] += 1

    return counts


def run(args: argparse.Namespace) -> None:
    """Execute the scaffold command.

    Args:
        args: Command-line arguments.
    """
    # Validate configuration
    config = StrapiConfig.from_args(args)
    config.validate()

    # Get validated domain path
    domain = get_validated_path(
        args.domain, "domain", DEFAULT_DOMAIN_PATHS, none_is_valid=False
    )

    structlogger.info(
        "cli.push.loading_domain",
        domain_path=domain,
    )

    try:
        responses = DomainLoader.load_responses(domain)
    except FileNotFoundError as e:
        structlogger.error(
            "cli.push.domain_not_found",
            error=str(e),
        )
        sys.exit(1)

    if not responses:
        structlogger.warning(
            "cli.push.no_responses",
            event_info="No responses found in domain files. Nothing to scaffold.",
        )
        sys.exit(0)

    structlogger.info(
        "cli.push.found_responses",
        count=len(responses),
    )
    structlogger.info(
        "cli.push.connecting",
        strapi_url=config.url,
    )

    # Run the async scaffolding function
    client = StrapiClient(config)
    counts = asyncio.run(
        scaffold_missing_responses(responses, client, args.placeholder)
    )

    # Print summary
    structlogger.info(
        "cli.push.complete",
        created=counts["created"],
        failed=counts["failed"],
    )

    if counts["failed"] > 0:
        sys.exit(1)
