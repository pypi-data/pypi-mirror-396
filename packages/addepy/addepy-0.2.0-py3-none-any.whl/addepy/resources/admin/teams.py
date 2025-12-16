"""Teams resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class TeamsResource(BaseResource):
    """
    Resource for Addepar Teams API.

    Teams are sets of users that share access to resources like analysis views,
    dashboards, and section templates.

    Tier 1 (CRUD):
        - get_team() - Get a single team
        - list_teams() - List all teams (paginated)
        - create_team() - Create a new team
        - update_team() - Update a team
        - delete_team() - Delete a team (must have no members)

    Member Methods:
        - get_members() - Get team member user IDs
        - add_members() - Add users to team
        - replace_members() - Replace all team members
        - remove_members() - Remove users from team
    """

    # =========================================================================
    # Tier 1: CRUD Methods
    # =========================================================================

    def get_team(self, team_id: str) -> Dict[str, Any]:
        """
        Get a single team by ID.

        Args:
            team_id: The ID of the team to retrieve.

        Returns:
            The team resource object containing id, type, attributes,
            and relationships.
        """
        response = self._get(f"/teams/{team_id}")
        data = response.json()
        team = data.get("data", {})
        logger.debug(f"Retrieved team {team_id}")
        return team

    def list_teams(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
        ids: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all teams with pagination and optional filters.

        Args:
            page_limit: Results per page (default: 500, max: 2000).
            ids: Filter by specific team IDs (comma-separated).

        Returns:
            List of team resource objects.
        """
        params: Dict[str, Any] = {}

        if ids is not None:
            params["filter[id]"] = ids

        teams = list(
            self._paginate("/teams", page_limit=page_limit, params=params if params else None)
        )
        logger.debug(f"Listed {len(teams)} teams")
        return teams

    def create_team(
        self,
        name: str,
        *,
        member_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new team.

        Args:
            name: The name of the team. Required.
            member_ids: List of user IDs to add as initial members.

        Returns:
            The created team resource object.

        Raises:
            ConflictError: If a team with the same name already exists.
        """
        relationships: Dict[str, Any] = {}

        if member_ids:
            relationships["members"] = {
                "data": [
                    {"type": "users", "id": user_id}
                    for user_id in member_ids
                ]
            }

        payload: Dict[str, Any] = {
            "data": {
                "id": None,
                "type": "teams",
                "attributes": {"name": name},
            }
        }

        if relationships:
            payload["data"]["relationships"] = relationships

        response = self._post("/teams", json=payload)
        data = response.json()
        team = data.get("data", {})
        logger.info(f"Created team: {team.get('id')}")
        return team

    def update_team(
        self,
        team_id: str,
        *,
        name: Optional[str] = None,
        member_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Update a team.

        Args:
            team_id: The ID of the team to update.
            name: New name for the team.
            member_ids: List of user IDs to replace current members.

        Returns:
            The updated team resource object.

        Raises:
            ConflictError: If the new name already exists.
        """
        attributes: Dict[str, Any] = {}
        relationships: Dict[str, Any] = {}

        if name is not None:
            attributes["name"] = name

        if member_ids is not None:
            relationships["members"] = {
                "data": [
                    {"type": "users", "id": user_id}
                    for user_id in member_ids
                ]
            }

        payload: Dict[str, Any] = {
            "data": {
                "id": team_id,
                "type": "teams",
                "attributes": attributes,
            }
        }

        if relationships:
            payload["data"]["relationships"] = relationships

        response = self._patch(f"/teams/{team_id}", json=payload)
        data = response.json()
        team = data.get("data", {})
        logger.info(f"Updated team: {team_id}")
        return team

    def delete_team(self, team_id: str) -> None:
        """
        Delete a team.

        The team must have zero members before it can be deleted.
        Use remove_members() or replace_members([]) first if needed.

        Args:
            team_id: The ID of the team to delete.

        Raises:
            BadRequestError: If the team still has members.
        """
        self._delete(f"/teams/{team_id}")
        logger.info(f"Deleted team: {team_id}")

    # =========================================================================
    # Member Methods
    # =========================================================================

    def get_members(self, team_id: str) -> List[Dict[str, Any]]:
        """
        Get a team's member user IDs.

        Args:
            team_id: The ID of the team.

        Returns:
            List of user relationship objects with 'id' and 'type' keys.
        """
        response = self._get(f"/teams/{team_id}/relationships/members")
        data = response.json()
        members = data.get("data", [])
        logger.debug(f"Retrieved {len(members)} members for team {team_id}")
        return members

    def add_members(self, team_id: str, user_ids: List[str]) -> None:
        """
        Add users to a team.

        Args:
            team_id: The ID of the team.
            user_ids: List of user IDs to add to the team.
        """
        payload = {
            "data": [
                {"type": "users", "id": user_id}
                for user_id in user_ids
            ]
        }

        self._post(f"/teams/{team_id}/relationships/members", json=payload)
        logger.info(f"Added {len(user_ids)} members to team {team_id}")

    def replace_members(self, team_id: str, user_ids: List[str]) -> None:
        """
        Replace all members of a team.

        This removes all existing members and replaces them with the new set.
        Pass an empty list to remove all members.

        Args:
            team_id: The ID of the team.
            user_ids: List of user IDs to set as the new members.
        """
        payload = {
            "data": [
                {"type": "users", "id": user_id}
                for user_id in user_ids
            ]
        }

        self._patch(f"/teams/{team_id}/relationships/members", json=payload)
        logger.info(f"Replaced members of team {team_id} with {len(user_ids)} users")

    def remove_members(self, team_id: str, user_ids: List[str]) -> None:
        """
        Remove users from a team.

        Args:
            team_id: The ID of the team.
            user_ids: List of user IDs to remove from the team.
        """
        payload = {
            "data": [
                {"type": "users", "id": user_id}
                for user_id in user_ids
            ]
        }

        self._delete(f"/teams/{team_id}/relationships/members", json=payload)
        logger.info(f"Removed {len(user_ids)} members from team {team_id}")
