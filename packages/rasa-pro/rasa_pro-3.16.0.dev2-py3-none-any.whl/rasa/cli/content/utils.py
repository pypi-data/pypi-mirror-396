"""Shared utilities for Strapi CMS operations."""

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Text

import aiohttp
import structlog
import yaml  # type: ignore[import-untyped]

structlogger = structlog.getLogger(__name__)


class StrapiConfig:
    """Configuration for Strapi connection."""

    def __init__(self, url: str, token: str):
        """Initialize Strapi configuration.

        Args:
            url: Strapi server URL.
            token: API token for authentication.
        """
        self.url = url.rstrip("/")
        self.token = token

    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for Strapi requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "StrapiConfig":
        """Create config from command-line arguments.

        Args:
            args: Parsed command-line arguments.

        Returns:
            StrapiConfig instance.
        """
        return cls(args.strapi_url, args.strapi_token)

    def validate(self) -> bool:
        """Validate that required configuration is present.

        Returns:
            True if valid, False otherwise (also logs error and exits).
        """
        if not self.token:
            structlogger.error(
                "cli.strapi.missing_token",
                event_info=(
                    "STRAPI_API_TOKEN is required.\n\n"
                    "To get your API token:\n"
                    "1. Log into Strapi admin panel (http://localhost:1337/admin)\n"
                    "2. Go to Settings > API Tokens\n"
                    "3. Create a new API Token with 'Full access' permissions\n\n"
                    "Set the token in one of these ways:\n"
                    "  - Environment variable: export STRAPI_API_TOKEN='your-token'\n"
                    "  - Command flag: --strapi-token 'your-token'"
                ),
            )
            sys.exit(1)
        return True


class DomainLoader:
    """Load and process Rasa domain files."""

    @staticmethod
    def load_responses(domain_path: Text, skip_shared: bool = True) -> Dict[str, Any]:
        """Load all domain YAML files and merge their responses.

        Args:
            domain_path: Path to domain directory or file.
            skip_shared: Whether to skip shared.yml files.

        Returns:
            Dictionary of response keys to variations.

        Raises:
            FileNotFoundError: If domain path doesn't exist.
        """
        all_responses = {}
        domain_dir = Path(domain_path)

        if not domain_dir.exists():
            raise FileNotFoundError(f"Domain directory not found: {domain_path}")

        # Handle both directory and single file
        yaml_files = (
            [domain_dir]
            if domain_dir.is_file()
            else list(domain_dir.rglob("*.yml")) + list(domain_dir.rglob("*.yaml"))
        )

        for yaml_file in yaml_files:
            # Skip shared.yml as it typically doesn't have responses
            if skip_shared and yaml_file.name == "shared.yml":
                continue

            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    domain_data = yaml.safe_load(f)
                    if domain_data and "responses" in domain_data:
                        all_responses.update(domain_data["responses"])
            except Exception as e:
                structlogger.warning(
                    "cli.domain.failed_to_load",
                    file=str(yaml_file),
                    exception=str(e),
                )

        return all_responses


