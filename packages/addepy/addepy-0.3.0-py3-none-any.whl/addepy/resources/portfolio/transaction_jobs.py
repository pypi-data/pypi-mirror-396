"""Transaction Jobs resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional, Union

import requests

from ...constants import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_INITIAL_WAIT,
    DEFAULT_MAX_WAIT,
    DEFAULT_PAGE_LIMIT,
    DEFAULT_TIMEOUT,
    PortfolioType,
    TransactionOutputType,
)
from ...exceptions import AddePyError
from ..base import BaseResource

logger = logging.getLogger("addepy")

# Job statuses that indicate the job is still processing
TRANSACTION_JOB_IN_PROGRESS_STATUSES = {
    "Queued",
    "In Progress",
    "In Progress - Waiting For Capacity",
    "Picked Up By Job Runner",
    "Cancel Requested",
}

# Job statuses that indicate the job has completed successfully
TRANSACTION_JOB_SUCCESS_STATUSES = {
    "Completed",
}

# Job statuses that indicate the job has failed or been canceled
TRANSACTION_JOB_FAILURE_STATUSES = {
    "Canceled",
    "Timed Out",
    "Failed",
    "Rejected",
    "Error Cancelled",
    "User Cancelled",
}

# All terminal statuses (job is done, whether success or failure)
TRANSACTION_JOB_TERMINAL_STATUSES = (
    TRANSACTION_JOB_SUCCESS_STATUSES | TRANSACTION_JOB_FAILURE_STATUSES
)


class TransactionJobsResource(BaseResource):
    """
    Resource for Addepar Transaction Jobs API.

    Supports async job-based exports for both transaction views and queries.

    Tier 1 (CRUD wrappers):
        - create_view_job() - Submit a transaction view job
        - create_query_job() - Submit a transaction query job
        - get_job_status() - Check job status
        - get_job_results() - Download completed job results
        - list_jobs() - List all transaction jobs
        - cancel_job() - Cancel a job

    Tier 2 (Orchestration):
        - execute_view_job() - Submit view job, poll, and download in one call
        - execute_query_job() - Submit query job, poll, and download in one call
    """

    # =========================================================================
    # Tier 1: CRUD Wrappers
    # =========================================================================

    def create_view_job(
        self,
        view_id: str,
        portfolio_id: str,
        portfolio_type: PortfolioType,
        start_date: str,
        end_date: str,
        output_type: TransactionOutputType = "CSV",
    ) -> str:
        """
        Submit a transaction view job to the Addepar API.

        Args:
            view_id: ID of the saved transaction view.
            portfolio_id: ID of the portfolio. Use "1" if portfolio_type is FIRM.
            portfolio_type: Type of portfolio. One of: ENTITY, GROUP, FIRM.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            output_type: Output format. One of: CSV, TSV, XLSX. Default: CSV.

        Returns:
            The job ID string.

        Raises:
            AddePyError: If job creation fails or no job ID is returned.

        Note:
            Each job has a timeout limit of 4 hours.
        """
        job_payload = {
            "data": {
                "type": "transaction_jobs",
                "attributes": {
                    "job_type": "transaction_view_results",
                    "parameters": {
                        "view_id": view_id,
                        "portfolio_id": portfolio_id,
                        "portfolio_type": portfolio_type.lower(),
                        "output_type": output_type.lower(),
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            }
        }

        response = self._post("/transaction_jobs", json=job_payload)
        data = response.json()

        job_id = data.get("data", {}).get("id")
        if not job_id:
            raise AddePyError(f"Failed to create transaction view job: {data}")

        logger.info(f"Created transaction view job: {job_id}")
        return job_id

    def create_query_job(
        self,
        columns: List[str],
        portfolio_type: PortfolioType,
        portfolio_id: Union[str, List[str]],
        start_date: str,
        end_date: str,
        *,
        filters: Optional[List[Dict[str, Any]]] = None,
        sorting: Optional[List[Dict[str, Any]]] = None,
        limit: Optional[int] = None,
        include_online_valuations: bool = False,
        include_unverified: bool = False,
        include_deleted: bool = False,
    ) -> str:
        """
        Submit a transaction query job to the Addepar API.

        Args:
            columns: List of column attribute keys to return.
            portfolio_type: Type of portfolio. One of: ENTITY, GROUP, FIRM.
            portfolio_id: Portfolio ID or list of IDs. Use "1" if portfolio_type is FIRM.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            filters: Optional list of filter objects.
            sorting: Optional list of sorting objects (up to 3 columns).
            limit: Max number of transactions to return.
            include_online_valuations: Include online snapshots (default: False).
            include_unverified: Include unverified transactions (default: False).
            include_deleted: Include deleted online transactions (default: False).

        Returns:
            The job ID string.

        Raises:
            AddePyError: If job creation fails or no job ID is returned.

        Note:
            Each job has a timeout limit of 4 hours.
        """
        # Normalize portfolio_id to list if needed
        if isinstance(portfolio_id, str):
            portfolio_id = [portfolio_id]

        parameters: Dict[str, Any] = {
            "columns": columns,
            "portfolio_type": portfolio_type.lower(),
            "portfolio_id": portfolio_id,
            "start_date": start_date,
            "end_date": end_date,
            "include_online_valuations": include_online_valuations,
            "include_unverified": include_unverified,
            "include_deleted": include_deleted,
        }

        if filters is not None:
            parameters["filters"] = filters
        if sorting is not None:
            parameters["sorting"] = sorting
        if limit is not None:
            parameters["limit"] = limit

        job_payload = {
            "data": {
                "type": "transaction_jobs",
                "attributes": {
                    "job_type": "transaction_query",
                    "parameters": parameters,
                },
            }
        }

        response = self._post("/transaction_jobs", json=job_payload)
        data = response.json()

        job_id = data.get("data", {}).get("id")
        if not job_id:
            raise AddePyError(f"Failed to create transaction query job: {data}")

        logger.info(f"Created transaction query job: {job_id}")
        return job_id

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a transaction job.

        Args:
            job_id: The ID of the job to check.

        Returns:
            The job data dictionary containing status information.
            Access status via: data['data']['attributes']['status']

            Possible status values:
            - 'Queued': Job has not yet been processed
            - 'In Progress - Waiting For Capacity': Placed back in queue
            - 'In Progress': Currently being processed
            - 'Picked Up By Job Runner': Picked up, waiting to run
            - 'Completed': Finished, results available
            - 'Canceled': Canceled by user
            - 'Timed Out': Results expired (24 hours after creation)
            - 'Failed': Processing failed due to server issue
            - 'Rejected': Job exceeds maximum quota
            - 'Error Cancelled': Canceled due to error (see errors field)
            - 'Cancel Requested': Cancel request received, job still running
            - 'User Cancelled': Job was canceled
        """
        response = self._get(f"/transaction_jobs/{job_id}")
        data = response.json()
        status = data.get("data", {}).get("attributes", {}).get("status", "Unknown")
        logger.debug(f"Transaction job {job_id} status: {status}")
        return data

    def get_job_results(self, job_id: str) -> requests.Response:
        """
        Download the results of a completed transaction job.

        Note: Job results are deleted 24 hours after a job is created.

        Args:
            job_id: The ID of the completed job.

        Returns:
            The requests.Response object containing the job results.
            - For query jobs: Use response.json() for JSON data
            - For view jobs: Use response.content (XLSX) or response.text (CSV/TSV)

        Raises:
            NotFoundError: If job has not completed or doesn't return results.
            GoneError: If results have expired (after 24 hours).
        """
        logger.debug(f"Downloading results for transaction job {job_id}")
        return self._get(f"/transaction_jobs/{job_id}/download")

    def list_jobs(self, *, page_limit: int = DEFAULT_PAGE_LIMIT) -> List[Dict[str, Any]]:
        """
        List all transaction jobs with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of transaction job resource objects.
        """
        jobs = list(self._paginate("/transaction_jobs", page_limit=page_limit))
        logger.debug(f"Listed {len(jobs)} transaction jobs")
        return jobs

    def cancel_job(self, job_id: str) -> None:
        """
        Cancel a transaction job.

        Can cancel jobs that are waiting, in progress, or already completed.
        - If 'Queued' or 'Waiting For Capacity': Job will not run
        - If 'In Progress': Cancel request is submitted
        - If 'Completed': Results are archived

        Args:
            job_id: The ID of the job to cancel.
        """
        self._delete(f"/transaction_jobs/{job_id}")
        logger.info(f"Canceled transaction job: {job_id}")

    # =========================================================================
    # Tier 2: Orchestration Methods
    # =========================================================================

    def execute_view_job(
        self,
        view_id: str,
        portfolio_id: str,
        portfolio_type: PortfolioType,
        start_date: str,
        end_date: str,
        output_type: TransactionOutputType = "CSV",
        *,
        initial_wait: float = DEFAULT_INITIAL_WAIT,
        max_wait: float = DEFAULT_MAX_WAIT,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> requests.Response:
        """
        Submit a transaction view job, poll for completion, and download results.

        This is a convenience method that combines create_view_job(), polling with
        get_job_status(), and get_job_results() into a single call.

        Args:
            view_id: ID of the saved transaction view.
            portfolio_id: ID of the portfolio. Use "1" if portfolio_type is FIRM.
            portfolio_type: Type of portfolio (e.g., 'ENTITY', 'GROUP', 'FIRM').
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            output_type: Output format (CSV, TSV, XLSX). Default: CSV.
            initial_wait: Initial polling interval in seconds (default: 30).
            max_wait: Maximum polling interval in seconds (default: 300).
            backoff_factor: Multiplier for exponential backoff (default: 1.5).
            timeout: Maximum time to wait for completion (default: 1200).

        Returns:
            Response containing the view results.
            Use response.content (XLSX) or response.text (CSV/TSV).

        Raises:
            AddePyError: If job creation fails or job doesn't complete successfully.
            AddePyTimeoutError: If job doesn't complete within timeout.
        """
        # Step 1: Submit the job
        job_id = self.create_view_job(
            view_id=view_id,
            portfolio_id=portfolio_id,
            portfolio_type=portfolio_type,
            start_date=start_date,
            end_date=end_date,
            output_type=output_type,
        )
        return self._poll_and_download(
            job_id,
            initial_wait=initial_wait,
            max_wait=max_wait,
            backoff_factor=backoff_factor,
            timeout=timeout,
        )

    def execute_query_job(
        self,
        columns: List[str],
        portfolio_type: PortfolioType,
        portfolio_id: Union[str, List[str]],
        start_date: str,
        end_date: str,
        *,
        filters: [List[Dict[str, Any]]] = [],
        sorting: [List[Dict[str, Any]]] = [],
        limit: Optional[int] = None,
        include_online_valuations: bool = False,
        include_unverified: bool = False,
        include_deleted: bool = False,
        initial_wait: float = DEFAULT_INITIAL_WAIT,
        max_wait: float = DEFAULT_MAX_WAIT,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> requests.Response:
        """
        Submit a transaction query job, poll for completion, and download results.

        This is a convenience method that combines create_query_job(), polling with
        get_job_status(), and get_job_results() into a single call.

        Args:
            columns: List of column attribute keys to return.
            portfolio_type: Type of portfolio (e.g., 'ENTITY', 'GROUP', 'FIRM').
            portfolio_id: Portfolio ID or list of IDs. Use "1" if portfolio_type is FIRM.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            filters: List of filter objects. Default is an empty list.
            sorting: List of sorting objects (up to 3 columns). Default is an empty list.
            limit: Max number of transactions to return.
            include_online_valuations: Include online snapshots (default: False).
            include_unverified: Include unverified transactions (default: False).
            include_deleted: Include deleted online transactions (default: False).
            initial_wait: Initial polling interval in seconds (default: 30).
            max_wait: Maximum polling interval in seconds (default: 300).
            backoff_factor: Multiplier for exponential backoff (default: 1.5).
            timeout: Maximum time to wait for completion (default: 1200).

        Returns:
            Response containing the query results (JSON).

        Raises:
            AddePyError: If job creation fails or job doesn't complete successfully.
            AddePyTimeoutError: If job doesn't complete within timeout.
        """
        # Step 1: Submit the job
        job_id = self.create_query_job(
            columns=columns,
            portfolio_type=portfolio_type,
            portfolio_id=portfolio_id,
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            sorting=sorting,
            limit=limit,
            include_online_valuations=include_online_valuations,
            include_unverified=include_unverified,
            include_deleted=include_deleted,
        )
        return self._poll_and_download(
            job_id,
            initial_wait=initial_wait,
            max_wait=max_wait,
            backoff_factor=backoff_factor,
            timeout=timeout,
        )

    def _poll_and_download(
        self,
        job_id: str,
        *,
        initial_wait: float,
        max_wait: float,
        backoff_factor: float,
        timeout: float,
    ) -> requests.Response:
        """
        Poll for job completion and download results.

        Internal helper method used by execute_view_job() and execute_query_job().
        """
        logger.info(f"Polling transaction job {job_id} for completion...")

        # Step 2: Poll for completion
        def check_status(jid: str) -> str:
            data = self.get_job_status(jid)
            return data.get("data", {}).get("attributes", {}).get("status", "Unknown")

        def is_complete(status: str) -> bool:
            return status in TRANSACTION_JOB_TERMINAL_STATUSES

        final_status = self._poll_until_complete(
            job_id=job_id,
            check_status_fn=check_status,
            is_complete_fn=is_complete,
            initial_wait=initial_wait,
            max_wait=max_wait,
            backoff_factor=backoff_factor,
            timeout=timeout,
            job_type="transaction job",
        )

        # Step 3: Verify success and download results
        if final_status not in TRANSACTION_JOB_SUCCESS_STATUSES:
            raise AddePyError(
                f"Transaction job {job_id} failed with status: {final_status}"
            )

        logger.info(f"Transaction job {job_id} completed successfully, downloading results")
        return self.get_job_results(job_id)
