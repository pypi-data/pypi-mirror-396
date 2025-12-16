"""Portfolio namespace containing portfolio-related resources."""
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...client import AddeparClient

from .analysis import AnalysisResource
from .arguments import ArgumentsResource
from .attributes import AttributesResource
from .benchmarks import BenchmarksResource
from .composite_securities import CompositeSecuritiesResource
from .constituent_attributes import ConstituentAttributesResource
from .historical_prices import HistoricalPricesResource
from .jobs import JobsResource
from .snapshots import SnapshotsResource
from .transactions import TransactionsResource
from .transaction_jobs import TransactionJobsResource


class PortfolioNamespace:
    """
    Namespace for portfolio-related API resources.

    Usage:
        client.portfolio.analysis.list_views()
        client.portfolio.analysis.get_view_results(...)
        client.portfolio.analysis.query(...)
        client.portfolio.arguments.list_arguments()
        client.portfolio.attributes.list_attributes(...)
        client.portfolio.benchmarks.list_benchmarks()
        client.portfolio.benchmarks.create_benchmark(...)
        client.portfolio.composite_securities.import_constituents(...)
        client.portfolio.constituent_attributes.create_constituent_attribute(...)
        client.portfolio.historical_prices.get_prices(...)
        client.portfolio.jobs.create_job(...)
        client.portfolio.jobs.execute_portfolio_query(...)
        client.portfolio.snapshots.create_snapshot(...)
        client.portfolio.snapshots.get_snapshot(...)
        client.portfolio.transactions.create_transaction(...)
        client.portfolio.transaction_jobs.execute_view_job(...)
    """

    def __init__(self, client: "AddeparClient") -> None:
        self._client = client
        self._analysis: Optional[AnalysisResource] = None
        self._arguments: Optional[ArgumentsResource] = None
        self._attributes: Optional[AttributesResource] = None
        self._benchmarks: Optional[BenchmarksResource] = None
        self._composite_securities: Optional[CompositeSecuritiesResource] = None
        self._constituent_attributes: Optional[ConstituentAttributesResource] = None
        self._historical_prices: Optional[HistoricalPricesResource] = None
        self._jobs: Optional[JobsResource] = None
        self._snapshots: Optional[SnapshotsResource] = None
        self._transactions: Optional[TransactionsResource] = None
        self._transaction_jobs: Optional[TransactionJobsResource] = None

    @property
    def analysis(self) -> AnalysisResource:
        """Access analysis resource for portfolio views and queries."""
        if self._analysis is None:
            self._analysis = AnalysisResource(self._client)
        return self._analysis

    @property
    def arguments(self) -> ArgumentsResource:
        """Access arguments resource for attribute arguments."""
        if self._arguments is None:
            self._arguments = ArgumentsResource(self._client)
        return self._arguments

    @property
    def attributes(self) -> AttributesResource:
        """Access attributes resource for attribute discovery."""
        if self._attributes is None:
            self._attributes = AttributesResource(self._client)
        return self._attributes

    @property
    def benchmarks(self) -> BenchmarksResource:
        """Access benchmarks resource."""
        if self._benchmarks is None:
            self._benchmarks = BenchmarksResource(self._client)
        return self._benchmarks

    @property
    def composite_securities(self) -> CompositeSecuritiesResource:
        """Access composite securities resource for constituent weights."""
        if self._composite_securities is None:
            self._composite_securities = CompositeSecuritiesResource(self._client)
        return self._composite_securities

    @property
    def constituent_attributes(self) -> ConstituentAttributesResource:
        """Access constituent attributes resource."""
        if self._constituent_attributes is None:
            self._constituent_attributes = ConstituentAttributesResource(self._client)
        return self._constituent_attributes

    @property
    def historical_prices(self) -> HistoricalPricesResource:
        """Access historical prices resource."""
        if self._historical_prices is None:
            self._historical_prices = HistoricalPricesResource(self._client)
        return self._historical_prices

    @property
    def jobs(self) -> JobsResource:
        """Access portfolio jobs resource."""
        if self._jobs is None:
            self._jobs = JobsResource(self._client)
        return self._jobs

    @property
    def snapshots(self) -> SnapshotsResource:
        """Access snapshots resource."""
        if self._snapshots is None:
            self._snapshots = SnapshotsResource(self._client)
        return self._snapshots

    @property
    def transactions(self) -> TransactionsResource:
        """Access transactions resource."""
        if self._transactions is None:
            self._transactions = TransactionsResource(self._client)
        return self._transactions

    @property
    def transaction_jobs(self) -> TransactionJobsResource:
        """Access transaction jobs resource."""
        if self._transaction_jobs is None:
            self._transaction_jobs = TransactionJobsResource(self._client)
        return self._transaction_jobs


__all__ = [
    "PortfolioNamespace",
    "AnalysisResource",
    "ArgumentsResource",
    "AttributesResource",
    "BenchmarksResource",
    "CompositeSecuritiesResource",
    "ConstituentAttributesResource",
    "HistoricalPricesResource",
    "JobsResource",
    "SnapshotsResource",
    "TransactionsResource",
    "TransactionJobsResource",
]
