"""Roles resource for the Addepar API."""
import logging
from typing import Any, Dict, List

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class RolesResource(BaseResource):
    """
    Resource for Addepar Roles API.

    Roles represent standard sets of permissions available to your firm.
    Note: Roles can only be created/deleted in the Addepar application.
    The API only allows viewing roles and managing user assignments.

    Read Methods:
        - get_role() - Get a single role
        - list_roles() - List all roles (paginated)

    User Assignment Methods:
        - get_assigned_users() - Get assigned user IDs
        - get_assigned_user_details() - Get full user details
        - assign_users() - Assign users to role
        - replace_assigned_users() - Replace all assigned users
        - remove_users() - Remove users from role
    """

    # =========================================================================
    # Read Methods
    # =========================================================================

    def get_role(self, role_id: str) -> Dict[str, Any]:
        """
        Get a single role by ID.

        Args:
            role_id: The ID of the role to retrieve.

        Returns:
            The role resource object containing id, type, attributes,
            and relationships.
        """
        response = self._get(f"/roles/{role_id}")
        data = response.json()
        role = data.get("data", {})
        logger.debug(f"Retrieved role {role_id}")
        return role

    def list_roles(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all roles with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of role resource objects.
        """
        roles = list(self._paginate("/roles", page_limit=page_limit))
        logger.debug(f"Listed {len(roles)} roles")
        return roles

    # =========================================================================
    # User Assignment Methods
    # =========================================================================

    def get_assigned_users(self, role_id: str) -> List[Dict[str, Any]]:
        """
        Get a role's assigned user IDs.

        Args:
            role_id: The ID of the role.

        Returns:
            List of user relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/roles/{role_id}/relationships/assigned_users")
        data = response.json()
        users = data.get("data", [])
        logger.debug(f"Retrieved {len(users)} assigned users for role {role_id}")
        return users

    def get_assigned_user_details(
        self,
        role_id: str,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Get full user details for users assigned to a role.

        Args:
            role_id: The ID of the role.
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of user resource objects with full attributes.
        """
        users = list(
            self._paginate(f"/roles/{role_id}/assigned_users", page_limit=page_limit)
        )
        logger.debug(f"Retrieved details for {len(users)} users assigned to role {role_id}")
        return users

    def assign_users(self, role_id: str, user_ids: List[str]) -> None:
        """
        Assign users to a role.

        Note: If a user is already assigned to a different role, calling this
        will overwrite their previous role assignment. Users can only have
        one role at a time.

        Args:
            role_id: The ID of the role.
            user_ids: List of user IDs to assign to this role.
        """
        payload = {
            "data": [
                {"type": "users", "id": user_id}
                for user_id in user_ids
            ]
        }

        self._post(f"/roles/{role_id}/relationships/assigned_users", json=payload)
        logger.info(f"Assigned {len(user_ids)} users to role {role_id}")

    def replace_assigned_users(self, role_id: str, user_ids: List[str]) -> None:
        """
        Replace all users assigned to a role.

        This removes all existing user assignments and replaces them with
        the new set. Pass an empty list to remove all users from the role.

        Args:
            role_id: The ID of the role.
            user_ids: List of user IDs to set as the new assigned users.
        """
        payload = {
            "data": [
                {"type": "users", "id": user_id}
                for user_id in user_ids
            ]
        }

        self._patch(f"/roles/{role_id}/relationships/assigned_users", json=payload)
        logger.info(f"Replaced assigned users of role {role_id} with {len(user_ids)} users")

    def remove_users(self, role_id: str, user_ids: List[str]) -> None:
        """
        Remove users from a role.

        Args:
            role_id: The ID of the role.
            user_ids: List of user IDs to remove from the role.
        """
        payload = {
            "data": [
                {"type": "users", "id": user_id}
                for user_id in user_ids
            ]
        }

        self._delete(f"/roles/{role_id}/relationships/assigned_users", json=payload)
        logger.info(f"Removed {len(user_ids)} users from role {role_id}")
