"""
Custom logging processors for domolibrary2.

This module contains result processors and extractors specifically designed
for domolibrary2 components to provide better logging integration.
"""

from typing import Any

from dc_logger.client.extractors import EntityExtractor, ResultProcessor
from dc_logger.client.models import (
    Entity as LogEntity,
    HTTPDetails,
)

from ...client import response as rgd


class NoOpEntityExtractor(EntityExtractor):
    """No-op entity extractor that returns None to avoid conflicts."""

    def extract(self, func: Any, args: tuple, kwargs: dict) -> LogEntity | None:
        """Return None to avoid entity conflicts."""
        return None


class DomoEntityExtractor(EntityExtractor):
    """Custom entity extractor for Domo routes that extracts entity info from function parameters."""

    def extract(self, func: Any, args: tuple, kwargs: dict) -> LogEntity | None:
        """Extract entity information from function parameters.

        This extractor looks at the function parameters to determine what type of entity
        is being accessed and extracts relevant information.
        """
        # Extract entity type from function name
        func_name = func.__name__.lower()

        # Determine entity type based on function name patterns
        if "dataset" in func_name or "datasource" in func_name:
            return self._extract_dataset_entity(kwargs)
        elif "card" in func_name:
            return self._extract_card_entity(kwargs)
        elif "user" in func_name:
            return self._extract_user_entity(kwargs)
        elif "page" in func_name or "stack" in func_name:
            return self._extract_page_entity(kwargs)
        elif "auth" in func_name:
            return self._extract_auth_entity(kwargs)

        return None

    def _extract_dataset_entity(self, kwargs: dict) -> LogEntity | None:
        """Extract rich dataset entity information."""
        dataset_id = kwargs.get("dataset_id")
        if not dataset_id:
            return None

        auth = kwargs.get("auth")
        additional_info = {
            "auth_instance": self._get_auth_instance(kwargs),
        }

        # Add display URL if auth is available
        if auth and hasattr(auth, "domo_instance"):
            additional_info["display_url"] = (
                f"https://{auth.domo_instance}.domo.com/datasources/{dataset_id}"
            )
            additional_info["auth_user"] = getattr(auth, "user", None)
            additional_info["auth_type"] = type(auth).__name__

        return LogEntity(
            type="dataset",
            id=str(dataset_id),
            name=f"Dataset {dataset_id}",
            additional_info=additional_info,
        )

    def _extract_card_entity(self, kwargs: dict) -> LogEntity | None:
        """Extract rich card entity information."""
        card_id = kwargs.get("card_id")
        if not card_id:
            return None

        auth = kwargs.get("auth")
        additional_info = {
            "entity_type": "card",
            "id": str(card_id),
            "auth_instance": self._get_auth_instance(kwargs),
        }

        # Add display URL if auth is available
        if auth and hasattr(auth, "domo_instance"):
            additional_info["display_url"] = (
                f"https://{auth.domo_instance}.domo.com/kpis/details/{card_id}"
            )
            additional_info["auth_user"] = getattr(auth, "user", None)
            additional_info["auth_type"] = type(auth).__name__

        return LogEntity(
            type="card",
            id=str(card_id),
            name=f"Card {card_id}",
            additional_info=additional_info,
        )

    def _extract_user_entity(self, kwargs: dict) -> LogEntity | None:
        """Extract user entity information."""
        user_id = kwargs.get("user_id")
        if not user_id:
            return None

        return LogEntity(
            type="user",
            id=str(user_id),
            name=f"User {user_id}",
            additional_info={"auth_instance": self._get_auth_instance(kwargs)},
        )

    def _extract_page_entity(self, kwargs: dict) -> LogEntity | None:
        """Extract page entity information."""
        page_id = kwargs.get("page_id")
        if not page_id:
            return None

        return LogEntity(
            type="page",
            id=str(page_id),
            name=f"Page {page_id}",
            additional_info={"auth_instance": self._get_auth_instance(kwargs)},
        )

    def _extract_auth_entity(self, kwargs: dict) -> LogEntity | None:
        """Extract auth entity information."""
        auth_instance = self._get_auth_instance(kwargs)
        if not auth_instance:
            return None

        return LogEntity(
            type="auth",
            id="auth_check",
            name="Authentication",
            additional_info={"auth_instance": auth_instance},
        )

    def _get_auth_instance(self, kwargs: dict) -> str | None:
        """Extract Domo instance from auth object."""
        auth = kwargs.get("auth")
        if auth and hasattr(auth, "domo_instance"):
            return auth.domo_instance
        return None


