"""Groups resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class GroupsResource(BaseResource):
    """
    Resource for Addepar Groups and Group Types API.

    Groups (CRUD):
        - get_group() - Get a single group
        - list_groups() - List all groups (paginated, with filters)
        - create_group() - Create a new group
        - create_groups() - Create multiple groups
        - update_group() - Update a group
        - update_groups() - Update multiple groups
        - delete_group() - Delete a group
        - delete_groups() - Delete multiple groups

    Group Types (CRUD):
        - get_group_type() - Get a single group type
        - list_group_types() - List all group types
        - create_group_type() - Create a new group type
        - update_group_type() - Update a group type
        - delete_group_type() - Delete a group type

    Member Methods:
        - get_members() - Get group member IDs
        - get_member_details() - Get full member entity details
        - add_members() - Add members to group
        - replace_members() - Replace all members
        - remove_members() - Remove members from group

    Child Group Methods:
        - get_child_groups() - Get child groups
        - add_child_groups() - Add child groups
        - replace_child_groups() - Replace all child groups

    Query Methods:
        - search_groups() - Search by name, type, or external ID
    """

    # =========================================================================
    # Tier 1: CRUD Methods
    # =========================================================================

    def get_group(self, group_id: str) -> Dict[str, Any]:
        """
        Get a single group by ID.

        Args:
            group_id: The ID of the group to retrieve.

        Returns:
            The group resource object containing id, type, attributes,
            and relationships.
        """
        response = self._get(f"/groups/{group_id}")
        data = response.json()
        group = data.get("data", {})
        logger.debug(f"Retrieved group {group_id}")
        return group

    def list_groups(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
        group_types: Optional[str] = None,
        ids: Optional[str] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        modified_before: Optional[str] = None,
        modified_after: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all groups with pagination and optional filters.

        Args:
            page_limit: Results per page (default: 500, max: 2000).
            group_types: Filter by group type ID.
            ids: Filter by specific group IDs (comma-separated).
            created_before: Groups created on/before date (YYYY-MM-DD).
            created_after: Groups created on/after date (YYYY-MM-DD).
            modified_before: Groups modified on/before date (YYYY-MM-DD).
            modified_after: Groups modified on/after date (YYYY-MM-DD).

        Returns:
            List of group resource objects.
        """
        params: Dict[str, Any] = {}

        if group_types is not None:
            params["filter[group_types]"] = group_types
        if ids is not None:
            params["filter[ids]"] = ids
        if created_before is not None:
            params["filter[created_before]"] = created_before
        if created_after is not None:
            params["filter[created_after]"] = created_after
        if modified_before is not None:
            params["filter[modified_before]"] = modified_before
        if modified_after is not None:
            params["filter[modified_after]"] = modified_after

        groups = list(
            self._paginate("/groups", page_limit=page_limit, params=params if params else None)
        )
        logger.debug(f"Listed {len(groups)} groups")
        return groups

    def create_group(
        self,
        name: str,
        group_type_id: str = "GROUPS",
        *,
        member_ids: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new group.

        Args:
            name: The name of the group. Required.
            group_type_id: The group type ID. Default: "GROUPS".
            member_ids: List of entity IDs to add as initial members.
            attributes: Additional attributes to set on the group.

        Returns:
            The created group resource object.
        """
        group_attributes: Dict[str, Any] = {"name": name}
        if attributes:
            group_attributes.update(attributes)

        relationships: Dict[str, Any] = {
            "group_type": {
                "data": {
                    "type": "group_types",
                    "id": group_type_id,
                }
            }
        }

        if member_ids:
            relationships["members"] = {
                "data": [
                    {"type": "entities", "id": entity_id}
                    for entity_id in member_ids
                ]
            }

        payload = {
            "data": {
                "type": "groups",
                "attributes": group_attributes,
                "relationships": relationships,
            }
        }

        response = self._post("/groups", json=payload)
        data = response.json()
        group = data.get("data", {})
        logger.info(f"Created group: {group.get('id')}")
        return group

    def create_groups(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple groups at once.

        Args:
            groups: List of group definitions. Each should have:
                - name (str): Group name. Required.
                - group_type_id (str): Group type ID. Default: "GROUPS".
                - member_ids (List[str], optional): Entity IDs to add as members.
                - attributes (Dict, optional): Additional attributes.

        Returns:
            List of created group resource objects.

        Example:
            groups = [
                {"name": "Group 1", "group_type_id": "GROUPS", "member_ids": ["1", "2"]},
                {"name": "Group 2", "group_type_id": "GROUPS"},
            ]
            created = client.ownership.groups.create_groups(groups)
        """
        data_items = []
        for group in groups:
            group_attributes: Dict[str, Any] = {"name": group["name"]}
            if "attributes" in group:
                group_attributes.update(group["attributes"])

            relationships: Dict[str, Any] = {
                "group_type": {
                    "data": {
                        "type": "group_types",
                        "id": group.get("group_type_id", "GROUPS"),
                    }
                }
            }

            if "member_ids" in group:
                relationships["members"] = {
                    "data": [
                        {"type": "entities", "id": entity_id}
                        for entity_id in group["member_ids"]
                    ]
                }

            data_items.append({
                "type": "groups",
                "attributes": group_attributes,
                "relationships": relationships,
            })

        payload = {"data": data_items}

        response = self._post("/groups", json=payload)
        data = response.json()
        created_groups = data.get("data", [])
        logger.info(f"Created {len(created_groups)} groups")
        return created_groups

    def update_group(
        self,
        group_id: str,
        *,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a group.

        Args:
            group_id: The ID of the group to update.
            name: New name for the group.
            attributes: Additional attributes to update.

        Returns:
            The updated group resource object.
        """
        group_attributes: Dict[str, Any] = {}

        if name is not None:
            group_attributes["name"] = name
        if attributes:
            group_attributes.update(attributes)

        payload = {
            "data": {
                "type": "groups",
                "id": group_id,
                "attributes": group_attributes,
            }
        }

        response = self._patch(f"/groups/{group_id}", json=payload)
        data = response.json()
        group = data.get("data", {})
        logger.info(f"Updated group: {group_id}")
        return group

    def update_groups(self, groups: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update multiple groups at once.

        Args:
            groups: List of group updates. Each should have:
                - id (str): Group ID. Required.
                - name (str, optional): New name.
                - member_ids (List[str], optional): Replace members.
                - child_group_ids (List[str], optional): Replace child groups.
                - attributes (Dict, optional): Additional attributes.

        Returns:
            List of updated group resource objects.

        Example:
            updates = [
                {"id": "1", "name": "New Name 1"},
                {"id": "2", "member_ids": ["entity_1", "entity_2"]},
            ]
            updated = client.ownership.groups.update_groups(updates)
        """
        data_items = []
        for group in groups:
            group_attributes: Dict[str, Any] = {}
            if "name" in group:
                group_attributes["name"] = group["name"]
            if "attributes" in group:
                group_attributes.update(group["attributes"])

            item: Dict[str, Any] = {
                "type": "groups",
                "id": group["id"],
                "attributes": group_attributes,
            }

            # Handle relationships if provided
            relationships: Dict[str, Any] = {}
            if "member_ids" in group:
                relationships["members"] = {
                    "data": [
                        {"type": "entities", "id": entity_id}
                        for entity_id in group["member_ids"]
                    ]
                }
            if "child_group_ids" in group:
                relationships["child_groups"] = {
                    "data": [
                        {"type": "groups", "id": child_id}
                        for child_id in group["child_group_ids"]
                    ]
                }

            if relationships:
                item["relationships"] = relationships

            data_items.append(item)

        payload = {"data": data_items}

        response = self._patch("/groups", json=payload)
        data = response.json()
        updated_groups = data.get("data", [])
        logger.info(f"Updated {len(updated_groups)} groups")
        return updated_groups

    def delete_group(self, group_id: str) -> None:
        """
        Delete a group.

        Args:
            group_id: The ID of the group to delete.
        """
        self._delete(f"/groups/{group_id}")
        logger.info(f"Deleted group: {group_id}")

    def delete_groups(self, group_ids: List[str]) -> None:
        """
        Delete multiple groups at once.

        Args:
            group_ids: List of group IDs to delete.
        """
        payload = {
            "data": [
                {"type": "groups", "id": group_id}
                for group_id in group_ids
            ]
        }

        self._delete("/groups", json=payload)
        logger.info(f"Deleted {len(group_ids)} groups")

    # =========================================================================
    # Member Methods
    # =========================================================================

    def get_members(self, group_id: str) -> List[Dict[str, Any]]:
        """
        Get a group's member entity IDs.

        Args:
            group_id: The ID of the group.

        Returns:
            List of entity relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/groups/{group_id}/relationships/members")
        data = response.json()
        members = data.get("data", [])
        logger.debug(f"Retrieved {len(members)} members for group {group_id}")
        return members

    def get_member_details(
        self,
        group_id: str,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Get full entity details for all members of a group.

        Args:
            group_id: The ID of the group.
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of entity resource objects with full attributes.
        """
        members = list(
            self._paginate(f"/groups/{group_id}/members", page_limit=page_limit)
        )
        logger.debug(f"Retrieved details for {len(members)} members of group {group_id}")
        return members

    def add_members(self, group_id: str, entity_ids: List[str]) -> None:
        """
        Add members to a group.

        Args:
            group_id: The ID of the group.
            entity_ids: List of entity IDs to add as members.
        """
        payload = {
            "data": [
                {"type": "entities", "id": entity_id}
                for entity_id in entity_ids
            ]
        }

        self._post(f"/groups/{group_id}/relationships/members", json=payload)
        logger.info(f"Added {len(entity_ids)} members to group {group_id}")

    def replace_members(self, group_id: str, entity_ids: List[str]) -> None:
        """
        Replace all members of a group.

        Args:
            group_id: The ID of the group.
            entity_ids: List of entity IDs to set as the new members.
        """
        payload = {
            "data": [
                {"type": "entities", "id": entity_id}
                for entity_id in entity_ids
            ]
        }

        self._patch(f"/groups/{group_id}/relationships/members", json=payload)
        logger.info(f"Replaced members of group {group_id} with {len(entity_ids)} entities")

    def remove_members(self, group_id: str, entity_ids: List[str]) -> None:
        """
        Remove members from a group.

        Args:
            group_id: The ID of the group.
            entity_ids: List of entity IDs to remove from the group.
        """
        payload = {
            "data": [
                {"type": "entities", "id": entity_id}
                for entity_id in entity_ids
            ]
        }

        self._delete(f"/groups/{group_id}/relationships/members", json=payload)
        logger.info(f"Removed {len(entity_ids)} members from group {group_id}")

    # =========================================================================
    # Child Group Methods
    # =========================================================================

    def get_child_groups(
        self,
        group_id: str,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Get a group's child groups.

        Args:
            group_id: The ID of the group.
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of child group resource objects with full attributes.
        """
        child_groups = list(
            self._paginate(f"/groups/{group_id}/child_groups", page_limit=page_limit)
        )
        logger.debug(f"Retrieved {len(child_groups)} child groups for group {group_id}")
        return child_groups

    def add_child_groups(self, group_id: str, child_group_ids: List[str]) -> None:
        """
        Add child groups to a group.

        Args:
            group_id: The ID of the parent group.
            child_group_ids: List of group IDs to add as children.
        """
        payload = {
            "data": [
                {"type": "groups", "id": child_id}
                for child_id in child_group_ids
            ]
        }

        self._post(f"/groups/{group_id}/relationships/child_groups", json=payload)
        logger.info(f"Added {len(child_group_ids)} child groups to group {group_id}")

    def replace_child_groups(self, group_id: str, child_group_ids: List[str]) -> None:
        """
        Replace all child groups of a group.

        Args:
            group_id: The ID of the parent group.
            child_group_ids: List of group IDs to set as the new children.
        """
        payload = {
            "data": [
                {"type": "groups", "id": child_id}
                for child_id in child_group_ids
            ]
        }

        self._patch(f"/groups/{group_id}/relationships/child_groups", json=payload)
        logger.info(f"Replaced child groups of group {group_id} with {len(child_group_ids)} groups")

    # =========================================================================
    # Query Methods
    # =========================================================================

    def search_groups(
        self,
        *,
        display_names: Optional[List[str]] = None,
        group_types: Optional[List[str]] = None,
        external_ids: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for groups by name, group type, or external ID.

        At least one search parameter must be provided.

        Args:
            display_names: List of group names to search for.
            group_types: List of group type IDs to filter by.
            external_ids: List of external ID objects, each with:
                - external_id_type: The external ID type name.
                - external_id: The external ID value.

        Returns:
            List of matching group resource objects.

        Example:
            # Search by name
            groups = client.ownership.groups.search_groups(
                display_names=["Smith Family", "Jones Trust"]
            )

            # Search by external ID
            groups = client.ownership.groups.search_groups(
                external_ids=[
                    {"external_id_type": "salesforce", "external_id": "abc123"}
                ]
            )
        """
        attributes: Dict[str, Any] = {}

        if display_names is not None:
            attributes["display_names"] = display_names
        if group_types is not None:
            attributes["group_types"] = group_types
        if external_ids is not None:
            attributes["external_ids"] = external_ids

        payload = {
            "data": {
                "type": "group_search",
                "attributes": attributes,
            }
        }

        response = self._post("/groups/query", json=payload)
        data = response.json()
        groups = data.get("data", [])
        logger.debug(f"Found {len(groups)} groups matching search criteria")
        return groups

    # =========================================================================
    # Group Types (CRUD)
    # =========================================================================

    def get_group_type(self, group_type_id: str) -> Dict[str, Any]:
        """
        Get a single group type by ID.

        Args:
            group_type_id: The ID (group_type_key) of the group type to retrieve.

        Returns:
            The group type resource object containing id, type, and attributes.
        """
        response = self._get(f"/group_types/{group_type_id}")
        data = response.json()
        group_type = data.get("data", {})
        logger.debug(f"Retrieved group type {group_type_id}")
        return group_type

    def list_group_types(
        self,
        *,
        is_permissioned_resource: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all group types.

        Note: This endpoint does not support pagination.

        Args:
            is_permissioned_resource: If True, filter to explicit access types.
                If False, filter to implicit access types.

        Returns:
            List of group type resource objects.
        """
        params: Dict[str, Any] = {}

        if is_permissioned_resource is not None:
            params["is_permissioned_resource"] = str(is_permissioned_resource).lower()

        response = self._get("/group_types", params=params if params else None)
        data = response.json()
        group_types = data.get("data", [])
        logger.debug(f"Listed {len(group_types)} group types")
        return group_types

    def create_group_type(
        self,
        group_type_key: str,
        display_name: str,
        *,
        is_permissioned_resource: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a new group type.

        Args:
            group_type_key: The unique ID/key for the group type.
            display_name: The user-facing name for the group type.
            is_permissioned_resource: If True (default), users need explicit access
                to groups of this type. If False, users need access to each
                individual member to access groups of this type.

        Returns:
            The created group type resource object.

        Raises:
            ConflictError: If group_type_key already exists.
        """
        payload = {
            "data": {
                "type": "group_types",
                "attributes": {
                    "group_type_key": group_type_key,
                    "display_name": display_name,
                    "is_permissioned_resource": is_permissioned_resource,
                },
            }
        }

        response = self._post("/group_types", json=payload)
        data = response.json()
        group_type = data.get("data", {})
        logger.info(f"Created group type: {group_type.get('id')}")
        return group_type

    def update_group_type(
        self,
        group_type_id: str,
        *,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a group type.

        Only the display_name can be updated. The default "GROUPS" type
        cannot be modified.

        Args:
            group_type_id: The ID of the group type to update.
            display_name: The new user-facing name for the group type.

        Returns:
            The updated group type resource object.
        """
        attributes: Dict[str, Any] = {}

        if display_name is not None:
            attributes["display_name"] = display_name

        payload = {
            "data": {
                "type": "group_types",
                "id": group_type_id,
                "attributes": attributes,
            }
        }

        response = self._patch(f"/group_types/{group_type_id}", json=payload)
        data = response.json()
        group_type = data.get("data", {})
        logger.info(f"Updated group type: {group_type_id}")
        return group_type

    def delete_group_type(self, group_type_id: str) -> None:
        """
        Delete a group type.

        The default "GROUPS" type cannot be deleted.

        Args:
            group_type_id: The ID of the group type to delete.
        """
        self._delete(f"/group_types/{group_type_id}")
        logger.info(f"Deleted group type: {group_type_id}")
