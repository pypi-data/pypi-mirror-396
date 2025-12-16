"""Billable Portfolios resource for the Addepar API."""
import logging
from typing import Optional

from ..base import BaseResource

logger = logging.getLogger("addepy")


class BillablePortfoliosResource(BaseResource):
    """
    Resource for Addepar Billable Portfolios API.

    A billable portfolio is a portfolio (entity or group) associated with
    a fee schedule for billing purposes.

    Methods:
        - create_billable_portfolio() - Add a portfolio for billing
        - update_fee_schedule() - Update fee schedule or restore archived portfolio
        - archive_billable_portfolio() - Archive a billable portfolio
    """

    def create_billable_portfolio(
        self,
        schedule_id: str,
        *,
        entity_id: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> str:
        """
        Add a portfolio for billing with a specified fee schedule.

        You must provide either entity_id OR group_id, but not both.

        Args:
            schedule_id: The ID of the fee schedule to associate.
            entity_id: The ID of the entity to set up for billing.
                Use this OR group_id, not both.
            group_id: The ID of the group to set up for billing.
                Use this OR entity_id, not both.

        Returns:
            The ID of the created billable portfolio.

        Raises:
            ValueError: If both entity_id and group_id are provided,
                or if neither is provided.
        """
        if entity_id and group_id:
            raise ValueError("Provide either entity_id or group_id, not both")
        if not entity_id and not group_id:
            raise ValueError("Must provide either entity_id or group_id")

        attributes = {"schedule_id": schedule_id}
        if entity_id:
            attributes["entity_id"] = entity_id
        if group_id:
            attributes["group_id"] = group_id

        payload = {
            "data": {
                "type": "create_billable_portfolio",
                "attributes": attributes,
            }
        }

        response = self._post("/billable_portfolios", json=payload)
        data = response.json()
        billable_portfolio_id = str(data.get("id", ""))
        logger.info(f"Created billable portfolio: {billable_portfolio_id}")
        return billable_portfolio_id

    def update_fee_schedule(
        self,
        billable_portfolio_id: str,
        fee_schedule_id: str,
    ) -> None:
        """
        Update a billable portfolio's fee schedule.

        This can also be used to restore an archived billable portfolio
        by assigning it a new fee schedule.

        Args:
            billable_portfolio_id: The ID of the billable portfolio.
            fee_schedule_id: The ID of the fee schedule to assign.
        """
        payload = {
            "data": {
                "id": fee_schedule_id,
                "type": "fee_schedules",
            }
        }

        self._patch(
            f"/billable_portfolios/{billable_portfolio_id}/relationships/fee_schedules",
            json=payload,
        )
        logger.info(
            f"Updated fee schedule for billable portfolio {billable_portfolio_id} "
            f"to {fee_schedule_id}"
        )

    def archive_billable_portfolio(self, billable_portfolio_id: str) -> None:
        """
        Archive a billable portfolio.

        Archived portfolios will no longer be billed. Previous bills
        are not affected.

        Args:
            billable_portfolio_id: The ID of the billable portfolio to archive.

        Raises:
            ConflictError: If the billable portfolio is already archived.
        """
        self._delete(
            f"/billable_portfolios/{billable_portfolio_id}/relationships/fee_schedules"
        )
        logger.info(f"Archived billable portfolio: {billable_portfolio_id}")