class DomoEntityResultProcessor(ResultProcessor):
    """Enhanced result processor that extracts rich entity information from DomoEntity objects."""

    def process(
        self, result: Any, http_details: HTTPDetails | None = None
    ) -> tuple[dict[str, Any], HTTPDetails | None]:
        """Process the result to extract rich entity information from DomoEntity objects."""
        result_context = {}

        # Try to extract entity information from the result
        entity_info = self._extract_rich_entity_info(result)
        if entity_info:
            # Put rich entity information in a custom field to complement basic entity
            result_context["domo_entity_info"] = entity_info

        # Update HTTP details if it's a ResponseGetData object
        if isinstance(result, rgd.ResponseGetData) and http_details:
            http_details.status_code = result.status

        return result_context, http_details

    def _extract_rich_entity_info(self, result: Any) -> dict | None:
        """Extract rich entity information from DomoEntity objects or ResponseGetData."""

        # Case 1: Direct DomoEntity object
        if self._is_domo_entity(result):
            return self._extract_from_domo_entity(result)

        # Case 2: ResponseGetData containing DomoEntity in response
        if isinstance(result, rgd.ResponseGetData) and result.is_success:
            response_data = result.response
            if isinstance(response_data, dict):
                # Try to extract entity info from the response data
                return self._extract_from_response_data(response_data, result)

        return None

    def _is_domo_entity(self, obj: Any) -> bool:
        """Check if an object is a DomoEntity."""
        if not hasattr(obj, "__class__"):
            return False

        class_name = obj.__class__.__name__
        return (
            class_name.startswith("Domo")
            and hasattr(obj, "id")
            and hasattr(obj, "auth")
        )

    def _extract_from_domo_entity(self, entity: Any) -> dict:
        """Extract rich information from a DomoEntity object."""
        entity_type = self._get_entity_type(entity)

        # Base entity information
        entity_info = {
            "type": entity_type,
            "id": str(entity.id),
            "name": self._get_entity_name(entity),
            "additional_info": {
                "auth_instance": getattr(entity.auth, "domo_instance", None),
                "class_name": entity.__class__.__name__,
            },
        }

        # Add entity-specific rich information
        if hasattr(entity, "title") and entity.title:
            entity_info["additional_info"]["title"] = entity.title

        if hasattr(entity, "description") and entity.description:
            entity_info["additional_info"]["description"] = entity.description

        if hasattr(entity, "display_url"):
            entity_info["additional_info"]["display_url"] = entity.display_url

        # Add type-specific information
        if entity_type == "card":
            self._add_card_specific_info(entity, entity_info)
        elif entity_type == "dataset":
            self._add_dataset_specific_info(entity, entity_info)
        elif entity_type == "page":
            self._add_page_specific_info(entity, entity_info)
        elif entity_type == "user":
            self._add_user_specific_info(entity, entity_info)

        return entity_info

    def _extract_from_response_data(
        self, response_data: dict, result: rgd.ResponseGetData
    ) -> dict | None:
        """Extract entity information from API response data."""
        # Try to determine entity type from URL or response structure
        url = (
            getattr(result.request_metadata, "url", "")
            if result.request_metadata
            else ""
        )

        if "/datasources/" in url or "/datasets/" in url:
            return self._extract_dataset_from_response(response_data, result)
        elif "/cards" in url:
            return self._extract_card_from_response(response_data, result)
        elif "/users/" in url:
            return self._extract_user_from_response(response_data, result)
        elif "/pages/" in url:
            return self._extract_page_from_response(response_data, result)

        return None

    def _get_entity_type(self, entity: Any) -> str:
        """Determine entity type from class name."""
        class_name = entity.__class__.__name__.lower()

        if "card" in class_name:
            return "card"
        elif "dataset" in class_name:
            return "dataset"
        elif "page" in class_name:
            return "page"
        elif "user" in class_name:
            return "user"
        elif "group" in class_name:
            return "group"
        elif "auth" in class_name:
            return "auth"
        else:
            return class_name.replace("domo", "")

    def _get_entity_name(self, entity: Any) -> str:
        """Get the best available name for the entity.

        Uses the entity_name property if available, otherwise falls back to
        checking common name attributes.
        """
        # Use entity_name property if available (preferred)
        if hasattr(entity, "entity_name"):
            return entity.entity_name

        # Fallback to old logic for backwards compatibility
        name_attrs = ["title", "name", "display_name", "label"]
        for attr in name_attrs:
            if hasattr(entity, attr):
                value = getattr(entity, attr)
                if value:
                    return str(value)

        # Fallback to ID-based name
        return f"{self._get_entity_type(entity).title()} {entity.id}"

    def _add_card_specific_info(self, card: Any, entity_info: dict):
        """Add card-specific information."""
        if hasattr(card, "chart_type") and card.chart_type:
            entity_info["additional_info"]["chart_type"] = card.chart_type
        if hasattr(card, "dataset_id") and card.dataset_id:
            entity_info["additional_info"]["dataset_id"] = card.dataset_id
        if hasattr(card, "type") and card.type:
            entity_info["additional_info"]["card_type"] = card.type

    def _add_dataset_specific_info(self, dataset: Any, entity_info: dict):
        """Add dataset-specific information."""
        if hasattr(dataset, "data_provider_type") and dataset.data_provider_type:
            entity_info["additional_info"][
                "data_provider_type"
            ] = dataset.data_provider_type
        if hasattr(dataset, "row_count") and dataset.row_count is not None:
            entity_info["additional_info"]["row_count"] = dataset.row_count
        if hasattr(dataset, "column_count") and dataset.column_count is not None:
            entity_info["additional_info"]["column_count"] = dataset.column_count

    def _add_page_specific_info(self, page: Any, entity_info: dict):
        """Add page-specific information."""
        if hasattr(page, "top_page_id") and page.top_page_id:
            entity_info["additional_info"]["top_page_id"] = page.top_page_id
        if hasattr(page, "parent_page_id") and page.parent_page_id:
            entity_info["additional_info"]["parent_page_id"] = page.parent_page_id
        if hasattr(page, "is_locked") and page.is_locked is not None:
            entity_info["additional_info"]["is_locked"] = page.is_locked

    def _add_user_specific_info(self, user: Any, entity_info: dict):
        """Add user-specific information."""
        if hasattr(user, "email") and user.email:
            entity_info["additional_info"]["email"] = user.email
        if hasattr(user, "display_name") and user.display_name:
            entity_info["additional_info"]["display_name"] = user.display_name

    def _extract_dataset_from_response(
        self, response_data: dict, result: rgd.ResponseGetData
    ) -> dict:
        """Extract dataset information from API response."""
        dataset_id = (
            self._extract_id_from_url(result.request_metadata.url)
            if result.request_metadata
            else "unknown"
        )

        return {
            "type": "dataset",
            "id": dataset_id,
            "name": response_data.get("name", f"Dataset {dataset_id}"),
            "additional_info": {
                "auth_instance": (
                    getattr(result.request_metadata, "auth_instance", None)
                    if result.request_metadata
                    else None
                ),
                "description": response_data.get("description"),
                "data_provider_type": response_data.get("dataProviderType"),
                "row_count": response_data.get("rowCount"),
                "column_count": response_data.get("columnCount"),
            },
        }

    def _extract_card_from_response(
        self, response_data: dict, result: rgd.ResponseGetData
    ) -> dict:
        """Extract card information from API response."""
        card_id = (
            self._extract_id_from_url(result.request_metadata.url)
            if result.request_metadata
            else "unknown"
        )

        return {
            "type": "card",
            "id": card_id,
            "name": response_data.get("title", f"Card {card_id}"),
            "additional_info": {
                "auth_instance": (
                    getattr(result.request_metadata, "auth_instance", None)
                    if result.request_metadata
                    else None
                ),
                "description": response_data.get("description"),
                "chart_type": response_data.get("chartType"),
                "dataset_id": response_data.get("datasetId"),
            },
        }

    def _extract_user_from_response(
        self, response_data: dict, result: rgd.ResponseGetData
    ) -> dict:
        """Extract user information from API response."""
        user_id = (
            self._extract_id_from_url(result.request_metadata.url)
            if result.request_metadata
            else "unknown"
        )

        return {
            "type": "user",
            "id": user_id,
            "name": response_data.get("displayName", f"User {user_id}"),
            "additional_info": {
                "auth_instance": (
                    getattr(result.request_metadata, "auth_instance", None)
                    if result.request_metadata
                    else None
                ),
                "email": response_data.get("email"),
                "role": response_data.get("role"),
            },
        }

    def _extract_page_from_response(
        self, response_data: dict, result: rgd.ResponseGetData
    ) -> dict:
        """Extract page information from API response."""
        page_id = (
            self._extract_id_from_url(result.request_metadata.url)
            if result.request_metadata
            else "unknown"
        )

        return {
            "type": "page",
            "id": page_id,
            "name": response_data.get("title", f"Page {page_id}"),
            "additional_info": {
                "auth_instance": (
                    getattr(result.request_metadata, "auth_instance", None)
                    if result.request_metadata
                    else None
                ),
                "description": response_data.get("description"),
                "top_page_id": response_data.get("topPageId"),
                "parent_page_id": response_data.get("parentPageId"),
            },
        }

    def _extract_id_from_url(self, url: str) -> str:
        """Extract entity ID from URL."""
        if not url:
            return "unknown"

        # Try to extract ID from URL patterns
        import re

        # Pattern for UUIDs
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        uuid_match = re.search(uuid_pattern, url, re.IGNORECASE)
        if uuid_match:
            return uuid_match.group()

        # Pattern for numeric IDs
        numeric_pattern = r"/(\d+)(?:/|$)"
        numeric_match = re.search(numeric_pattern, url)
        if numeric_match:
            return numeric_match.group(1)

        return "unknown"


