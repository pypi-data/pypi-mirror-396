"""Seed bot responses from domain files to Strapi CMS."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Text

import aiohttp
import structlog
import yaml  # type: ignore[import-untyped]

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
    """Add seed subcommand parser.

    Args:
        subparsers: Subparser we are going to attach to.
        parents: Parent parsers, needed to ensure tree structure in argparse.
    """
    seed_parser = subparsers.add_parser(
        "seed",
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="Seed CMS with full bot responses from domain files.",
    )

    add_arguments(seed_parser)
    seed_parser.set_defaults(func=run)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments for seed command.

    Args:
        parser: Argument parser to add arguments to.
    """
    add_domain_param(parser, default="domain/original_domain_with_responses")
    add_common_strapi_arguments(parser)

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force seed even if responses already exist in Strapi. "
        "This will update existing entries.",
    )


async def seed_responses(
    responses: Dict[str, Any],
    client: StrapiClient,
    skip_existing: bool,
) -> Dict[str, int]:
    """Seed all responses to Strapi.

    Args:
        responses: Dictionary of response keys to variations.
        client: Strapi client instance.
        skip_existing: Whether to skip existing responses.

    Returns:
        Dictionary with counts of created, skipped, and failed responses.
    """
    counts = {"created": 0, "skipped": 0, "failed": 0}

    async with aiohttp.ClientSession() as session:
        for response_key, variations in responses.items():
            # Check if response exists
            if skip_existing:
                exists = await client.check_response_exists(session, response_key)

                if exists:
                    structlogger.info(
                        "cli.seed.skipping_existing",
                        response_key=response_key,
                    )
                    counts["skipped"] += 1
                    continue

            structlogger.info("cli.seed.creating", response_key=response_key)
            strapi_data = ResponseTransformer.rasa_to_strapi(response_key, variations)
            success = await client.create_response(session, strapi_data, publish=True)

            if success:
                structlogger.info(
                    "cli.seed.created_successfully",
                    response_key=response_key,
                )
                counts["created"] += 1
            else:
                structlogger.error(
                    "cli.seed.create_failed",
                    response_key=response_key,
                )
                counts["failed"] += 1

    return counts


def clear_domain_responses(domain_path: Text) -> None:
    """Clear response text from domain files, leaving empty lists.

    Args:
        domain_path: Path to domain directory or file.
    """
    domain_dir = Path(domain_path)

    # Handle both directory and single file
    yaml_files = (
        [domain_dir]
        if domain_dir.is_file()
        else list(domain_dir.rglob("*.yml")) + list(domain_dir.rglob("*.yaml"))
    )

    for yaml_file in yaml_files:
        # Skip shared.yml
        if yaml_file.name == "shared.yml":
            continue

        try:
            # Read the file as text
            with open(yaml_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Parse to check if responses exist
            with open(yaml_file, "r", encoding="utf-8") as f:
                domain_data = yaml.safe_load(f)

            # If file has responses, replace them
            if domain_data and "responses" in domain_data:
                # Find where responses section starts
                in_responses = False
                responses_indent = 0
                new_lines = []

                for line in lines:
                    # Check if we're entering the responses section
                    if line.strip().startswith("responses:"):
                        in_responses = True
                        responses_indent = len(line) - len(line.lstrip())
                        new_lines.append(line)
                        # Add cleared responses
                        for response_key in domain_data["responses"]:
                            new_lines.append(f"  {response_key}: []\n")
                        continue

                    # Skip lines that are part of responses section
                    if in_responses:
                        current_indent = len(line) - len(line.lstrip())
                        # If we hit a line at same or lower indent level
                        # we're out of responses
                        if line.strip() and current_indent <= responses_indent:
                            in_responses = False
                            new_lines.append(line)
                        # Skip response content lines
                        continue

                    # Keep all other lines as-is
                    new_lines.append(line)

                # Write back to file
                with open(yaml_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)

                structlogger.info(
                    "cli.seed.cleared_responses",
                    file=str(yaml_file),
                )
        except Exception as e:
            structlogger.warning(
                "cli.seed.failed_to_clear",
                file=str(yaml_file),
                exception=str(e),
            )


def run(args: argparse.Namespace) -> None:
    """Execute the seed command.

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

    # Handle --force flag (opposite of --skip-existing)
    skip_existing = not args.force

    structlogger.info(
        "cli.seed.loading_domain",
        domain_path=domain,
    )

    try:
        responses = DomainLoader.load_responses(domain)
    except FileNotFoundError as e:
        structlogger.error(
            "cli.seed.domain_not_found",
            error=str(e),
        )
        sys.exit(1)

    if not responses:
        structlogger.warning(
            "cli.seed.no_responses",
            event_info="No responses found in domain files. Nothing to seed.",
        )
        sys.exit(0)

    structlogger.info(
        "cli.seed.found_responses",
        count=len(responses),
    )
    structlogger.info(
        "cli.seed.connecting",
        strapi_url=config.url,
    )

    # Run the async seeding function
    client = StrapiClient(config)
    counts = asyncio.run(seed_responses(responses, client, skip_existing))

    # Print summary
    structlogger.info(
        "cli.seed.complete",
        created=counts["created"],
        skipped=counts["skipped"],
        failed=counts["failed"],
    )

    if counts["failed"] > 0:
        sys.exit(1)

    # Clear responses from the domain directory after successful seeding
    if counts["created"] > 0:
        structlogger.info("cli.seed.clearing_domain_responses")
        clear_domain_responses(domain)
