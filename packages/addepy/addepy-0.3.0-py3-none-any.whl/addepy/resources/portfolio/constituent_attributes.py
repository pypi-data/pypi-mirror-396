"""Constituent Attributes resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional, Union

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class ConstituentAttributesResource(BaseResource):
    """
    Resource for Addepar Constituent Attributes API.

    Constituents are investments held by a composite security (e.g., ETF).
    Use this API to assign attribute values to security master constituents
    via their ASM ID.

    Note: Entity-level attributes take precedence over constituent attributes.

    Single Operations:
        - get_constituent_attribute() - Get a single attribute
        - list_constituent_attributes() - List all with optional filter
        - create_constituent_attribute() - Create single attribute
        - update_constituent_attribute() - Update single attribute
        - delete_constituent_attribute() - Delete single attribute

    Bulk Operations:
        - create_constituent_attributes() - Create multiple attributes
        - update_constituent_attributes() - Update multiple attributes
        - delete_constituent_attributes_by_asm() - Delete all for an ASM ID
    """

    # =========================================================================
    # Single Operations
    # =========================================================================

    def get_constituent_attribute(self, attribute_id: str) -> Dict[str, Any]:
        """
        Get a constituent attribute by ID.

        Args:
            attribute_id: The constituent attribute ID.

        Returns:
            Constituent attribute resource object containing id, type, and
            attributes (asm_id, attribute_key, values).

        Example:
            attr = client.portfolio.constituent_attributes.get_constituent_attribute("1")
            print(f"ASM: {attr['attributes']['asm_id']}")
            print(f"Key: {attr['attributes']['attribute_key']}")
        """
        response = self._get(f"/constituent_attributes/{attribute_id}")
        data = response.json()
        result = data.get("data", {})
        logger.debug(f"Retrieved constituent attribute: {attribute_id}")
        return result

    def list_constituent_attributes(
        self,
        *,
        asm_id: Optional[int] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all constituent attributes.

        Args:
            asm_id: Optional ASM ID to filter by.
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of constituent attribute resource objects.

        Example:
            # List all
            attrs = client.portfolio.constituent_attributes.list_constituent_attributes()

            # Filter by ASM ID
            attrs = client.portfolio.constituent_attributes.list_constituent_attributes(
                asm_id=123456
            )
        """
        params: Dict[str, Any] = {}
        if asm_id is not None:
            params["asmId"] = asm_id

        attributes = list(
            self._paginate(
                "/constituent_attributes",
                page_limit=page_limit,
                params=params if params else None,
            )
        )
        logger.debug(f"Listed {len(attributes)} constituent attributes")
        return attributes

    def create_constituent_attribute(
        self,
        asm_id: int,
        attribute_key: str,
        values: Union[Any, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Create a constituent attribute.

        Args:
            asm_id: The ASM ID of the constituent.
            attribute_key: The attribute's API field name.
            values: The attribute value. Can be a simple value (string, bool,
                number) or a time-varying list of dicts with date, value,
                and optional weight keys.

        Returns:
            The created constituent attribute resource object.

        Example:
            # Simple value
            attr = client.portfolio.constituent_attributes.create_constituent_attribute(
                asm_id=123456,
                attribute_key="_custom_boolean_1",
                values=True
            )

            # Time-varying value
            attr = client.portfolio.constituent_attributes.create_constituent_attribute(
                asm_id=123456,
                attribute_key="asset_class",
                values=[
                    {"date": None, "value": "Equity"},
                    {"date": "2024-12-31", "value": "Private Equity"}
                ]
            )
        """
        payload = {
            "data": {
                "type": "constituent_attributes",
                "attributes": {
                    "asm_id": asm_id,
                    "attribute_key": attribute_key,
                    "values": values,
                },
            }
        }

        response = self._post("/constituent_attributes", json=payload)
        data = response.json()
        result = data.get("data", {})
        logger.info(f"Created constituent attribute for ASM {asm_id}: {attribute_key}")
        return result

    def update_constituent_attribute(
        self,
        attribute_id: str,
        values: Union[Any, List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """
        Update a constituent attribute's value.

        Note: For time-varying or weighted attribute values, you must provide
        the entire attribute history in the request payload.

        Args:
            attribute_id: The constituent attribute ID.
            values: The new attribute value(s).

        Returns:
            The updated constituent attribute resource object.

        Example:
            updated = client.portfolio.constituent_attributes.update_constituent_attribute(
                attribute_id="1",
                values=[{"date": None, "value": "Private Equity", "weight": 1.0}]
            )
        """
        payload = {
            "data": {
                "id": attribute_id,
                "type": "constituent_attributes",
                "attributes": {
                    "values": values,
                },
            }
        }

        response = self._patch(f"/constituent_attributes/{attribute_id}", json=payload)
        data = response.json()
        result = data.get("data", {})
        logger.info(f"Updated constituent attribute: {attribute_id}")
        return result

    def delete_constituent_attribute(self, attribute_id: str) -> None:
        """
        Delete a constituent attribute.

        Args:
            attribute_id: The constituent attribute ID.

        Example:
            client.portfolio.constituent_attributes.delete_constituent_attribute("1")
        """
        self._delete(f"/constituent_attributes/{attribute_id}")
        logger.info(f"Deleted constituent attribute: {attribute_id}")

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    def create_constituent_attributes(
        self,
        attributes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Create multiple constituent attributes in bulk.

        Args:
            attributes: List of attribute dicts, each containing:
                - asm_id (int): The ASM ID
                - attribute_key (str): The attribute's API field name
                - values: The attribute value(s)

        Returns:
            List of created constituent attribute resource objects.

        Example:
            attrs = client.portfolio.constituent_attributes.create_constituent_attributes([
                {
                    "asm_id": 123,
                    "attribute_key": "_custom_boolean_1",
                    "values": True
                },
                {
                    "asm_id": 123,
                    "attribute_key": "_custom_currency_1",
                    "values": "EUR"
                }
            ])
        """
        payload = {
            "data": [
                {
                    "type": "constituent_attributes",
                    "attributes": attr,
                }
                for attr in attributes
            ]
        }

        response = self._post("/constituent_attributes", json=payload)
        data = response.json()
        results = data.get("data", [])
        logger.info(f"Created {len(results)} constituent attributes")
        return results

    def update_constituent_attributes(
        self,
        updates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Update multiple constituent attributes in bulk.

        Args:
            updates: List of update dicts, each containing:
                - id (str): The constituent attribute ID
                - values: The new attribute value(s)

        Returns:
            List of updated constituent attribute resource objects.

        Example:
            updated = client.portfolio.constituent_attributes.update_constituent_attributes([
                {
                    "id": "1",
                    "values": [{"date": None, "value": "Private Equity", "weight": 1.0}]
                },
                {
                    "id": "2",
                    "values": [{"date": None, "value": "Private Equity", "weight": 1.0}]
                }
            ])
        """
        payload = {
            "data": [
                {
                    "id": update["id"],
                    "type": "constituent_attributes",
                    "attributes": {
                        "values": update["values"],
                    },
                }
                for update in updates
            ]
        }

        response = self._patch("/constituent_attributes", json=payload)
        data = response.json()
        results = data.get("data", [])
        logger.info(f"Updated {len(results)} constituent attributes")
        return results

    def delete_constituent_attributes_by_asm(self, asm_id: int) -> None:
        """
        Delete all constituent attributes for an ASM ID.

        Args:
            asm_id: The ASM ID to delete all attributes for.

        Example:
            client.portfolio.constituent_attributes.delete_constituent_attributes_by_asm(
                asm_id=123456
            )
        """
        self._delete(f"/constituent_attributes?asmId={asm_id}")
        logger.info(f"Deleted all constituent attributes for ASM {asm_id}")
