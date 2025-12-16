"""Analysis resource for the Addepar Portfolio API."""
import logging
from typing import Any, Dict, List, Optional, Union

from ...constants import OutputType, PortfolioType
from ..base import BaseResource

logger = logging.getLogger("addepy")

# Valid portfolio types
PORTFOLIO_TYPES = [
    "ENTITY",
    "ENTITY_FUNDS",
    "GROUP",
    "GROUP_FUNDS",
    "FIRM",
    "FIRM_ACCOUNTS",
    "FIRM_CLIENTS",
    "FIRM_HOUSEHOLDS",
    "FIRM_UNVERIFIED_ACCOUNTS",
]

# Valid output types for view results
OUTPUT_TYPES = ["JSON", "CSV", "TSV", "XLSX"]


class AnalysisResource(BaseResource):
    """
    Resource for Addepar Portfolio Analysis APIs.

    Execute portfolio views and dynamic queries to extract portfolio data.

    View Methods:
        - list_views() - List all portfolio views
        - get_view() - Get view definition with query parameters
        - get_view_results() - Execute a saved view and get results

    Query Methods:
        - query() - Execute a dynamic portfolio query

    Note:
        For large-scale queries, use the Jobs API (client.portfolio.jobs)
        for async execution to avoid timeouts.
    """

    # =========================================================================
    # View List Methods
    # =========================================================================

    def list_views(self) -> List[Dict[str, Any]]:
        """
        List all portfolio views accessible to the user.

        Returns:
            List of view resource objects containing id, type, and attributes
            (share_type, display_name).

        Example:
            views = client.portfolio.analysis.list_views()
            for view in views:
                print(f"{view['id']}: {view['attributes']['display_name']}")
        """
        response = self._get("/portfolio/views")
        data = response.json()
        views = data.get("data", [])
        logger.debug(f"Listed {len(views)} portfolio views")
        return views

    def get_view(self, view_id: str) -> Dict[str, Any]:
        """
        Get a portfolio view definition by ID.

        Args:
            view_id: The ID of the view.

        Returns:
            View resource object containing id, type, and attributes
            (share_type, display_name, parameters). The parameters include
            columns, groupings, filters, and other query settings.

        Example:
            view = client.portfolio.analysis.get_view(view_id="19")
            params = view["attributes"]["parameters"]
            print(f"Columns: {params['columns']}")
            print(f"Groupings: {params['groupings']}")
        """
        response = self._get(f"/portfolio/views/{view_id}")
        data = response.json()
        view = data.get("data", {})
        logger.debug(f"Retrieved view {view_id}")
        return view

    # =========================================================================
    # View Results Methods
    # =========================================================================

    def get_view_results(
        self,
        view_id: str,
        portfolio_id: int,
        portfolio_type: PortfolioType,
        start_date: str,
        end_date: str,
        output_type: OutputType = "JSON",
    ) -> Union[Dict[str, Any], bytes]:
        """
        Execute a saved portfolio view and get results.

        Args:
            view_id: The ID of the view to execute.
            portfolio_id: The ID of the portfolio (entity or group).
                If portfolio_type is FIRM, must be 1.
            portfolio_type: Type of portfolio. One of:
                ENTITY, ENTITY_FUNDS, GROUP, GROUP_FUNDS, FIRM,
                FIRM_ACCOUNTS, FIRM_CLIENTS, FIRM_HOUSEHOLDS,
                FIRM_UNVERIFIED_ACCOUNTS.
            start_date: Start date of the time period (YYYY-MM-DD).
            end_date: End date of the time period (YYYY-MM-DD).
            output_type: Output format. One of: JSON, CSV, TSV, XLSX.
                Default is JSON.

        Returns:
            For JSON: Dict containing meta (columns, groupings) and data
            (total with nested children by grouping level).
            For CSV/TSV/XLSX: Raw bytes of the file content.

        Note:
            - JSON does not support Advanced or Pivot tables
            - CSV/TSV do not support Advanced/Pivot tables or benchmarks
              at the grouping level
            - XLSX supports all table types

        Example:
            # JSON output
            results = client.portfolio.analysis.get_view_results(
                view_id="19",
                portfolio_id=10,
                portfolio_type="ENTITY",
                start_date="2024-01-01",
                end_date="2024-03-31",
                output_type="JSON"
            )
            total = results["data"]["attributes"]["total"]
            print(f"Total: {total['columns']}")

            # CSV output
            csv_data = client.portfolio.analysis.get_view_results(
                view_id="19",
                portfolio_id=10,
                portfolio_type="ENTITY",
                start_date="2024-01-01",
                end_date="2024-03-31",
                output_type="CSV"
            )
            with open("portfolio.csv", "wb") as f:
                f.write(csv_data)
        """
        params = {
            "portfolio_id": portfolio_id,
            "portfolio_type": portfolio_type.upper(),
            "output_type": output_type.upper(),
            "start_date": start_date,
            "end_date": end_date,
        }

        response = self._get(f"/portfolio/views/{view_id}/results", params=params)

        if output_type.upper() == "JSON":
            result = response.json()
            logger.debug(f"Executed view {view_id} for portfolio {portfolio_id}")
            return result
        else:
            logger.debug(
                f"Executed view {view_id} for portfolio {portfolio_id} "
                f"(output: {output_type.upper()})"
            )
            return response.content

    # =========================================================================
    # Query Methods
    # =========================================================================

    def query(
        self,
        columns: List[Dict[str, Any]],
        groupings: List[Union[str, Dict[str, Any]]],
        portfolio_type: PortfolioType,
        portfolio_id: Union[int, List[int]],
        start_date: str,
        end_date: str,
        *,
        filters: Optional[List[Dict[str, Any]]] = None,
        hide_previous_holdings: Optional[bool] = None,
        group_by_historical_values: Optional[bool] = None,
        group_by_multiple_attribute_values: Optional[bool] = None,
        look_through_composite_securities: Optional[bool] = None,
        look_through_constituent_holdings: Optional[Dict[str, Any]] = None,
        display_account_fees: Optional[bool] = None,
        external_ids: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a dynamic portfolio query.

        Args:
            columns: List of column attributes with optional arguments.
                Each column is a dict with 'key' and optional 'arguments'.
            groupings: List of grouping attributes. Can be strings (attribute
                keys) or dicts with 'key' and optional 'arguments'.
            portfolio_type: Type of portfolio. One of:
                ENTITY, ENTITY_FUNDS, GROUP, GROUP_FUNDS, FIRM,
                FIRM_ACCOUNTS, FIRM_CLIENTS, FIRM_HOUSEHOLDS,
                FIRM_UNVERIFIED_ACCOUNTS.
            portfolio_id: Portfolio ID or list of IDs. If portfolio_type
                is FIRM, must be 1.
            start_date: Start date of the time period (YYYY-MM-DD).
            end_date: End date of the time period (YYYY-MM-DD).
            filters: Optional list of filter objects. Each filter has:
                - attribute: Attribute key to filter on
                - type: 'discrete' or 'number'
                - operator: 'include'/'exclude' (discrete) or 'range'/'rank' (number)
                - values: List of values (for discrete)
                - ranges: List of {from, to} pairs (for number range)
                - rank_order/rank_value: For number rank filters
            hide_previous_holdings: Exclude holdings not held at period end.
            group_by_historical_values: Include previous values for
                time-varying attributes.
            group_by_multiple_attribute_values: Breakout by each value
                in multi-value attributes.
            look_through_composite_securities: Look through fund components.
            look_through_constituent_holdings: Configure constituent lookthrough.
                Dict with 'type' ('none', 'top', 'all', 'weighted') and
                optional 'threshold'.
            display_account_fees: Show account fees.
            external_ids: Use external IDs instead of portfolio_id. List of
                dicts with 'external_type_key' and 'external_id'.

        Returns:
            Dict containing meta (columns, groupings) and data (total with
            nested children by grouping level).

        Example:
            results = client.portfolio.analysis.query(
                columns=[
                    {"key": "value"},
                    {"key": "time_weighted_return", "arguments": {"period": "trailing P1Y"}}
                ],
                groupings=[
                    {"key": "asset_class"},
                    {"key": "security"}
                ],
                portfolio_type="ENTITY",
                portfolio_id=[329263, 259910],
                start_date="2024-01-01",
                end_date="2024-03-31",
                filters=[
                    {
                        "attribute": "asset_class",
                        "type": "discrete",
                        "operator": "include",
                        "values": ["Equity", "Fixed Income"]
                    }
                ],
                hide_previous_holdings=True
            )

            # Access results
            total = results["data"]["attributes"]["total"]
            print(f"Total: {total['columns']}")
            for child in total["children"]:
                print(f"  {child['name']}: {child['columns']}")
        """
        attributes: Dict[str, Any] = {
            "columns": columns,
            "groupings": groupings,
            "portfolio_type": portfolio_type.upper(),
            "portfolio_id": portfolio_id,
            "start_date": start_date,
            "end_date": end_date,
        }

        # Add optional parameters
        if filters is not None:
            attributes["filters"] = filters
        if hide_previous_holdings is not None:
            attributes["hide_previous_holdings"] = hide_previous_holdings
        if group_by_historical_values is not None:
            attributes["group_by_historical_values"] = group_by_historical_values
        if group_by_multiple_attribute_values is not None:
            attributes["group_by_multiple_attribute_values"] = (
                group_by_multiple_attribute_values
            )
        if look_through_composite_securities is not None:
            attributes["look_through_composite_securities"] = (
                look_through_composite_securities
            )
        if look_through_constituent_holdings is not None:
            attributes["look_through_constituent_holdings"] = (
                look_through_constituent_holdings
            )
        if display_account_fees is not None:
            attributes["display_account_fees"] = display_account_fees
        if external_ids is not None:
            attributes["external_ids"] = external_ids

        payload = {
            "data": {
                "type": "portfolio_query",
                "attributes": attributes,
            }
        }

        response = self._post("/portfolio/query", json=payload)
        result = response.json()

        # Log with portfolio count info
        if isinstance(portfolio_id, list):
            logger.debug(f"Executed portfolio query for {len(portfolio_id)} portfolios")
        else:
            logger.debug(f"Executed portfolio query for portfolio {portfolio_id}")

        return result