class DomoEntityObjectProcessor(ResultProcessor):
    """Custom result processor for DomoEntity objects returned from class methods."""

    def _extract_entity_from_domo_object(self, result: Any) -> LogEntity | None:
        """Extract entity information from DomoEntity objects.

        Args:
            result: The function result (should be DomoEntity_w_Lineage)

        Returns:
            LogEntity with extracted entity information or None
        """
        # Check if it's a DomoEntity_w_Lineage by checking class name and attributes
        if not (
            hasattr(result, "__class__")
            and hasattr(result, "id")
            and hasattr(result, "auth")
            and result.__class__.__name__.startswith("Domo")
        ):
            return None

        # Extract entity information from DomoEntity object
        entity_info = {
            "type": result.__class__.__name__.lower().replace("domo", ""),
            "id": result.id,
            "name": getattr(result, "title", None) or getattr(result, "name", None),
        }

        additional_info = {}

        # Add entity-specific fields
        if hasattr(result, "title") and result.title:
            additional_info["title"] = result.title
        if hasattr(result, "description") and result.description:
            additional_info["description"] = result.description
        if hasattr(result, "type") and result.type:
            additional_info["entity_type"] = result.type
        if hasattr(result, "chart_type") and result.chart_type:
            additional_info["chart_type"] = result.chart_type
        if hasattr(result, "dataset_id") and result.dataset_id:
            additional_info["dataset_id"] = result.dataset_id
        if hasattr(result, "urn") and result.urn:
            additional_info["urn"] = result.urn

        # Add instance information
        if (
            hasattr(result, "auth")
            and result.auth
            and hasattr(result.auth, "domo_instance")
        ):
            additional_info["instance"] = result.auth.domo_instance

        # Add display URL if available
        if hasattr(result, "display_url"):
            additional_info["display_url"] = result.display_url

        # Add additional_info to entity_info
        if additional_info:
            entity_info["additional_info"] = additional_info

        return LogEntity.from_any(entity_info) if entity_info else None

    def process(
        self, result: Any, http_details: HTTPDetails | None = None
    ) -> tuple[dict[str, Any], HTTPDetails | None]:
        """Process DomoEntity result and extract entity information.

        Args:
            result: The function result (should be DomoEntity_w_Lineage)
            http_details: Optional HTTP details to update

        Returns:
            Tuple of (result_context dict with entity info, updated http_details)
        """
        result_context = {}

        # Extract entity information from DomoEntity object
        entity = self._extract_entity_from_domo_object(result)
        if entity:
            # Override the entity field with our extracted entity information
            # This will replace the decorator's entity field
            result_context["entity"] = {
                "type": entity.type,
                "id": entity.id,
                "name": entity.name,
                "additional_info": entity.additional_info,
            }

        return result_context, http_details


