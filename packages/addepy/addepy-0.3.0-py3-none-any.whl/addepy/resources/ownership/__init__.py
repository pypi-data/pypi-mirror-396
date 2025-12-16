"""Ownership namespace containing ownership-related resources."""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...client import AddeparClient
    from .entities import EntitiesResource
    from .external_ids import ExternalIdsResource
    from .groups import GroupsResource
    from .positions import PositionsResource


class OwnershipNamespace:
    """
    Namespace for ownership-related API resources.

    Resources:
        - entities: Manage entities and query entity types
        - external_ids: Manage external ID types
        - groups: Manage groups and query group types
        - positions: Manage positions and ownership relationships
    """

    def __init__(self, client: "AddeparClient") -> None:
        self._client = client
        self._entities: Optional["EntitiesResource"] = None
        self._external_ids: Optional["ExternalIdsResource"] = None
        self._groups: Optional["GroupsResource"] = None
        self._positions: Optional["PositionsResource"] = None

    @property
    def entities(self) -> "EntitiesResource":
        """Access the Entities resource."""
        if self._entities is None:
            from .entities import EntitiesResource

            self._entities = EntitiesResource(self._client)
        return self._entities

    @property
    def external_ids(self) -> "ExternalIdsResource":
        """Access the External IDs resource."""
        if self._external_ids is None:
            from .external_ids import ExternalIdsResource

            self._external_ids = ExternalIdsResource(self._client)
        return self._external_ids

    @property
    def groups(self) -> "GroupsResource":
        """Access the Groups resource."""
        if self._groups is None:
            from .groups import GroupsResource

            self._groups = GroupsResource(self._client)
        return self._groups

    @property
    def positions(self) -> "PositionsResource":
        """Access the Positions resource."""
        if self._positions is None:
            from .positions import PositionsResource

            self._positions = PositionsResource(self._client)
        return self._positions


__all__ = [
    "OwnershipNamespace",
    "EntitiesResource",
    "ExternalIdsResource",
    "GroupsResource",
    "PositionsResource",
]
