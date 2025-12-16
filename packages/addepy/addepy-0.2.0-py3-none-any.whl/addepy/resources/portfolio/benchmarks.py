"""Benchmarks resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")

# Valid benchmark types
BENCHMARK_TYPES = {
    "blended",
    "imported",
    "fixed_return",
    "portfolio_benchmark",
    "security_benchmark",
}

# Valid rebalance intervals for blended benchmarks
REBALANCE_INTERVALS = {
    "None",
    "ONE_DAY",
    "ONE_WEEK",
    "ONE_MONTH",
    "THREE_MONTHS",
    "SIX_MONTHS",
    "ONE_YEAR",
}

# Valid matching types for benchmark association strategies
MATCHING_TYPES = {"PATH", "PDN"}


class BenchmarksResource(BaseResource):
    """
    Resource for Addepar Benchmarks APIs.

    Manage benchmarks in Addepar, including creating, updating, and deleting
    benchmarks, managing compositions for blended benchmarks, importing
    benchmark data, and configuring benchmark association strategies.

    Benchmarks Methods:
        - get_benchmark() - Get a single benchmark
        - list_benchmarks() - List all benchmarks
        - create_benchmark() - Create a benchmark
        - update_benchmark() - Update a single benchmark
        - update_benchmarks() - Update multiple benchmarks
        - delete_benchmark() - Delete a benchmark

    Benchmark Compositions Methods:
        - get_benchmark_composition() - Get composition for a blended benchmark
        - list_benchmark_compositions() - List all compositions
        - update_benchmark_composition() - Update composition intervals

    Imported Benchmark Data Methods:
        - get_imported_benchmark_data() - Get daily returns
        - update_imported_benchmark_data() - Add/update daily returns

    Benchmark Associations Strategies Methods:
        - get_benchmark_association_strategy() - Get a single strategy
        - list_benchmark_association_strategies() - List all strategies
        - create_benchmark_association_strategy() - Create a strategy
        - update_benchmark_association_strategy() - Update a strategy
        - delete_benchmark_association_strategy() - Delete a strategy
    """

    # =========================================================================
    # Benchmarks CRUD Methods
    # =========================================================================

    def get_benchmark(self, benchmark_id: str) -> Dict[str, Any]:
        """
        Get a single benchmark by ID.

        Args:
            benchmark_id: The ID of the benchmark to retrieve.

        Returns:
            The benchmark resource object containing id, type, and attributes
            (benchmark_type, name, and type-specific fields).
        """
        response = self._get(f"/benchmarks/{benchmark_id}")
        data = response.json()
        benchmark = data.get("data", {})
        logger.debug(f"Retrieved benchmark {benchmark_id}")
        return benchmark

    def list_benchmarks(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all active benchmarks with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of benchmark resource objects.
        """
        benchmarks = list(self._paginate("/benchmarks", page_limit=page_limit))
        logger.debug(f"Listed {len(benchmarks)} benchmarks")
        return benchmarks

    def create_benchmark(
        self,
        benchmark_type: str,
        *,
        name: Optional[str] = None,
        blended: Optional[Dict[str, Any]] = None,
        fixed_return: Optional[Dict[str, Any]] = None,
        portfolio: Optional[Dict[str, Any]] = None,
        security: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new benchmark.

        Note: Index benchmarks cannot be created via API (vendor-provided).

        Args:
            benchmark_type: Type of benchmark - "blended", "imported",
                "fixed_return", "portfolio_benchmark", or "security_benchmark".
            name: Display name for the benchmark (not required for fixed_return).
            blended: For blended benchmarks - dict with "rebalance_interval"
                (e.g., {"rebalance_interval": "THREE_MONTHS"}).
            fixed_return: For fixed return benchmarks - dict with "fixed_return"
                (decimal) and "is_compounded" (bool).
            portfolio: For portfolio benchmarks - dict with "entity_id".
            security: For security benchmarks - dict with "entity_id".

        Returns:
            The created benchmark resource object.

        Raises:
            ValueError: If benchmark_type is invalid.

        Example:
            # Create a blended benchmark
            benchmark = client.portfolio.benchmarks.create_benchmark(
                benchmark_type="blended",
                name="60/40 Portfolio",
                blended={"rebalance_interval": "THREE_MONTHS"}
            )

            # Create a fixed return benchmark
            benchmark = client.portfolio.benchmarks.create_benchmark(
                benchmark_type="fixed_return",
                fixed_return={"fixed_return": 0.05, "is_compounded": True}
            )
        """
        if benchmark_type not in BENCHMARK_TYPES:
            raise ValueError(
                f"Invalid benchmark_type '{benchmark_type}'. "
                f"Must be one of: {', '.join(sorted(BENCHMARK_TYPES))}"
            )

        attributes: Dict[str, Any] = {"benchmark_type": benchmark_type}

        if name is not None:
            attributes["name"] = name
        if blended is not None:
            attributes["blended"] = blended
        if fixed_return is not None:
            attributes["fixed_return"] = fixed_return
        if portfolio is not None:
            attributes["portfolio"] = portfolio
        if security is not None:
            attributes["security"] = security

        payload = {
            "data": [{
                "type": "benchmarks",
                "attributes": attributes,
            }]
        }

        response = self._post("/benchmarks", json=payload)
        data = response.json()
        benchmark = data.get("data", {})
        benchmark_id = benchmark.get("id", "unknown")
        logger.info(f"Created benchmark: {benchmark_id}")
        return benchmark

    def update_benchmark(
        self,
        benchmark_id: str,
        *,
        name: Optional[str] = None,
        blended: Optional[Dict[str, Any]] = None,
        fixed_return: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Update a single benchmark.

        Note: benchmark_type cannot be changed. For index benchmarks, only the
        name can be updated.

        Args:
            benchmark_id: The ID of the benchmark to update.
            name: New display name for the benchmark.
            blended: For blended benchmarks - dict with "rebalance_interval".
            fixed_return: For fixed return benchmarks - dict with "fixed_return"
                and/or "is_compounded".

        Returns:
            The updated benchmark resource object.
        """
        attributes: Dict[str, Any] = {}

        if name is not None:
            attributes["name"] = name
        if blended is not None:
            attributes["blended"] = blended
        if fixed_return is not None:
            attributes["fixed_return"] = fixed_return

        payload = {
            "data": {
                "id": benchmark_id,
                "type": "benchmarks",
                "attributes": attributes,
            }
        }

        response = self._patch(f"/benchmarks/{benchmark_id}", json=payload)
        data = response.json()
        benchmark = data.get("data", {})
        logger.info(f"Updated benchmark: {benchmark_id}")
        return benchmark

    def update_benchmarks(
        self,
        benchmarks: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Update multiple benchmarks in bulk.

        Args:
            benchmarks: List of benchmark update dicts. Each dict should contain
                "id" and any fields to update (name, blended, fixed_return).

        Returns:
            List of updated benchmark resource objects.

        Example:
            updated = client.portfolio.benchmarks.update_benchmarks([
                {"id": "739", "name": "New Name", "fixed_return": {"fixed_return": 0.17}},
                {"id": "571", "blended": {"rebalance_interval": "SIX_MONTHS"}},
            ])
        """
        payload_data = []
        for benchmark in benchmarks:
            benchmark_id = benchmark.pop("id")
            payload_data.append({
                "id": benchmark_id,
                "type": "benchmarks",
                "attributes": benchmark,
            })

        payload = {"data": payload_data}
        response = self._patch("/benchmarks", json=payload)
        data = response.json()
        updated_benchmarks = data.get("data", [])
        logger.info(f"Updated {len(updated_benchmarks)} benchmarks")
        return updated_benchmarks

    def delete_benchmark(self, benchmark_id: str) -> None:
        """
        Delete a benchmark.

        Note: Fixed return and index benchmarks cannot be deleted.

        Args:
            benchmark_id: The ID of the benchmark to delete.
        """
        self._delete(f"/benchmarks/{benchmark_id}")
        logger.info(f"Deleted benchmark: {benchmark_id}")

    # =========================================================================
    # Benchmark Compositions Methods
    # =========================================================================

    def get_benchmark_composition(self, composition_id: str) -> Dict[str, Any]:
        """
        Get the composition for a blended benchmark.

        The composition ID is the same as the blended benchmark's ID.

        Args:
            composition_id: The ID of the benchmark composition (same as
                the blended benchmark ID).

        Returns:
            The composition resource object containing intervals with
            weighted benchmark allocations.
        """
        response = self._get(f"/benchmark_compositions/{composition_id}")
        data = response.json()
        composition = data.get("data", {})
        logger.debug(f"Retrieved benchmark composition {composition_id}")
        return composition

    def list_benchmark_compositions(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all benchmark compositions with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of composition resource objects.
        """
        compositions = list(
            self._paginate("/benchmark_compositions", page_limit=page_limit)
        )
        logger.debug(f"Listed {len(compositions)} benchmark compositions")
        return compositions

    def update_benchmark_composition(
        self,
        composition_id: str,
        intervals: List[Dict[str, Any]],
    ) -> None:
        """
        Update the composition of a blended benchmark.

        Args:
            composition_id: The ID of the benchmark composition (same as
                the blended benchmark ID).
            intervals: List of interval dicts. Each interval should have:
                - "date": Start date (YYYY-MM-DD) or null for initial value
                - "value": List of {"benchmark_id": int, "percent": float}
                  or null to remove the interval

        Example:
            client.portfolio.benchmarks.update_benchmark_composition(
                composition_id="571",
                intervals=[
                    {"date": None, "value": [
                        {"benchmark_id": 734, "percent": 0.6},
                        {"benchmark_id": 735, "percent": 0.4}
                    ]},
                    {"date": "2024-01-01", "value": [
                        {"benchmark_id": 734, "percent": 0.5},
                        {"benchmark_id": 735, "percent": 0.5}
                    ]}
                ]
            )
        """
        payload = {
            "data": {
                "id": composition_id,
                "type": "benchmark_compositions",
                "attributes": {
                    "intervals": intervals,
                },
            }
        }

        self._patch(f"/benchmark_compositions/{composition_id}", json=payload)
        logger.info(f"Updated benchmark composition: {composition_id}")

    # =========================================================================
    # Imported Benchmark Data Methods
    # =========================================================================

    def get_imported_benchmark_data(self, benchmark_id: str) -> Dict[str, Any]:
        """
        Get daily returns for an imported benchmark.

        Args:
            benchmark_id: The ID of the imported benchmark.

        Returns:
            The imported benchmark data resource object containing
            daily_returns array with date and value pairs.
        """
        response = self._get(f"/imported_benchmark_data/{benchmark_id}")
        data = response.json()
        benchmark_data = data.get("data", {})
        logger.debug(f"Retrieved imported benchmark data for {benchmark_id}")
        return benchmark_data

    def update_imported_benchmark_data(
        self,
        benchmark_id: str,
        daily_returns: List[Dict[str, Any]],
    ) -> None:
        """
        Add or update daily returns for an imported benchmark.

        New returns are appended to existing returns. For dates that already
        have returns, new values overwrite existing ones.

        Args:
            benchmark_id: The ID of the imported benchmark.
            daily_returns: List of daily return dicts with "date" (YYYY-MM-DD)
                and "value" (decimal representing daily return).

        Example:
            client.portfolio.benchmarks.update_imported_benchmark_data(
                benchmark_id="378862",
                daily_returns=[
                    {"date": "2024-01-01", "value": 0.005},
                    {"date": "2024-01-02", "value": -0.003},
                    {"date": "2024-01-03", "value": 0.0},
                ]
            )
        """
        payload = {
            "data": {
                "id": benchmark_id,
                "type": "imported_benchmark_data",
                "attributes": {
                    "daily_returns": daily_returns,
                },
            }
        }

        self._patch(f"/imported_benchmark_data/{benchmark_id}", json=payload)
        logger.info(
            f"Updated imported benchmark data for {benchmark_id} "
            f"({len(daily_returns)} daily returns)"
        )

    # =========================================================================
    # Benchmark Associations Strategies Methods
    # =========================================================================

    def get_benchmark_association_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get a benchmark associations strategy by ID.

        Args:
            strategy_id: The ID of the strategy to retrieve.

        Returns:
            The strategy resource object containing display_name,
            matching_type, and benchmark_associations.
        """
        response = self._get(f"/benchmark_associations_strategies/{strategy_id}")
        data = response.json()
        strategy = data.get("data", {})
        logger.debug(f"Retrieved benchmark association strategy {strategy_id}")
        return strategy

    def list_benchmark_association_strategies(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all benchmark associations strategies with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 500).

        Returns:
            List of strategy resource objects.
        """
        strategies = list(
            self._paginate("/benchmark_associations_strategies", page_limit=page_limit)
        )
        logger.debug(f"Listed {len(strategies)} benchmark association strategies")
        return strategies

    def create_benchmark_association_strategy(
        self,
        display_name: str,
        matching_type: str,
        benchmark_associations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create a new benchmark associations strategy.

        Args:
            display_name: Display name for the strategy.
            matching_type: Either "PATH" (assigns to positions, rolls up) or
                "PDN" (assigns to table rows, doesn't roll up).
            benchmark_associations: List of association dicts. Each should have:
                - "rules": List of {"attribute": str, "value": str|int}
                - "benchmarks": List of benchmark IDs

        Returns:
            The created strategy resource object.

        Raises:
            ValueError: If matching_type is invalid.

        Example:
            strategy = client.portfolio.benchmarks.create_benchmark_association_strategy(
                display_name="Asset Class Strategy",
                matching_type="PATH",
                benchmark_associations=[
                    {
                        "rules": [{"attribute": "asset_class", "value": "Equity"}],
                        "benchmarks": [571, 734]
                    },
                    {
                        "rules": [{"attribute": "sector", "value": "Energy"}],
                        "benchmarks": [735]
                    }
                ]
            )
        """
        if matching_type not in MATCHING_TYPES:
            raise ValueError(
                f"Invalid matching_type '{matching_type}'. "
                f"Must be one of: {', '.join(sorted(MATCHING_TYPES))}"
            )

        payload = {
            "data": {
                "type": "benchmark_associations_strategies",
                "attributes": {
                    "display_name": display_name,
                    "matching_type": matching_type,
                    "benchmark_associations": benchmark_associations,
                },
            }
        }

        response = self._post("/benchmark_associations_strategies", json=payload)
        data = response.json()
        strategy = data.get("data", {})
        strategy_id = strategy.get("id", "unknown")
        logger.info(f"Created benchmark association strategy: {strategy_id}")
        return strategy

    def update_benchmark_association_strategy(
        self,
        strategy_id: str,
        *,
        display_name: Optional[str] = None,
        matching_type: Optional[str] = None,
        benchmark_associations: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Update a benchmark associations strategy.

        Note: If benchmark_associations is omitted (None), existing associations
        are preserved. If provided, it overwrites all existing associations.

        Args:
            strategy_id: The ID of the strategy to update.
            display_name: New display name for the strategy.
            matching_type: New matching type ("PATH" or "PDN").
            benchmark_associations: New associations (overwrites existing).
                Set to empty list to clear all associations.

        Returns:
            The updated strategy resource object.

        Raises:
            ValueError: If matching_type is invalid.
        """
        if matching_type is not None and matching_type not in MATCHING_TYPES:
            raise ValueError(
                f"Invalid matching_type '{matching_type}'. "
                f"Must be one of: {', '.join(sorted(MATCHING_TYPES))}"
            )

        attributes: Dict[str, Any] = {}

        if display_name is not None:
            attributes["display_name"] = display_name
        if matching_type is not None:
            attributes["matching_type"] = matching_type
        if benchmark_associations is not None:
            attributes["benchmark_associations"] = benchmark_associations

        payload = {
            "data": {
                "id": strategy_id,
                "type": "benchmark_associations_strategies",
                "attributes": attributes,
            }
        }

        response = self._patch(
            f"/benchmark_associations_strategies/{strategy_id}", json=payload
        )
        data = response.json()
        strategy = data.get("data", {})
        logger.info(f"Updated benchmark association strategy: {strategy_id}")
        return strategy

    def delete_benchmark_association_strategy(self, strategy_id: str) -> None:
        """
        Delete a benchmark associations strategy.

        Args:
            strategy_id: The ID of the strategy to delete.
        """
        self._delete(f"/benchmark_associations_strategies/{strategy_id}")
        logger.info(f"Deleted benchmark association strategy: {strategy_id}")