class DomoEntityProcessor(ResultProcessor):
    """Custom result processor for DomoEntity objects from route responses."""

    def _extract_entity_info(self, result: Any) -> LogEntity | None:
        """Extract entity information from route response.

        Args:
            result: The function result (should be ResponseGetData)

        Returns:
            LogEntity with extracted entity information or None
        """
        if not isinstance(result, rgd.ResponseGetData) or not result.is_success:
            return None

        response = result.response
        if not isinstance(response, dict):
            return None

        # Extract common entity fields
        entity_info = {}
        additional_info = {}

        # Dataset entity fields
        if "id" in response:
            entity_info["id"] = response["id"]
        if "name" in response:
            entity_info["name"] = response["name"]
        if "description" in response:
            additional_info["description"] = response["description"]

        # User entity fields
        if "displayName" in response:
            additional_info["display_name"] = response["displayName"]
        if "email" in response:
            additional_info["email"] = response["email"]

        # Page/Card entity fields
        if "title" in response:
            additional_info["title"] = response["title"]
        if "pageId" in response:
            additional_info["page_id"] = response["pageId"]

        # Application entity fields
        if "applicationId" in response:
            additional_info["application_id"] = response["applicationId"]

        # Add entity type based on common patterns
        if (
            "dataset_id" in str(result.request_metadata.url)
            if result.request_metadata
            else False
        ):
            entity_info["type"] = "dataset"
        elif (
            "users" in str(result.request_metadata.url)
            if result.request_metadata
            else False
        ):
            entity_info["type"] = "user"
        elif (
            "stacks" in str(result.request_metadata.url)
            if result.request_metadata
            else False
        ):
            entity_info["type"] = "page"
        elif (
            "cards" in str(result.request_metadata.url)
            if result.request_metadata
            else False
        ):
            entity_info["type"] = "card"
        elif (
            "applications" in str(result.request_metadata.url)
            if result.request_metadata
            else False
        ):
            entity_info["type"] = "application"
        else:
            entity_info["type"] = "unknown"

        # Add instance information if available
        if result.request_metadata and hasattr(result.request_metadata, "url"):
            url = result.request_metadata.url
            if ".domo.com" in url:
                instance = url.split("//")[1].split(".")[0] if "//" in url else None
                if instance:
                    additional_info["instance"] = instance

        # Add additional_info to entity_info
        if additional_info:
            entity_info["additional_info"] = additional_info

        return LogEntity.from_any(entity_info) if entity_info else None

    def process(
        self, result: Any, http_details: HTTPDetails | None = None
    ) -> tuple[dict[str, Any], HTTPDetails | None]:
        """Process route result and extract entity information.

        Args:
            result: The function result (should be ResponseGetData)
            http_details: Optional HTTP details to update

        Returns:
            Tuple of (result_context dict with entity info, updated http_details)
        """
        result_context = {}

        # Debug: Print what we're processing
        print(f"DEBUG DomoEntityProcessor: Processing result type: {type(result)}")
        if hasattr(result, "request_metadata") and result.request_metadata:
            print(f"DEBUG DomoEntityProcessor: URL: {result.request_metadata.url}")

        # Extract entity information
        entity = self._extract_entity_info(result)
        if entity:
            print(f"DEBUG DomoEntityProcessor: Extracted entity: {entity}")
            # Override the entity field directly - this should work since result_context is spread after log_context
            result_context["entity"] = entity
        else:
            print("DEBUG DomoEntityProcessor: No entity extracted")

        # Update HTTP details if it's a ResponseGetData object
        if isinstance(result, rgd.ResponseGetData) and http_details:
            http_details.status_code = result.status

            # Extract response size and body
            if hasattr(result, "response"):
                response = result.response
                if isinstance(response, str | bytes):
                    http_details.response_size = len(response)
                    response_str = str(response)
                    http_details.response_body = (
                        response_str[:500] if len(response_str) > 500 else response_str
                    )
                elif isinstance(response, dict):
                    # For dictionaries, show key information
                    http_details.response_size = len(str(response))
                    # Show first few keys and values for context
                    keys = list(response.keys())[:5]
                    summary = {k: response[k] for k in keys if k in response}
                    http_details.response_body = summary
                elif hasattr(response, "__len__"):
                    try:
                        response_len = len(response)
                    except TypeError:
                        response_len = None
                    else:
                        http_details.response_size = response_len
                        http_details.response_body = (
                            f"<{type(response).__name__} with {response_len} items>"
                        )
                else:
                    http_details.response_body = f"<{type(response).__name__}>"

            # Use request metadata if available
            if hasattr(result, "request_metadata") and result.request_metadata:
                metadata = result.request_metadata
                if not http_details.url:
                    http_details.url = metadata.url
                if not http_details.method:
                    http_details.method = metadata.method
                if not http_details.headers:
                    http_details.headers = metadata.headers
                if not http_details.params:
                    http_details.params = metadata.params
                if not http_details.request_body:
                    http_details.request_body = metadata.body

        return result_context, http_details


