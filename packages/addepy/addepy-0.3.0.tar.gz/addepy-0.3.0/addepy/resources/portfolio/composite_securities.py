"""Composite Securities resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseResource

logger = logging.getLogger("addepy")


class CompositeSecuritiesResource(BaseResource):
    """
    Resource for Addepar Composite Securities API.

    Composite securities are investments made up of underlying "constituent"
    securities. Common examples include ETFs, mutual funds, and benchmarks.
    Use this API to manage constituent weights for composite securities.

    Note: Addepar currently only supports constituent data for ETFs.

    Methods:
        - get_constituent_weight() - Get a constituent's weight history
        - import_constituents() - Create constituent weights for a date
        - delete_constituents() - Delete all weights for a date
    """

    def get_constituent_weight(
        self,
        composite_id: str,
        constituent_id: str,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get a constituent's weight data from within a composite security.

        Args:
            composite_id: The composite security entity ID.
            constituent_id: The constituent security entity ID.
            start_date: Start date for weight data (YYYY-MM-DD). Optional.
            end_date: End date for weight data (YYYY-MM-DD). Optional.

        Returns:
            Constituent values resource object containing id, type, and
            attributes (values). Values is a list of date-weight pairs.

        Example:
            weight = client.portfolio.composite_securities.get_constituent_weight(
                composite_id="58",
                constituent_id="199",
                start_date="2024-01-01"
            )
            for value in weight["attributes"]["values"]:
                for date, pct in value.items():
                    print(f"{date}: {pct}")
        """
        params: Dict[str, str] = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date

        response = self._get(
            f"/composite_securities/{composite_id}/{constituent_id}",
            params=params if params else None,
        )
        data = response.json()
        result = data.get("data", {})
        logger.debug(
            f"Retrieved constituent weight for {constituent_id} "
            f"in composite {composite_id}"
        )
        return result

    def import_constituents(
        self,
        composite_id: str,
        date: str,
        constituents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Add constituent weight data to a composite security for a specific date.

        Args:
            composite_id: The composite security entity ID.
            date: The date for the constituent weights (YYYY-MM-DD).
            constituents: List of constituent objects with:
                - entityId (int): Constituent security entity ID.
                - percentage (float): Constituent weight (e.g., 0.42 for 42%).

        Returns:
            The created composite security resource object with constituents.

        Example:
            result = client.portfolio.composite_securities.import_constituents(
                composite_id="58",
                date="2024-01-01",
                constituents=[
                    {"entityId": 199, "percentage": 0.42},
                    {"entityId": 200, "percentage": 0.58}
                ]
            )
        """
        payload = {
            "data": {
                "type": "composite_security",
                "id": composite_id,
                "attributes": {
                    "date": date,
                    "constituents": constituents,
                },
            }
        }

        response = self._post("/composite_securities/import", json=payload)
        data = response.json()
        result = data.get("data", {})
        logger.info(
            f"Imported {len(constituents)} constituents for composite {composite_id} "
            f"on {date}"
        )
        return result

    def delete_constituents(self, composite_id: str, date: str) -> None:
        """
        Remove all constituent weight data from a composite security for a date.

        Args:
            composite_id: The composite security entity ID.
            date: The date to remove weights for (YYYY-MM-DD).

        Example:
            client.portfolio.composite_securities.delete_constituents(
                composite_id="58",
                date="2024-01-01"
            )
        """
        self._delete(f"/composite_securities/{composite_id}/{date}")
        logger.info(f"Deleted constituents for composite {composite_id} on {date}")
