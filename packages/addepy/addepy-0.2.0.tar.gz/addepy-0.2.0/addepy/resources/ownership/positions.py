"""Positions resource for the Addepar API."""

import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class PositionsResource(BaseResource):
    """
    Resource for Addepar Positions API.

    Positions connect two entities in the ownership graph and represent
    ownership relationships. Multiple positions can exist between the same
    owner/owned entities, but this API only reads/writes incepting open positions.

    Tier 1 (CRUD):
        - get_position() - Get a single position
        - list_positions() - List all positions (paginated, with filters)
        - create_position() - Create a new position
        - create_positions() - Create multiple positions
        - update_position() - Update a position
        - update_positions() - Update multiple positions
        - delete_position() - Delete a position
        - delete_positions() - Delete multiple positions

    Relationship Methods:
        - get_position_owner() - Get owner entity details
        - get_position_owned() - Get owned entity details
        - get_position_owner_relationship() - Get owner relationship
        - get_position_owned_relationship() - Get owned relationship
    """

    # =========================================================================
    # Tier 1: CRUD Methods
    # =========================================================================

    def get_position(self, position_id: str) -> Dict[str, Any]:
        """
        Get a single position by ID.

        Args:
            position_id: The ID of the position to retrieve.

        Returns:
            The position resource object containing id, type, attributes,
            and relationships (owner and owned).

        Example:
            position = client.ownership.positions.get_position("12345")
            print(position["attributes"]["incepting_open_position_date"])
            owner_id = position["relationships"]["owner"]["data"]["id"]
        """
        response = self._get(f"/positions/{position_id}")
        data = response.json()
        position = data.get("data", {})
        logger.debug(f"Retrieved position {position_id}")
        return position

    def list_positions(
        self,
        *,
        fields: Optional[List[str]] = None,
        created_before: Optional[str] = None,
        created_after: Optional[str] = None,
        modified_before: Optional[str] = None,
        modified_after: Optional[str] = None,
        owner_model_types: Optional[List[str]] = None,
        owned_model_types: Optional[List[str]] = None,
        owner_entity_id: Optional[List[str]] = None,
        owned_entity_id: Optional[List[str]] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all positions with optional filtering and pagination.

        Args:
            fields: Specific attributes to return (e.g., ["name", "incepting_open_position_date"]).
                Use empty list [] to omit all attributes.
            created_before: Filter positions created on/before date (YYYY-MM-DD).
            created_after: Filter positions created on/after date (YYYY-MM-DD).
            modified_before: Filter positions modified on/before date (YYYY-MM-DD).
            modified_after: Filter positions modified on/after date (YYYY-MM-DD).
            owner_model_types: Filter by owner entity model types (e.g., ["PERSON_NODE", "TRUST"]).
            owned_model_types: Filter by owned entity model types (e.g., ["STOCK", "BOND"]).
            owner_entity_id: Filter by specific owner entity IDs.
            owned_entity_id: Filter by specific owned entity IDs.
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of position resource objects.

        Example:
            # Get all positions owned by specific entities
            positions = client.ownership.positions.list_positions(
                owner_entity_id=["123", "456"],
                created_after="2024-01-01"
            )

            # Get minimal position data
            positions = client.ownership.positions.list_positions(
                fields=["incepting_open_position_date"],
                owner_model_types=["TRUST"]
            )
        """
        params: Dict[str, Any] = {}

        if fields is not None:
            params["fields[positions]"] = ",".join(fields) if fields else "[]"
        if created_before:
            params["filter[created_before]"] = created_before
        if created_after:
            params["filter[created_after]"] = created_after
        if modified_before:
            params["filter[modified_before]"] = modified_before
        if modified_after:
            params["filter[modified_after]"] = modified_after
        if owner_model_types:
            params["filter[owner_model_types]"] = ",".join(owner_model_types)
        if owned_model_types:
            params["filter[owned_model_types]"] = ",".join(owned_model_types)
        if owner_entity_id:
            params["filter[owner_entity_id]"] = ",".join(owner_entity_id)
        if owned_entity_id:
            params["filter[owned_entity_id]"] = ",".join(owned_entity_id)

        positions = list(self._paginate("/positions", params=params, page_limit=page_limit))
        logger.debug(f"Listed {len(positions)} positions")
        return positions

    def create_position(
        self,
        owner_id: str,
        owned_id: str,
        *,
        name: Optional[str] = None,
        incepting_open_position_date: Optional[str] = None,
        incepting_open_position_ownership_percentage: Optional[float] = None,
        **attributes: Any,
    ) -> Dict[str, Any]:
        """
        Create a single position.

        Args:
            owner_id: The entity ID that holds the position.
            owned_id: The entity ID being held in the position.
            name: Position name. Required for cash positions. Names must be
                unique for cash positions with the same owner and owned entities.
            incepting_open_position_date: Date ownership was first linked (YYYY-MM-DD).
                Required for percent-based assets. For share-based assets that
                directly own positions (like accounts), use one day before the
                first transaction/snapshot date.
            incepting_open_position_ownership_percentage: Percentage ownership
                as a decimal (e.g., 0.5 for 50%). Required for percent-based assets.
            **attributes: Additional attributes for the position (custom and standard).

        Returns:
            The created position resource object containing id, type, attributes,
            and relationships.

        Raises:
            BadRequestError: If required attributes are missing for the ownership type.
            NotFoundError: If owner_id or owned_id don't exist.

        Examples:
            # Create position for share-based asset (stock in account)
            position = client.ownership.positions.create_position(
                owner_id="27",  # Account
                owned_id="29"   # Stock
            )

            # Create position for percent-based asset (person owns trust)
            position = client.ownership.positions.create_position(
                owner_id="22",  # Person
                owned_id="23",  # Trust
                incepting_open_position_date="2001-01-01",
                incepting_open_position_ownership_percentage=1.0
            )

            # Create cash position
            position = client.ownership.positions.create_position(
                owner_id="100",
                owned_id="101",
                name="USD Cash",
                incepting_open_position_date="2020-01-01",
                incepting_open_position_ownership_percentage=1.0
            )
        """
        position_attributes: Dict[str, Any] = {}

        if name is not None:
            position_attributes["name"] = name
        if incepting_open_position_date is not None:
            position_attributes["incepting_open_position_date"] = incepting_open_position_date
        if incepting_open_position_ownership_percentage is not None:
            position_attributes["incepting_open_position_ownership_percentage"] = (
                incepting_open_position_ownership_percentage
            )

        # Add any additional custom/standard attributes
        position_attributes.update(attributes)

        payload = {
            "data": {
                "type": "positions",
                "attributes": position_attributes,
                "relationships": {
                    "owner": {
                        "data": {
                            "type": "entities",
                            "id": owner_id,
                        }
                    },
                    "owned": {
                        "data": {
                            "type": "entities",
                            "id": owned_id,
                        }
                    },
                },
            }
        }

        response = self._post("/positions", json=payload)
        data = response.json()
        position = data.get("data", {})
        logger.info(f"Created position: {position.get('id')}")
        return position

    def create_positions(
        self,
        positions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Create multiple positions at once.

        Args:
            positions: List of position definitions. Each should have:
                - owner_id (str): The entity ID that holds the position. Required.
                - owned_id (str): The entity ID being held. Required.
                - name (str, optional): Position name. Required for cash positions.
                - incepting_open_position_date (str, optional): Date in YYYY-MM-DD.
                  Required for percent-based assets.
                - incepting_open_position_ownership_percentage (float, optional):
                  Decimal percentage. Required for percent-based assets.
                - attributes (Dict, optional): Additional custom/standard attributes.

        Returns:
            List of created position resource objects.

        Example:
            positions = [
                {
                    "owner_id": "1",
                    "owned_id": "2",
                    "incepting_open_position_date": "2012-12-01",
                    "incepting_open_position_ownership_percentage": 1.0
                },
                {
                    "owner_id": "3",
                    "owned_id": "4",
                    "incepting_open_position_date": "2012-01-01",
                    "incepting_open_position_ownership_percentage": 0.5
                }
            ]
            created = client.ownership.positions.create_positions(positions)
        """
        data_items = []

        for position in positions:
            position_attributes: Dict[str, Any] = {}

            # Extract known attributes
            if "name" in position:
                position_attributes["name"] = position["name"]
            if "incepting_open_position_date" in position:
                position_attributes["incepting_open_position_date"] = (
                    position["incepting_open_position_date"]
                )
            if "incepting_open_position_ownership_percentage" in position:
                position_attributes["incepting_open_position_ownership_percentage"] = (
                    position["incepting_open_position_ownership_percentage"]
                )

            # Add any additional attributes
            if "attributes" in position:
                position_attributes.update(position["attributes"])

            data_items.append(
                {
                    "type": "positions",
                    "attributes": position_attributes,
                    "relationships": {
                        "owner": {
                            "data": {
                                "type": "entities",
                                "id": position["owner_id"],
                            }
                        },
                        "owned": {
                            "data": {
                                "type": "entities",
                                "id": position["owned_id"],
                            }
                        },
                    },
                }
            )

        payload = {"data": data_items}

        response = self._post("/positions", json=payload)
        data = response.json()
        created_positions = data.get("data", [])
        logger.info(f"Created {len(created_positions)} positions")
        return created_positions

    def update_position(
        self,
        position_id: str,
        **attributes: Any,
    ) -> Dict[str, Any]:
        """
        Update a single position.

        Note: This updates the incepting open position only.

        Args:
            position_id: The ID of the position to update.
            **attributes: Attributes to update (e.g., name="New Name",
                incepting_open_position_ownership_percentage=0.2).

        Returns:
            The updated position resource object.

        Examples:
            # Update ownership percentage for percent-based asset
            position = client.ownership.positions.update_position(
                "104",
                incepting_open_position_date="2010-01-01",
                incepting_open_position_ownership_percentage=0.2
            )

            # Update custom attribute
            position = client.ownership.positions.update_position(
                "998",
                display_name="My Cash Asset",
                _custom_balance_sheet_12345=[{"value": "Below The Line"}]
            )
        """
        payload = {
            "data": {
                "id": position_id,
                "type": "positions",
                "attributes": attributes,
            }
        }

        response = self._patch(f"/positions/{position_id}", json=payload)
        data = response.json()
        position = data.get("data", {})
        logger.info(f"Updated position: {position_id}")
        return position

    def update_positions(
        self,
        positions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Update multiple positions at once.

        Note: This updates the incepting open positions only.

        Args:
            positions: List of position updates. Each must have:
                - id (str): Position ID. Required.
                - Plus any attributes to update.

        Returns:
            List of updated position resource objects.

        Example:
            updates = [
                {
                    "id": "13",
                    "name": "Bob",
                    "incepting_open_position_date": "2016-12-01",
                    "incepting_open_position_value": 5
                },
                {
                    "id": "14",
                    "incepting_open_position_ownership_percentage": 0.75
                }
            ]
            updated = client.ownership.positions.update_positions(updates)
        """
        payload = {
            "data": [
                {
                    "id": position["id"],
                    "type": "positions",
                    "attributes": {k: v for k, v in position.items() if k != "id"},
                }
                for position in positions
            ]
        }

        response = self._patch("/positions", json=payload)
        data = response.json()
        updated_positions = data.get("data", [])
        logger.info(f"Updated {len(updated_positions)} positions")
        return updated_positions

    def delete_position(self, position_id: str) -> None:
        """
        Delete a single position.

        Args:
            position_id: The ID of the position to delete.

        Raises:
            BadRequestError: If position is referenced in transactions.
            NotFoundError: If position doesn't exist.

        Note:
            Cannot delete a position if it is being referenced in transactions.
        """
        self._delete(f"/positions/{position_id}")
        logger.info(f"Deleted position: {position_id}")

    def delete_positions(self, position_ids: List[str]) -> None:
        """
        Delete multiple positions at once.

        Args:
            position_ids: List of position IDs to delete.

        Raises:
            BadRequestError: If any position is referenced in transactions.

        Note:
            Cannot delete positions that are being referenced in transactions.
        """
        payload = {
            "data": [
                {"id": position_id, "type": "positions"}
                for position_id in position_ids
            ]
        }

        self._delete("/positions", json=payload)
        logger.info(f"Deleted {len(position_ids)} positions")

    # =========================================================================
    # Relationship Methods
    # =========================================================================

    def get_position_owner(self, position_id: str) -> Dict[str, Any]:
        """
        Get the owner entity details for a position.

        Args:
            position_id: The ID of the position.

        Returns:
            The owner entity resource object with full attributes.

        Example:
            owner = client.ownership.positions.get_position_owner("9")
            print(owner["attributes"]["original_name"])
            print(owner["attributes"]["model_type"])
        """
        response = self._get(f"/positions/{position_id}/owner")
        data = response.json()
        owner = data.get("data", {})
        logger.debug(f"Retrieved owner entity for position {position_id}")
        return owner

    def get_position_owned(self, position_id: str) -> Dict[str, Any]:
        """
        Get the owned entity details for a position.

        Args:
            position_id: The ID of the position.

        Returns:
            The owned entity resource object with full attributes.

        Example:
            owned = client.ownership.positions.get_position_owned("9")
            print(owned["attributes"]["original_name"])
            print(owned["attributes"]["ownership_type"])
        """
        response = self._get(f"/positions/{position_id}/owned")
        data = response.json()
        owned = data.get("data", {})
        logger.debug(f"Retrieved owned entity for position {position_id}")
        return owned

    def get_position_owner_relationship(self, position_id: str) -> Dict[str, Any]:
        """
        Get the owner relationship for a position.

        Returns just the relationship identifier (id and type), not full entity details.

        Args:
            position_id: The ID of the position.

        Returns:
            Relationship object with 'id' and 'type' fields.

        Example:
            relationship = client.ownership.positions.get_position_owner_relationship("9")
            owner_id = relationship["id"]  # Returns: "192"
            owner_type = relationship["type"]  # Returns: "entities"
        """
        response = self._get(f"/positions/{position_id}/relationships/owner")
        data = response.json()
        relationship = data.get("data", {})
        logger.debug(f"Retrieved owner relationship for position {position_id}")
        return relationship

    def get_position_owned_relationship(self, position_id: str) -> Dict[str, Any]:
        """
        Get the owned relationship for a position.

        Returns just the relationship identifier (id and type), not full entity details.

        Args:
            position_id: The ID of the position.

        Returns:
            Relationship object with 'id' and 'type' fields.

        Example:
            relationship = client.ownership.positions.get_position_owned_relationship("9")
            owned_id = relationship["id"]  # Returns: "23"
            owned_type = relationship["type"]  # Returns: "entities"
        """
        response = self._get(f"/positions/{position_id}/relationships/owned")
        data = response.json()
        relationship = data.get("data", {})
        logger.debug(f"Retrieved owned relationship for position {position_id}")
        return relationship