class StrapiClient:
    """Client for interacting with Strapi CMS."""

    def __init__(self, config: StrapiConfig):
        """Initialize Strapi client.

        Args:
            config: Strapi configuration.
        """
        self.config = config
        self.base_url = f"{config.url}/api/bot-responses"

    async def check_response_exists(
        self, session: aiohttp.ClientSession, response_key: str
    ) -> bool:
        """Check if a response key exists in Strapi.

        Args:
            session: aiohttp client session.
            response_key: The response key to check.

        Returns:
            True if the response exists, False otherwise.
        """
        params = {"filters[responseKey][$eq]": response_key}

        try:
            async with session.get(
                self.base_url, params=params, headers=self.config.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return len(data.get("data", [])) > 0
        except Exception as e:
            structlogger.warning(
                "cli.strapi.check_response_failed",
                response_key=response_key,
                exception=str(e),
            )

        return False

    async def get_existing_response_keys(
        self, session: aiohttp.ClientSession
    ) -> Set[str]:
        """Get all existing response keys from Strapi (including drafts).

        Args:
            session: aiohttp client session.

        Returns:
            Set of existing response keys.
        """
        all_keys = set()
        page = 1
        page_size = 100

        while True:
            params = {
                "pagination[page]": page,
                "pagination[pageSize]": page_size,
                "fields[0]": "responseKey",
                "publicationState": "preview",  # Fetch both published and draft
            }

            try:
                async with session.get(
                    self.base_url, params=params, headers=self.config.headers
                ) as response:
                    if response.status != 200:
                        break

                    data = await response.json()
                    entries = data.get("data", [])

                    if not entries:
                        break

                    for entry in entries:
                        # Handle both nested attributes and direct structure
                        attributes = entry.get("attributes", entry)
                        if "responseKey" in attributes:
                            all_keys.add(attributes["responseKey"])

                    pagination = data.get("meta", {}).get("pagination", {})
                    if page >= pagination.get("pageCount", 1):
                        break

                    page += 1
            except Exception as e:
                structlogger.warning(
                    "cli.strapi.fetch_failed",
                    page=page,
                    exception=str(e),
                )
                break

        return all_keys

    async def find_response_by_key(
        self, session: aiohttp.ClientSession, response_key: str
    ) -> Optional[Dict[str, Any]]:
        """Find a response entry in Strapi by response key.

        Args:
            session: aiohttp client session.
            response_key: The response key to find.

        Returns:
            The response entry if found, None otherwise.
        """
        params = {
            "filters[responseKey][$eq]": response_key,
            "publicationState": "preview",  # Include drafts
        }

        try:
            async with session.get(
                self.base_url, params=params, headers=self.config.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get("data", [])
                    if entries:
                        return entries[0]
        except Exception as e:
            structlogger.error(
                "cli.strapi.find_failed",
                response_key=response_key,
                exception=str(e),
            )

        return None

    async def create_response(
        self,
        session: aiohttp.ClientSession,
        response_data: Dict[str, Any],
        publish: bool = True,
    ) -> bool:
        """Create a new Bot Response in Strapi.

        Args:
            session: aiohttp client session.
            response_data: The response data to create.
            publish: Whether to publish the entry after creation.

        Returns:
            True if creation was successful, False otherwise.
        """
        payload = {"data": response_data}
        draft_url = f"{self.base_url}?status=draft"

        try:
            async with session.post(
                draft_url, json=payload, headers=self.config.headers
            ) as response:
                response_text = await response.text()

                if response.status in (200, 201):
                    if publish:
                        result = await response.json()
                        entry_id = result["data"]["id"]
                        publish_url = f"{self.base_url}/{entry_id}/actions/publish"
                        async with session.post(
                            publish_url, headers=self.config.headers
                        ):
                            pass
                    return True
                elif response.status == 405:
                    structlogger.error(
                        "cli.strapi.method_not_allowed",
                        event_info=(
                            "405 Method Not Allowed error. This usually means:\n"
                            "1.The Strapi server needs to be restarted\n"
                            "2.API permissions need to be configured in Strapi admin:\n"
                            "   - Go to Settings > Roles & Permissions > Public\n"
                            "   - Enable 'create' permission for 'Bot Response'"
                        ),
                    )
                    return False
                else:
                    structlogger.error(
                        "cli.strapi.create_failed",
                        status_code=response.status,
                        response_text=response_text,
                    )
                    return False
        except Exception as e:
            structlogger.error(
                "cli.strapi.create_exception",
                response_key=response_data.get("responseKey", "unknown"),
                exception=str(e),
            )
            return False

    async def update_response(
        self,
        session: aiohttp.ClientSession,
        entry: Dict[str, Any],
        response_data: Dict[str, Any],
    ) -> bool:
        """Update an existing Bot Response in Strapi.

        Args:
            session: aiohttp client session.
            entry: The full entry object from search.
            response_data: The response data to update.

        Returns:
            True if update was successful, False otherwise.
        """
        # Try both documentId and id
        identifier = entry.get("documentId") or entry.get("id")
        url = f"{self.base_url}/{identifier}"
        payload = {"data": response_data}

        try:
            async with session.put(
                url, json=payload, headers=self.config.headers
            ) as response:
                if response.status == 200:
                    return True
                else:
                    response_text = await response.text()
                    structlogger.error(
                        "cli.strapi.update_failed",
                        identifier=identifier,
                        status_code=response.status,
                        response_text=response_text,
                    )
                    return False
        except Exception as e:
            structlogger.error(
                "cli.strapi.update_exception",
                identifier=identifier,
                exception=str(e),
            )
            return False

    async def fetch_all_responses(
        self, session: aiohttp.ClientSession, publication_state: str = "live"
    ) -> List[Dict[str, Any]]:
        """Fetch all Bot Responses from Strapi with full population.

        Args:
            session: aiohttp client session.
            publication_state: Publication state filter ('live', 'preview').

        Returns:
            List of bot response entries from Strapi.
        """
        all_responses = []
        page = 1
        page_size = 100

        while True:
            params = {
                "pagination[page]": page,
                "pagination[pageSize]": page_size,
                "populate[variations][populate]": "*",
                "publicationState": publication_state,
            }

            try:
                async with session.get(
                    self.base_url, params=params, headers=self.config.headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        structlogger.error(
                            "cli.strapi.fetch_failed",
                            status_code=response.status,
                            error=error_text,
                        )
                        break

                    data = await response.json()
                    entries = data.get("data", [])

                    if not entries:
                        break

                    all_responses.extend(entries)

                    pagination = data.get("meta", {}).get("pagination", {})
                    if page >= pagination.get("pageCount", 1):
                        break

                    page += 1
            except Exception as e:
                structlogger.error(
                    "cli.strapi.fetch_exception",
                    page=page,
                    exception=str(e),
                )
                break

        return all_responses


def add_common_strapi_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common Strapi-related arguments to a parser.

    Args:
        parser: Argument parser to add arguments to.
    """
    parser.add_argument(
        "--strapi-url",
        type=str,
        default=os.getenv("STRAPI_URL", "http://localhost:1337"),
        help="Strapi server URL. Can also be set via STRAPI_URL environment variable.",
    )

    parser.add_argument(
        "--strapi-token",
        type=str,
        default=os.getenv("STRAPI_API_TOKEN", ""),
        help="Strapi API token for authentication. Can also be set via "
        "STRAPI_API_TOKEN environment variable.",
    )
