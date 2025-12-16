"""Users resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT, LoginMethod
from ..base import BaseResource

logger = logging.getLogger("addepy")


class UsersResource(BaseResource):
    """
    Resource for Addepar Users API.

    Tier 1 (CRUD):
        - get_user() - Get a single user
        - list_users() - List all users (paginated)
        - get_current_user() - Get the authenticated user
        - create_user() - Create a new user
        - update_user() - Update a user
        - delete_user() - Delete a user

    Query Methods:
        - get_users_by_email() - Find users by email addresses
        - get_users_by_external_id() - Find users by external user IDs

    Relationship Methods:
        - get_user_assigned_role() - Get user's assigned role
        - update_user_role() - Update user's assigned role
        - get_permissioned_entities() - Get user's entity access
        - add_permissioned_entities() - Grant entity access
        - remove_permissioned_entities() - Revoke entity access
        - get_permissioned_groups() - Get user's group access
        - add_permissioned_groups() - Grant group access
        - remove_permissioned_groups() - Revoke group access
    """

    # =========================================================================
    # Tier 1: CRUD Methods
    # =========================================================================

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get a single user by ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The user resource object containing id, type, attributes,
            and relationships.
        """
        response = self._get(f"/users/{user_id}")
        data = response.json()
        user = data.get("data", {})
        logger.debug(f"Retrieved user {user_id}")
        return user

    def list_users(self, *, page_limit: int = DEFAULT_PAGE_LIMIT) -> List[Dict[str, Any]]:
        """
        List all users with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of user resource objects.
        """
        users = list(self._paginate("/users", page_limit=page_limit))
        logger.debug(f"Listed {len(users)} users")
        return users

    def get_current_user(self) -> Dict[str, Any]:
        """
        Get the currently authenticated user.

        This is the user who created the API key used to authenticate the request.

        Returns:
            The current user resource object.
        """
        response = self._get("/users/me")
        data = response.json()
        user = data.get("data", {})
        logger.debug(f"Retrieved current user: {user.get('id')}")
        return user

    def create_user(
        self,
        email: str,
        login_method: LoginMethod = "email_password",
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        saml_user_id: Optional[str] = None,
        admin_access: bool = False,
        all_data_access: bool = False,
        external_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new user.

        By default, users are created in custom mode with no permissions.
        Use update_user_role() or the Roles API to assign permissions based on a role.

        Args:
            email: Email address for authentication.
            login_method: Authentication method. One of: 'email_password', 'saml'.
                Default: 'email_password'.
            first_name: User's first name.
            last_name: User's last name.
            saml_user_id: SAML user ID. Required if login_method is 'saml'.
            admin_access: Grant full permissions. Default: False.
            all_data_access: Grant access to all portfolio data. Default: False.
            external_user_id: Firm's unique identifier for the user.

        Returns:
            The created user resource object.

        Raises:
            ValidationError: If email is invalid or already in use.
            ConflictError: If external_user_id is a duplicate.
        """
        user_attributes: Dict[str, Any] = {
            "email": email,
            "login_method": login_method,
        }

        if first_name is not None:
            user_attributes["first_name"] = first_name
        if last_name is not None:
            user_attributes["last_name"] = last_name
        if saml_user_id is not None:
            user_attributes["saml_user_id"] = saml_user_id
        if admin_access:
            user_attributes["admin_access"] = admin_access
        if all_data_access:
            user_attributes["all_data_access"] = all_data_access
        if external_user_id is not None:
            user_attributes["external_user_id"] = external_user_id

        payload = {
            "data": {
                "type": "users",
                "attributes": user_attributes,
            }
        }

        response = self._post("/users", json=payload)
        data = response.json()
        user = data.get("data", {})
        logger.info(f"Created user: {user.get('id')}")
        return user

    def update_user(
        self,
        user_id: str,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        admin_access: Optional[bool] = None,
        all_data_access: Optional[bool] = None,
        external_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a user.

        Args:
            user_id: The ID of the user to update.
            first_name: User's first name.
            last_name: User's last name.
            admin_access: Grant/revoke full permissions.
            all_data_access: Grant/revoke access to all portfolio data.
            external_user_id: Firm's unique identifier for the user.

        Returns:
            The updated user resource object.

        Note:
            Cannot update: email, login_method, saml_user_id, two_factor_auth_enabled.
            To update relationships, use the relationship methods instead.

        Raises:
            ConflictError: If external_user_id is a duplicate.
        """
        user_attributes: Dict[str, Any] = {}

        if first_name is not None:
            user_attributes["first_name"] = first_name
        if last_name is not None:
            user_attributes["last_name"] = last_name
        if admin_access is not None:
            user_attributes["admin_access"] = admin_access
        if all_data_access is not None:
            user_attributes["all_data_access"] = all_data_access
        if external_user_id is not None:
            user_attributes["external_user_id"] = external_user_id

        payload = {
            "data": {
                "type": "users",
                "id": user_id,
                "attributes": user_attributes,
            }
        }

        response = self._patch(f"/users/{user_id}", json=payload)
        data = response.json()
        user = data.get("data", {})
        logger.info(f"Updated user: {user_id}")
        return user

    def delete_user(self, user_id: str) -> None:
        """
        Delete a user.

        Args:
            user_id: The ID of the user to delete.
        """
        self._delete(f"/users/{user_id}")
        logger.info(f"Deleted user: {user_id}")

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_users_by_email(self, emails: List[str]) -> List[Dict[str, Any]]:
        """
        Get users by email addresses.

        Args:
            emails: List of email addresses to search for.

        Returns:
            List of user resource objects matching the provided emails.
        """
        payload = {
            "data": {
                "type": "email_query",
                "attributes": {
                    "email_ids": emails,
                },
            }
        }

        response = self._post("/users/email_query", json=payload)
        data = response.json()
        users = data.get("data", [])
        logger.debug(f"Found {len(users)} users by email")
        return users

    def get_users_by_external_id(self, external_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get users by external user IDs.

        Args:
            external_ids: List of external user IDs to search for.

        Returns:
            List of user resource objects matching the provided external IDs.
        """
        payload = {
            "data": {
                "type": "external_user_id_query",
                "attributes": {
                    "external_user_ids": external_ids,
                },
            }
        }

        response = self._post("/users/external_user_id_query", json=payload)
        data = response.json()
        users = data.get("data", [])
        logger.debug(f"Found {len(users)} users by external ID")
        return users

    # =========================================================================
    # Relationship Methods
    # =========================================================================

    def get_user_assigned_role(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user's assigned role.

        Args:
            user_id: The ID of the user.

        Returns:
            The role relationship data, or None if no role is assigned.
            Returns dict with 'id' and 'type' keys when a role is assigned.
        """
        response = self._get(f"/users/{user_id}/relationships/assigned_role")
        data = response.json()
        role = data.get("data")
        logger.debug(f"Retrieved assigned role for user {user_id}")
        return role

    def update_user_role(self, user_id: str, role_id: str) -> None:
        """
        Update a user's assigned role.

        Args:
            user_id: The ID of the user.
            role_id: The ID of the role to assign.

        Note:
            Before using this method, you must first assign a role to
            the user in the Addepar application.
        """
        payload = {
            "data": {
                "id": role_id,
                "type": "role",
            }
        }

        self._patch(f"/users/{user_id}/relationships/assigned_role", json=payload)
        logger.info(f"Updated role for user {user_id} to role {role_id}")

    def get_permissioned_entities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get a user's permissioned entities (client portfolios).

        Args:
            user_id: The ID of the user.

        Returns:
            List of entity relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/users/{user_id}/relationships/permissioned_entities")
        data = response.json()
        entities = data.get("data", [])
        logger.debug(f"Retrieved {len(entities)} permissioned entities for user {user_id}")
        return entities

    def add_permissioned_entities(self, user_id: str, entity_ids: List[str]) -> None:
        """
        Grant a user access to entities (client portfolios).

        Args:
            user_id: The ID of the user.
            entity_ids: List of entity IDs to grant access to.
        """
        payload = {
            "data": [
                {"id": entity_id, "type": "entities"}
                for entity_id in entity_ids
            ]
        }

        self._post(f"/users/{user_id}/relationships/permissioned_entities", json=payload)
        logger.info(f"Added {len(entity_ids)} permissioned entities for user {user_id}")

    def remove_permissioned_entities(self, user_id: str, entity_ids: List[str]) -> None:
        """
        Revoke a user's access to entities (client portfolios).

        Args:
            user_id: The ID of the user.
            entity_ids: List of entity IDs to revoke access from.
        """
        payload = {
            "data": [
                {"id": entity_id, "type": "entities"}
                for entity_id in entity_ids
            ]
        }

        self._delete(f"/users/{user_id}/relationships/permissioned_entities", json=payload)
        logger.info(f"Removed {len(entity_ids)} permissioned entities for user {user_id}")

    def get_permissioned_groups(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get a user's permissioned groups.

        Args:
            user_id: The ID of the user.

        Returns:
            List of group relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/users/{user_id}/relationships/permissioned_groups")
        data = response.json()
        groups = data.get("data", [])
        logger.debug(f"Retrieved {len(groups)} permissioned groups for user {user_id}")
        return groups

    def add_permissioned_groups(self, user_id: str, group_ids: List[str]) -> None:
        """
        Grant a user access to groups.

        Args:
            user_id: The ID of the user.
            group_ids: List of group IDs to grant access to.
        """
        payload = {
            "data": [
                {"id": group_id, "type": "groups"}
                for group_id in group_ids
            ]
        }

        self._post(f"/users/{user_id}/relationships/permissioned_groups", json=payload)
        logger.info(f"Added {len(group_ids)} permissioned groups for user {user_id}")

    def remove_permissioned_groups(self, user_id: str, group_ids: List[str]) -> None:
        """
        Revoke a user's access to groups.

        Args:
            user_id: The ID of the user.
            group_ids: List of group IDs to revoke access from.
        """
        payload = {
            "data": [
                {"id": group_id, "type": "groups"}
                for group_id in group_ids
            ]
        }

        self._delete(f"/users/{user_id}/relationships/permissioned_groups", json=payload)
        logger.info(f"Removed {len(group_ids)} permissioned groups for user {user_id}")
