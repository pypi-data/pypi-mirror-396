"""Historical Prices resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseResource

logger = logging.getLogger("addepy")


class HistoricalPricesResource(BaseResource):
    """
    Resource for Addepar Historical Prices API.

    Historical prices represent the price of a share-based investment on a
    specific date. They're typically created for assets held before using
    Addepar.

    Note: POST and DELETE operations are asynchronous and return job IDs.

    Methods:
        - get_prices() - Get historical prices for an entity
        - create_prices() - Create or update prices (async)
        - delete_price() - Delete a price for a date (async)
    """

    def get_prices(
        self,
        entity_id: str,
        *,
        date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get historical prices for an entity.

        Args:
            entity_id: The entity ID.
            date: Optional date to retrieve price for (YYYY-MM-DD).
                If omitted, all prices are returned.

        Returns:
            List of historical price resource objects containing id, type,
            and attributes (date, source, value, nodeId).

        Example:
            # Get all prices
            prices = client.portfolio.historical_prices.get_prices(entity_id="60")

            # Get price for specific date
            prices = client.portfolio.historical_prices.get_prices(
                entity_id="60",
                date="2024-01-01"
            )
        """
        params: Dict[str, str] = {}
        if date is not None:
            params["date"] = date

        response = self._get(
            f"/entities/{entity_id}/prices",
            params=params if params else None,
        )
        data = response.json()
        results = data.get("data", [])
        logger.debug(f"Retrieved {len(results)} prices for entity {entity_id}")
        return results

    def create_prices(
        self,
        entity_id: str,
        prices: List[Dict[str, Any]],
    ) -> int:
        """
        Create or update historical prices for an entity.

        This operation is asynchronous and returns a job ID.

        Args:
            entity_id: The entity ID.
            prices: List of price dicts, each containing:
                - date (str): The date (YYYY-MM-DD)
                - nodeId (int): The entity ID (should match entity_id)
                - value (float): The price value

        Returns:
            The async job ID (async_price_save_id).

        Example:
            job_id = client.portfolio.historical_prices.create_prices(
                entity_id="60",
                prices=[
                    {"date": "2024-01-01", "nodeId": 60, "value": 100.0},
                    {"date": "2024-01-02", "nodeId": 60, "value": 101.5}
                ]
            )
            print(f"Price save job ID: {job_id}")
        """
        payload = {
            "data": [
                {
                    "type": "historical_prices",
                    "attributes": price,
                }
                for price in prices
            ]
        }

        response = self._post(f"/entities/{entity_id}/prices", json=payload)
        data = response.json()
        job_id = data.get("async_price_save_id")
        logger.info(
            f"Submitted price creation job {job_id} for entity {entity_id} "
            f"({len(prices)} prices)"
        )
        return job_id

    def delete_price(self, entity_id: str, date: str) -> int:
        """
        Delete a historical price for a specific date.

        This operation is asynchronous and returns a job ID.

        Args:
            entity_id: The entity ID.
            date: The date of the price to delete (YYYY-MM-DD).

        Returns:
            The async job ID (async_price_delete_id).

        Example:
            job_id = client.portfolio.historical_prices.delete_price(
                entity_id="60",
                date="2024-01-01"
            )
            print(f"Price delete job ID: {job_id}")
        """
        response = self._delete(f"/entities/{entity_id}/prices/{date}")
        data = response.json()
        job_id = data.get("async_price_delete_id")
        logger.info(
            f"Submitted price deletion job {job_id} for entity {entity_id} on {date}"
        )
        return job_id
