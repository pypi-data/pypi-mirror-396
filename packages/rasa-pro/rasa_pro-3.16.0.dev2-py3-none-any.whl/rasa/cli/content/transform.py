"""Transformers for converting between Rasa and Strapi response formats."""

from typing import Any, Dict, List

import structlog

structlogger = structlog.getLogger(__name__)


class ResponseTransformer:
    """Transform responses between Rasa and Strapi formats."""

    @staticmethod
    def rasa_to_strapi(
        response_key: str, variations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Transform Rasa response format to Strapi format.

        Args:
            response_key: The response key (e.g., 'utter_greet').
            variations: List of response variations from Rasa domain.

        Returns:
            Strapi-formatted response data.
        """
        strapi_variations: List[Dict[str, Any]] = []

        for variation in variations:
            strapi_variation: Dict[str, Any] = {}

            # Text (optional - can have buttons/image/custom without text)
            if "text" in variation:
                text_value = variation.get("text")
                if text_value is not None:
                    strapi_variation["text"] = str(text_value)

            # Buttons - preserve original type
            if variation.get("buttons"):
                strapi_buttons = []
                for btn in variation["buttons"]:
                    if not isinstance(btn, dict):
                        continue

                    payload = btn.get("payload")
                    title = btn.get("title")

                    # Convert payload to string
                    payload_str = str(payload) if payload is not None else ""

                    # Only add button if it has required fields
                    if payload_str and title is not None:
                        strapi_buttons.append(
                            {
                                "payload": payload_str,
                                "title": title,
                            }
                        )

                if strapi_buttons:
                    strapi_variation["buttons"] = strapi_buttons

            # Image (URL string)
            if "image" in variation:
                image_value = variation.get("image")
                if image_value is not None:
                    strapi_variation["image"] = str(image_value)

            # Custom (JSON object - preserve as-is)
            if "custom" in variation:
                custom_value = variation.get("custom")
                if custom_value is not None:
                    strapi_variation["custom"] = custom_value

            # Channel (string)
            if "channel" in variation:
                channel_value = variation.get("channel")
                if channel_value is not None:
                    strapi_variation["channel"] = str(channel_value)

            # Condition (JSON object/array - preserve as-is)
            if "condition" in variation:
                condition_value = variation.get("condition")
                if condition_value is not None:
                    strapi_variation["condition"] = condition_value

            # ID (string)
            if "id" in variation:
                id_value = variation.get("id")
                if id_value is not None:
                    strapi_variation["id"] = str(id_value)

            # Allow interruptions (boolean - preserve as boolean)
            if "allow_interruptions" in variation:
                allow_interruptions_value = variation.get("allow_interruptions")
                if allow_interruptions_value is not None:
                    strapi_variation["allowInterruptions"] = bool(
                        allow_interruptions_value
                    )

            # Only add variation if it has at least one field
            if strapi_variation:
                strapi_variations.append(strapi_variation)

        return {
            "responseKey": response_key,
            "variations": strapi_variations,
            "publishedAt": None,
        }

    @staticmethod
    def _extract_component_data(component: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from a Strapi component.

        Args:
            component: Strapi component data.

        Returns:
            Extracted component data.
        """
        if not isinstance(component, dict):
            return {}

        # Check if it has attributes (nested structure)
        if "attributes" in component:
            attrs = component["attributes"]
            if "id" in attrs:
                attrs = {k: v for k, v in attrs.items() if k != "id"}
            return attrs

        # Check if it has data fields directly
        data_fields = [
            "text",
            "buttons",
            "image",
            "custom",
            "channel",
            "condition",
            "id",
            "allowInterruptions",
            "payload",
            "title",
        ]
        has_data = any(key in component for key in data_fields)

        if has_data:
            if len(component) == 1 and "id" in component:
                return {}
            return component

        return {}

    @classmethod
    def strapi_to_rasa(
        cls, responses: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Transform Strapi format to Rasa responses format.

        Args:
            responses: List of Strapi response entries.

        Returns:
            Dictionary of Rasa-formatted responses.
        """
        rasa_responses = {}

        for entry in responses:
            # Handle both direct attributes and nested structure
            attributes = entry.get("attributes", entry)
            response_key = attributes.get("responseKey")

            if not response_key:
                structlogger.warning(
                    "cli.transformer.missing_response_key",
                    entry_id=entry.get("id", "unknown"),
                )
                continue

            # Get variations
            variations = attributes.get("variations", [])
            if not variations and "variations" in entry:
                variations = entry["variations"]

            if not variations:
                structlogger.warning(
                    "cli.transformer.no_variations",
                    response_key=response_key,
                )
                continue

            rasa_variations = []

            for variation_raw in variations:
                variation = cls._extract_component_data(variation_raw)
                rasa_variation = {}

                # Add text if present
                text = variation.get("text")
                if text:
                    rasa_variation["text"] = text

                # Add buttons if present
                buttons_raw = variation.get("buttons", [])
                if not buttons_raw and isinstance(variation_raw, dict):
                    buttons_raw = variation_raw.get("buttons", [])

                if buttons_raw:
                    rasa_buttons = []
                    for button_raw in buttons_raw:
                        button = None

                        if isinstance(button_raw, dict):
                            button = cls._extract_component_data(button_raw)

                            if not button or (
                                "payload" not in button and "title" not in button
                            ):
                                if "payload" in button_raw or "title" in button_raw:
                                    button = button_raw
                                elif "data" in button_raw:
                                    button = button_raw["data"]
                                elif "attributes" in button_raw:
                                    button = button_raw["attributes"]

                        if button and isinstance(button, dict):
                            rasa_button = {}
                            payload = button.get("payload")
                            title = button.get("title")

                            if payload:
                                rasa_button["payload"] = str(payload)
                            if title is not None:
                                rasa_button["title"] = title

                            if rasa_button.get("payload") and "title" in rasa_button:
                                rasa_buttons.append(rasa_button)

                    if rasa_buttons:
                        rasa_variation["buttons"] = rasa_buttons

                # Add image if present
                image = variation.get("image")
                if image:
                    rasa_variation["image"] = image

                # Add custom if present
                custom = variation.get("custom")
                if custom is not None:
                    rasa_variation["custom"] = custom

                # Add channel if present
                channel = variation.get("channel")
                if channel:
                    rasa_variation["channel"] = channel

                # Add condition if present
                condition = variation.get("condition")
                if condition is not None:
                    rasa_variation["condition"] = condition

                # Add allow_interruptions only if explicitly set to false
                allow_interruptions = variation.get("allowInterruptions")
                if allow_interruptions is False:
                    rasa_variation["allow_interruptions"] = False

                # Only add variation if it has content
                if rasa_variation:
                    rasa_variations.append(rasa_variation)

            if rasa_variations:
                rasa_responses[response_key] = rasa_variations

        return rasa_responses
