"""External IDs resource for the Addepar API."""
import logging
from typing import Any, Dict, List

from ..base import BaseResource

logger = logging.getLogger("addepy")


class ExternalIdsResource(BaseResource):
    """
    Resource for Addepar External ID Types API.

    External ID Types represent non-Addepar systems or applications you wish
    to map to External IDs. Once you've created a type, use the Entities or
    Groups API to map entities/groups to external system identifiers.

    Methods:
        - get_external_id_type() - Get a single external ID type
        - list_external_id_types() - List all external ID types
        - create_external_id_type() - Create a new external ID type
        - update_external_id_type() - Update an external ID type
        - delete_external_id_type() - Delete an external ID type
    """

    def get_external_id_type(self, external_id_type_id: str) -> Dict[str, Any]:
        """
        Get an external ID type by ID.

        Args:
            external_id_type_id: The ID (external_type_key) of the type.

        Returns:
            External ID type resource object containing id, type, and
            attributes (external_type_key, display_name).

        Example:
            ext_type = client.ownership.external_ids.get_external_id_type(
                external_id_type_id="salesforce"
            )
            print(ext_type["attributes"]["display_name"])
        """
        response = self._get(f"/external_id_types/{external_id_type_id}")
        data = response.json()
        result = data.get("data", {})
        logger.debug(f"Retrieved external ID type: {external_id_type_id}")
        return result

    def list_external_id_types(self) -> List[Dict[str, Any]]:
        """
        List all external ID types.

        Returns:
            List of external ID type resource objects containing id, type,
            and attributes (external_type_key, display_name).

        Example:
            types = client.ownership.external_ids.list_external_id_types()
            for t in types:
                print(f"{t['id']}: {t['attributes']['display_name']}")
        """
        response = self._get("/external_id_types")
        data = response.json()
        results = data.get("data", [])
        logger.debug(f"Listed {len(results)} external ID types")
        return results

    def create_external_id_type(
        self,
        external_type_key: str,
        display_name: str,
    ) -> Dict[str, Any]:
        """
        Create a new external ID type.

        Args:
            external_type_key: Unique key for the external ID type.
            display_name: Display name for the external ID type.

        Returns:
            The created external ID type resource object.

        Example:
            new_type = client.ownership.external_ids.create_external_id_type(
                external_type_key="salesforce",
                display_name="Salesforce"
            )
        """
        payload = {
            "data": {
                "type": "external_id_types",
                "attributes": {
                    "external_type_key": external_type_key,
                    "display_name": display_name,
                },
            }
        }

        response = self._post("/external_id_types", json=payload)
        data = response.json()
        result = data.get("data", {})
        logger.info(f"Created external ID type: {external_type_key}")
        return result

    def update_external_id_type(
        self,
        external_id_type_id: str,
        display_name: str,
    ) -> Dict[str, Any]:
        """
        Update an external ID type's display name.

        Args:
            external_id_type_id: The ID (external_type_key) of the type.
            display_name: New display name for the external ID type.

        Returns:
            The updated external ID type resource object.

        Example:
            updated = client.ownership.external_ids.update_external_id_type(
                external_id_type_id="salesforce",
                display_name="Salesforce CRM"
            )
        """
        payload = {
            "data": {
                "id": external_id_type_id,
                "type": "external_id_types",
                "attributes": {
                    "display_name": display_name,
                },
            }
        }

        response = self._patch(f"/external_id_types/{external_id_type_id}", json=payload)
        data = response.json()
        result = data.get("data", {})
        logger.info(f"Updated external ID type: {external_id_type_id}")
        return result

    def delete_external_id_type(self, external_id_type_id: str) -> None:
        """
        Delete an external ID type.

        Note: The external ID type cannot be deleted if it is associated
        with any Addepar objects.

        Args:
            external_id_type_id: The ID (external_type_key) of the type.

        Example:
            client.ownership.external_ids.delete_external_id_type(
                external_id_type_id="salesforce"
            )
        """
        self._delete(f"/external_id_types/{external_id_type_id}")
        logger.info(f"Deleted external ID type: {external_id_type_id}")
