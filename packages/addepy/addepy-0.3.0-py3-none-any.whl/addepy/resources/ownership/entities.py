"""Entities resource for the Addepar API."""

import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT, UnderlyingType
from ...exceptions import AddePyError
from ..base import BaseResource

logger = logging.getLogger("addepy")


class EntitiesResource(BaseResource):
    """
    Resource for Addepar Entities and Entity Types API.

    Entities (CRUD):
        - get_entity() - Get a single entity by ID
        - list_entities() - List all entities with pagination and filtering
        - create_entity() - Create a single entity
        - create_entities() - Bulk create entities
        - update_entity() - Update a single entity
        - update_entities() - Bulk update entities
        - delete_entity() - Delete a single entity
        - delete_entities() - Bulk delete entities

    Entity Types (Read-only):
        - get_entity_type() - Get a single model type by API name
        - list_entity_types() - List all available model types
    """

    # =========================================================================
    # Tier 1: CRUD Wrappers
    # =========================================================================

    def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        Get a single entity by ID.

        Args:
            entity_id: The ID of the entity to retrieve.

        Returns:
            The entity resource object containing id, type, and attributes.
        """
        response = self._get(f"/entities/{entity_id}")
        data = response.json()
        entity = data.get("data", {})
        logger.debug(f"Retrieved entity {entity_id}")
        return entity

    def list_entities(
        self,
        *,
        model_types: Optional[List[str]] = None,
        linking_status: Optional[str] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        modified_before: Optional[str] = None,
        modified_after: Optional[str] = None,
        ids: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all entities with optional filtering and pagination.

        Args:
            model_types: Filter by model types (e.g., ["TRUST", "FINANCIAL_ACCOUNT"]).
            linking_status: Filter by linking status ("linked" or "unlinked").
            created_before: Filter by creation date (YYYY-MM-DD).
            created_after: Filter by creation date (YYYY-MM-DD).
            modified_before: Filter by modification date (YYYY-MM-DD).
            modified_after: Filter by modification date (YYYY-MM-DD).
            ids: Filter by specific entity IDs.
            fields: Specific attributes to return (e.g., ["original_name", "model_type"]).
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of entity resource objects.
        """
        params: Dict[str, Any] = {}

        if model_types:
            params["filter[model_types]"] = ",".join(model_types)
        if linking_status:
            params["filter[linking_status]"] = linking_status
        if created_before:
            params["filter[created_before]"] = created_before
        if created_after:
            params["filter[created_after]"] = created_after
        if modified_before:
            params["filter[modified_before]"] = modified_before
        if modified_after:
            params["filter[modified_after]"] = modified_after
        if ids:
            params["filter[ids]"] = ",".join(ids)
        if fields is not None:
            params["fields[entities]"] = ",".join(fields) if fields else "[]"

        entities = list(self._paginate("/entities", params=params, page_limit=page_limit))
        logger.debug(f"Listed {len(entities)} entities")
        return entities

    def create_entity(
        self,
        original_name: str,
        model_type: str,
        currency_factor: Optional[str] = None,
        *,
        underlying_type: Optional[UnderlyingType] = None,
        delivery_price: Optional[Dict[str, Any]] = None,
        allow_new_investment_types: bool = False,
        **attributes: Any,
    ) -> Dict[str, Any]:
        """
        Create a single entity.

        Args:
            original_name: Name of the entity (e.g., "Smith Trust").
            model_type: The entity type (e.g., "TRUST", "PERSON_NODE").
            currency_factor: Currency code (e.g., "USD"). Required for non-client entities.
            underlying_type: Required for forward/futures contracts. One of:
                INTEREST_RATE, CURRENCY, COMMODITY, SECURITY, INDEX.
            delivery_price: Required for forward contracts. Money value object,
                e.g., {"value": 100.5, "currency": "USD"}.
            allow_new_investment_types: Set True if creating a custom/new investment type.
            **attributes: Additional attributes for the entity.

        Returns:
            The created entity resource object containing id, type, and attributes.

        Raises:
            AddePyError: If entity creation fails.
        """
        entity_attributes = {
            "original_name": original_name,
            "model_type": model_type,
            **attributes,
        }
        if currency_factor is not None:
            entity_attributes["currency_factor"] = currency_factor
        if underlying_type is not None:
            entity_attributes["underlying_type"] = underlying_type
        if delivery_price is not None:
            entity_attributes["delivery_price"] = delivery_price

        payload = {
            "data": {
                "type": "entities",
                "attributes": entity_attributes,
            }
        }

        params = {}
        if allow_new_investment_types:
            params["allow_new_investment_types"] = "true"

        response = self._post("/entities", json=payload, params=params if params else None)
        data = response.json()

        entity = data.get("data", {})
        if not entity.get("id"):
            raise AddePyError(f"Failed to create entity: {data}")

        logger.info(f"Created entity: {entity.get('id')}")
        return entity

    def create_entities(
        self,
        entities: List[Dict[str, Any]],
        *,
        allow_new_investment_types: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Bulk create entities.

        Args:
            entities: List of entity attribute dicts. Each must contain at minimum:
                      - original_name: Name of the entity
                      - model_type: The entity type
                      - currency_factor: Currency (required for non-client entities)
            allow_new_investment_types: Set True if creating custom/new investment types.

        Returns:
            List of created entity resource objects.

        Raises:
            AddePyError: If entity creation fails.
        """
        payload = {
            "data": [
                {"type": "entities", "attributes": entity}
                for entity in entities
            ]
        }

        params = {}
        if allow_new_investment_types:
            params["allow_new_investment_types"] = "true"

        response = self._post("/entities", json=payload, params=params if params else None)
        data = response.json()

        created = data.get("data", [])

        if len(created) != len(entities):
            raise AddePyError(f"Failed to create all entities: {data}")

        logger.info(f"Created {len(created)} entities")
        return created

    def update_entity(
        self,
        entity_id: str,
        *,
        allow_new_investment_types: bool = False,
        **attributes: Any,
    ) -> Dict[str, Any]:
        """
        Update a single entity.

        Args:
            entity_id: The ID of the entity to update.
            allow_new_investment_types: Set True if applicable.
            **attributes: Attributes to update (e.g., original_name="New Name").

        Returns:
            The updated entity resource object.

        Note:
            The model_type attribute generally cannot be updated.
        """
        payload = {
            "data": {
                "id": entity_id,
                "type": "entities",
                "attributes": attributes,
            }
        }

        params = {}
        if allow_new_investment_types:
            params["allow_new_investment_types"] = "true"

        response = self._patch(
            f"/entities/{entity_id}",
            json=payload,
            params=params if params else None,
        )
        data = response.json()
        entity = data.get("data", {})

        logger.info(f"Updated entity: {entity_id}")
        return entity

    def update_entities(
        self,
        entities: List[Dict[str, Any]],
        *,
        allow_new_investment_types: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Bulk update entities.

        Args:
            entities: List of entity update dicts. Each must contain:
                      - id: The entity ID to update
                      - Plus any attributes to update
            allow_new_investment_types: Set True if applicable.

        Returns:
            List of updated entity resource objects.

        Note:
            The model_type attribute generally cannot be updated.
        """
        payload = {
            "data": [
                {
                    "id": entity["id"],
                    "type": "entities",
                    "attributes": {k: v for k, v in entity.items() if k != "id"},
                }
                for entity in entities
            ]
        }

        params = {}
        if allow_new_investment_types:
            params["allow_new_investment_types"] = "true"

        response = self._patch(
            "/entities",
            json=payload,
            params=params if params else None,
        )
        data = response.json()
        updated = data.get("data", [])

        logger.info(f"Updated {len(updated)} entities")
        return updated

    def delete_entity(self, entity_id: str) -> None:
        """
        Delete a single entity.

        Args:
            entity_id: The ID of the entity to delete.

        Note:
            Cannot delete an entity if it holds other entities or is referenced
            by positions.
        """
        self._delete(f"/entities/{entity_id}")
        logger.info(f"Deleted entity: {entity_id}")

    def delete_entities(self, entity_ids: List[str]) -> None:
        """
        Bulk delete entities.

        Args:
            entity_ids: List of entity IDs to delete.

        Note:
            Cannot delete entities that hold other entities or are referenced
            by positions.
        """
        payload = {
            "data": [
                {"id": entity_id, "type": "entities"}
                for entity_id in entity_ids
            ]
        }

        self._delete("/entities", json=payload)
        logger.info(f"Deleted {len(entity_ids)} entities")

    # =========================================================================
    # Entity Types (Read-Only)
    # =========================================================================

    def get_entity_type(self, type_id: str) -> Dict[str, Any]:
        """
        Get a single model type by its API name.

        Args:
            type_id: The API name of the model type (e.g., "bond", "trust",
                     "person_node", "financial_account").

        Returns:
            The model type resource object containing:
                - display_name: Human-readable name
                - category: Broad category classification
                - ownership_type: Ownership structure (share_based, percent_based, value_based)
                - entity_attributes: Dictionary of available attributes for this type
        """
        response = self._get(f"/entity_types/{type_id}")
        data = response.json()
        entity_type = data.get("data", {})
        logger.debug(f"Retrieved entity type: {type_id}")
        return entity_type

    def list_entity_types(self) -> List[Dict[str, Any]]:
        """
        List all available model types.

        Returns:
            List of model type resource objects, each containing display_name,
            category, ownership_type, and entity_attributes.

        Note:
            This endpoint does not support pagination.
        """
        response = self._get("/entity_types")
        data = response.json()
        entity_types = data.get("data", [])
        logger.debug(f"Listed {len(entity_types)} entity types")
        return entity_types