class ResponseGetDataProcessor(ResultProcessor):
    """Custom result processor for ResponseGetData objects."""

    def _sanitize_headers(self, headers: dict) -> dict:
        """Sanitize sensitive headers for logging."""
        if not headers:
            return headers

        sanitized = headers.copy()
        sensitive_headers = [
            "x-domo-developer-token",
            "authorization",
            "x-api-key",
            "cookie",
            "set-cookie",
        ]

        for header_name in sensitive_headers:
            # Case-insensitive check
            for key in list(sanitized.keys()):
                if key.lower() == header_name.lower():
                    sanitized[key] = "***"
                    break

        return sanitized

    def _format_response_body(self, response: Any) -> Any:
        """Format response body appropriately for logging."""
        if isinstance(response, dict):
            # Return dictionary as-is for proper JSON formatting
            return response
        elif isinstance(response, list):
            # Return list as-is for proper JSON formatting
            return response
        elif isinstance(response, str | bytes):
            # Try to parse as JSON if it looks like JSON
            try:
                import json

                response_str = str(response)
                # Check if it looks like JSON
                if response_str.strip().startswith(("{", "[")):
                    parsed = json.loads(response_str)
                    return parsed
                else:
                    # Return as string, truncated if too long
                    return (
                        response_str[:500] if len(response_str) > 500 else response_str
                    )
            except (json.JSONDecodeError, ValueError):
                # If not valid JSON, return as string
                response_str = str(response)
                return response_str[:500] if len(response_str) > 500 else response_str
        elif hasattr(response, "__len__"):
            try:
                length = len(response)
            except TypeError:
                return f"<{type(response).__name__}>"
            else:
                return f"<{type(response).__name__} with {length} items>"
        else:
            return f"<{type(response).__name__}>"

    def process(
        self, result: Any, http_details: HTTPDetails | None = None
    ) -> tuple[dict[str, Any], HTTPDetails | None]:
        """Process ResponseGetData result and update HTTP details.

        Args:
            result: The function result (should be ResponseGetData)
            http_details: Optional HTTP details to update

        Returns:
            Tuple of (result_context dict, updated http_details)
        """
        result_context = {}

        if isinstance(result, rgd.ResponseGetData) and http_details:
            # Update HTTP details with response information
            http_details.status_code = result.status

            # Extract response size and body
            if hasattr(result, "response"):
                response = result.response
                http_details.response_body = self._format_response_body(response)

                # Calculate response size
                if isinstance(response, str | bytes):
                    http_details.response_size = len(response)
                elif hasattr(response, "__len__"):
                    try:
                        http_details.response_size = len(response)
                    except TypeError:
                        http_details.response_size = None

            # Use request metadata if available to fill in missing request details
            if hasattr(result, "request_metadata") and result.request_metadata:
                metadata = result.request_metadata
                if not http_details.url:
                    http_details.url = metadata.url
                if not http_details.method:
                    http_details.method = metadata.method
                if not http_details.headers:
                    # Sanitize headers before setting
                    http_details.headers = self._sanitize_headers(metadata.headers)
                if not http_details.params:
                    http_details.params = metadata.params
                if not http_details.request_body:
                    http_details.request_body = metadata.body

        return result_context, http_details


__all__ = [
    "ResponseGetDataProcessor",
]
