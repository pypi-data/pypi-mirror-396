"""Fetch bot responses from Strapi CMS to domain files."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

import aiohttp
import structlog
from ruamel.yaml import YAML

from rasa.cli import SubParsersAction
from rasa.cli.arguments.default_arguments import add_domain_param
from rasa.cli.validation.config_path_validation import get_validated_path
from rasa.shared.constants import DEFAULT_DOMAIN_PATHS

from .transform import ResponseTransformer
from .utils import (
    StrapiClient,
    StrapiConfig,
    add_common_strapi_arguments,
)

structlogger = structlog.getLogger(__name__)


def add_subparser(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add fetch subcommand parser.

    Args:
        subparsers: Subparser we are going to attach to.
        parents: Parent parsers, needed to ensure tree structure in argparse.
    """
    fetch_parser = subparsers.add_parser(
        "fetch",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Fetch bot responses from CMS to domain files.",
    )

    add_arguments(fetch_parser)
    fetch_parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for fetch command.

    Args:
        parser: Argument parser to add arguments to.
    """
    add_domain_param(parser)
    add_common_strapi_arguments(parser)

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="responses.yml",
        help="Output filename for responses (relative to domain directory).",
    )


def write_responses_yml(
    responses: Dict[str, List[Dict[str, Any]]], output_path: Path
) -> None:
    """Write responses to a YAML file in Rasa format.

    Args:
        responses: Dictionary of responses to write.
        output_path: Path to output YAML file.
    """
    yaml_handler = YAML()
    yaml_handler.preserve_quotes = True  # type: ignore[assignment]
    yaml_handler.width = 4096  # type: ignore[assignment]
    yaml_handler.indent(mapping=2, sequence=4, offset=2)

    output_data = {
        "version": "3.1",
        "responses": responses,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        yaml_handler.dump(output_data, f)

    structlogger.info(
        "cli.fetch.wrote_responses",
        count=len(responses),
        path=str(output_path),
    )


async def fetch_responses(client: StrapiClient, output_path: Path) -> int:
    """Fetch all responses from Strapi and write to file.

    Args:
        client: Strapi client instance.
        output_path: Path to output YAML file.

    Returns:
        Number of responses fetched.
    """
    async with aiohttp.ClientSession() as session:
        structlogger.info(
            "cli.fetch.fetching",
            strapi_url=client.config.url,
        )

        strapi_responses = await client.fetch_all_responses(
            session, publication_state="live"
        )

        if not strapi_responses:
            structlogger.warning("cli.fetch.no_responses")
            return 0

        structlogger.info(
            "cli.fetch.found_responses",
            count=len(strapi_responses),
        )

        structlogger.info("cli.fetch.transforming")
        rasa_responses = ResponseTransformer.strapi_to_rasa(strapi_responses)

        structlogger.info(
            "cli.fetch.writing",
            count=len(rasa_responses),
            path=str(output_path),
        )

        write_responses_yml(rasa_responses, output_path)

        return len(rasa_responses)


def run(args: argparse.Namespace) -> None:
    """Execute the fetch command.

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

    # Determine output file path
    domain_path = Path(domain)
    output_path = domain_path if domain_path.is_file() else domain_path / args.output

    structlogger.info(
        "cli.fetch.starting",
        domain=domain,
        output=str(output_path),
    )

    # Run the async fetching function
    client = StrapiClient(config)
    count: int = asyncio.run(fetch_responses(client, output_path))

    if count == 0:
        structlogger.warning("cli.fetch.no_responses_fetched")
        sys.exit(1)

    structlogger.info(
        "cli.fetch.complete",
        count=count,
    )
