"""Target Allocations resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class TargetAllocationsResource(BaseResource):
    """
    Resource for Addepar Target Allocations APIs.

    Manage allocation models and allocation templates in Addepar.

    Allocation Models Methods:
        - get_allocation_model() - Get a single allocation model
        - list_allocation_models() - List all allocation models
        - create_allocation_model() - Create an allocation model
        - update_allocation_model() - Update an allocation model (name only)
        - delete_allocation_model() - Delete an allocation model

    Allocation Templates Methods:
        - get_allocation_template() - Get a single allocation template
        - list_allocation_templates() - List all allocation templates
        - create_allocation_template() - Create an allocation template
        - update_allocation_template() - Partial update (preserves existing data)
        - replace_allocation_template() - Full replacement (does not preserve data)
        - delete_allocation_template() - Delete an allocation template
    """

    # =========================================================================
    # Allocation Models Methods
    # =========================================================================

    def get_allocation_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get an allocation model by ID.

        Args:
            model_id: The ID of the allocation model.

        Returns:
            Allocation model resource object containing id, type, and attributes
            (name, attribute_ids).
        """
        response = self._get(f"/allocation_models/{model_id}")
        data = response.json()
        model = data.get("data", {})
        logger.debug(f"Retrieved allocation model {model_id}")
        return model

    def list_allocation_models(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all allocation models.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of allocation model resource objects containing id, type,
            and attributes (name, attribute_ids).
        """
        models = list(self._paginate("/allocation_models", page_limit=page_limit))
        logger.debug(f"Listed {len(models)} allocation models")
        return models

    def create_allocation_model(
        self,
        name: str,
        attribute_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Create an allocation model.

        Args:
            name: Display name for the allocation model.
            attribute_ids: List of attribute identifiers defining the dimensions
                of the allocation model (e.g., ["asset_class", "market_cap"]).

        Returns:
            Created allocation model resource object.

        Note:
            The attribute_ids are immutable after creation. To change the
            dimensions, create a new allocation model.

        Example:
            model = client.admin.target_allocations.create_allocation_model(
                name="Conservative Growth Model",
                attribute_ids=["asset_class", "market_cap", "sector"]
            )
        """
        payload = {
            "data": {
                "type": "allocation_models",
                "attributes": {
                    "name": name,
                    "attribute_ids": attribute_ids,
                },
            }
        }

        response = self._post("/allocation_models", json=payload)
        data = response.json()
        model = data.get("data", {})
        model_id = model.get("id", "unknown")
        logger.info(f"Created allocation model: {model_id}")
        return model

    def update_allocation_model(
        self,
        model_id: str,
        name: str,
    ) -> Dict[str, Any]:
        """
        Update an allocation model.

        Args:
            model_id: The ID of the allocation model to update.
            name: New display name for the allocation model.

        Returns:
            Updated allocation model resource object.

        Note:
            Only the name can be updated. The attribute_ids are immutable
            after creation.

        Example:
            model = client.admin.target_allocations.update_allocation_model(
                model_id="123",
                name="Updated Model Name"
            )
        """
        payload = {
            "data": {
                "type": "allocation_models",
                "id": model_id,
                "attributes": {
                    "name": name,
                },
            }
        }

        response = self._patch(f"/allocation_models/{model_id}", json=payload)
        data = response.json()
        model = data.get("data", {})
        logger.info(f"Updated allocation model: {model_id}")
        return model

    def delete_allocation_model(self, model_id: str) -> None:
        """
        Delete an allocation model.

        Args:
            model_id: The ID of the allocation model to delete.

        Note:
            Deleting an allocation model will also delete any associated
            allocation templates.
        """
        self._delete(f"/allocation_models/{model_id}")
        logger.info(f"Deleted allocation model: {model_id}")

    # =========================================================================
    # Allocation Templates Methods
    # =========================================================================

    def get_allocation_template(self, template_id: str) -> Dict[str, Any]:
        """
        Get an allocation template by ID.

        Args:
            template_id: The ID of the allocation template.

        Returns:
            Allocation template resource object containing id, type, and
            attributes (model_id, name, description, allocation_intervals).
        """
        response = self._get(f"/allocation_templates/{template_id}")
        data = response.json()
        template = data.get("data", {})
        logger.debug(f"Retrieved allocation template {template_id}")
        return template

    def list_allocation_templates(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all allocation templates.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of allocation template resource objects containing id, type,
            and attributes (model_id, name, description, allocation_intervals).
        """
        templates = list(
            self._paginate("/allocation_templates", page_limit=page_limit)
        )
        logger.debug(f"Listed {len(templates)} allocation templates")
        return templates

    def create_allocation_template(
        self,
        model_id: str,
        name: str,
        allocation_intervals: List[Dict[str, Any]],
        *,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an allocation template.

        Args:
            model_id: ID of the associated allocation model.
            name: Display name for the allocation template.
            allocation_intervals: Allocation distribution data as a list of
                interval objects, each containing an "allocations" array.
            description: Optional description of the template.

        Returns:
            Created allocation template resource object.

        Note:
            The model_id is immutable after creation. To change the model,
            create a new allocation template.

        Example:
            template = client.admin.target_allocations.create_allocation_template(
                model_id="123",
                name="Conservative Growth Template",
                description="A balanced allocation strategy",
                allocation_intervals=[
                    {
                        "allocations": [
                            {
                                "parent_id": None,
                                "attribute_id": "asset_class",
                                "attribute_value": "EQUITY",
                                "target_allocation": 60.0,
                                "min_allocation": 50.0,
                                "max_allocation": 70.0,
                                "children": []
                            }
                        ]
                    }
                ]
            )
        """
        attributes: Dict[str, Any] = {
            "model_id": model_id,
            "name": name,
            "allocation_intervals": allocation_intervals,
        }

        if description is not None:
            attributes["description"] = description

        payload = {
            "data": {
                "type": "allocation_templates",
                "attributes": attributes,
            }
        }

        response = self._post("/allocation_templates", json=payload)
        data = response.json()
        template = data.get("data", {})
        template_id = template.get("id", "unknown")
        logger.info(f"Created allocation template: {template_id}")
        return template

    def update_allocation_template(
        self,
        template_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        allocation_intervals: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Partially update an allocation template (PATCH).

        This preserves existing data for fields not provided.

        Args:
            template_id: The ID of the allocation template to update.
            name: New display name (optional).
            description: New description (optional).
            allocation_intervals: New allocation distribution data (optional).

        Returns:
            Updated allocation template resource object.

        Note:
            The model_id is immutable and cannot be updated.

        Example:
            template = client.admin.target_allocations.update_allocation_template(
                template_id="456",
                name="Updated Template Name",
                description="Updated description"
            )
        """
        attributes: Dict[str, Any] = {}

        if name is not None:
            attributes["name"] = name
        if description is not None:
            attributes["description"] = description
        if allocation_intervals is not None:
            attributes["allocation_intervals"] = allocation_intervals

        payload = {
            "data": {
                "type": "allocation_templates",
                "id": template_id,
                "attributes": attributes,
            }
        }

        response = self._patch(f"/allocation_templates/{template_id}", json=payload)
        data = response.json()
        template = data.get("data", {})
        logger.info(f"Updated allocation template: {template_id}")
        return template

    def replace_allocation_template(
        self,
        template_id: str,
        model_id: str,
        name: str,
        allocation_intervals: List[Dict[str, Any]],
        *,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fully replace an allocation template (PUT).

        This does NOT preserve existing data - all fields must be provided.

        Args:
            template_id: The ID of the allocation template to replace.
            model_id: ID of the associated allocation model (must match existing).
            name: Display name for the allocation template.
            allocation_intervals: Complete allocation distribution data.
            description: Optional description of the template.

        Returns:
            Replaced allocation template resource object.

        Note:
            Unlike update_allocation_template (PATCH), this method replaces
            all data. Any fields not provided will be cleared/reset.

        Example:
            template = client.admin.target_allocations.replace_allocation_template(
                template_id="456",
                model_id="123",
                name="Completely Replaced Template",
                allocation_intervals=[
                    {
                        "allocations": [
                            {
                                "parent_id": None,
                                "attribute_id": "asset_class",
                                "attribute_value": "FIXED_INCOME",
                                "target_allocation": 100.0,
                                "children": []
                            }
                        ]
                    }
                ]
            )
        """
        attributes: Dict[str, Any] = {
            "model_id": model_id,
            "name": name,
            "allocation_intervals": allocation_intervals,
        }

        if description is not None:
            attributes["description"] = description

        payload = {
            "data": {
                "type": "allocation_templates",
                "id": template_id,
                "attributes": attributes,
            }
        }

        response = self._put(f"/allocation_templates/{template_id}", json=payload)
        data = response.json()
        template = data.get("data", {})
        logger.info(f"Replaced allocation template: {template_id}")
        return template

    def delete_allocation_template(self, template_id: str) -> None:
        """
        Delete an allocation template.

        Args:
            template_id: The ID of the allocation template to delete.
        """
        self._delete(f"/allocation_templates/{template_id}")
        logger.info(f"Deleted allocation template: {template_id}")
