"""Portfolio Jobs resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

import requests

from ...constants import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_INITIAL_WAIT,
    DEFAULT_MAX_WAIT,
    DEFAULT_PAGE_LIMIT,
    DEFAULT_TIMEOUT,
)
from ...exceptions import AddePyError
from ..base import BaseResource

logger = logging.getLogger("addepy")

# Job statuses that indicate the job is still processing
JOB_IN_PROGRESS_STATUSES = {
    "Queued",
    "In Progress",
    "In Progress - Waiting For Capacity",
    "Picked Up By Job Runner",
    "Cancel Requested",
}

# Job statuses that indicate the job has completed successfully
JOB_SUCCESS_STATUSES = {
    "Completed",
}

# Job statuses that indicate the job has failed or been canceled
JOB_FAILURE_STATUSES = {
    "Canceled",
    "Timed Out",
    "Failed",
    "Rejected",
    "Error Cancelled",
    "User Cancelled",
}

# All terminal statuses (job is done, whether success or failure)
JOB_TERMINAL_STATUSES = JOB_SUCCESS_STATUSES | JOB_FAILURE_STATUSES


class JobsResource(BaseResource):
    """
    Resource for Addepar Portfolio Jobs API.

    Supports both portfolio query jobs and portfolio view jobs.

    Tier 1 (CRUD wrappers):
        - create_query_job() - Submit a portfolio query job
        - create_view_job() - Submit a portfolio view job
        - get_job_status() - Check job status
        - get_job_results() - Download completed job results
        - list_jobs() - List all jobs
        - cancel_job() - Cancel a job

    Tier 2 (Orchestration):
        - execute_portfolio_query() - Submit query, poll, and download in one call
        - execute_portfolio_view() - Submit view job, poll, and download in one call
    """

    # =========================================================================
    # Tier 1: CRUD Wrappers
    # =========================================================================

    def create_query_job(
        self,
        portfolio_type: str,
        portfolio_id: str,
        start_date: str,
        end_date: str,
        columns: List[Dict[str, Any]],
        groupings: List[Dict[str, Any]],
        *,
        filters: Optional[List[Dict[str, Any]]] = None,
        hide_previous_holdings: bool = False,
    ) -> str:
        """
        Submit a portfolio query job to the Addepar API.

        Args:
            portfolio_type: Type of portfolio. One of: ENTITY, ENTITY_FUNDS, GROUP,
                GROUP_FUNDS, FIRM, FIRM_ACCOUNTS, FIRM_CLIENTS, FIRM_HOUSEHOLDS,
                FIRM_UNVERIFIED_ACCOUNTS.
            portfolio_id: ID of the portfolio. Use "1" if portfolio_type is FIRM.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            columns: List of column definitions with 'key' and optional 'arguments'.
            groupings: List of grouping definitions with 'key' and optional 'arguments'.
            filters: Optional list of filter definitions.
            hide_previous_holdings: If True, exclude holdings not held at end of period.

        Returns:
            The job ID string.

        Raises:
            AddePyError: If job creation fails or no job ID is returned.
        """
        parameters = {
            "portfolio_type": portfolio_type.lower(),
            "portfolio_id": portfolio_id,
            "start_date": start_date,
            "end_date": end_date,
            "columns": columns,
            "groupings": groupings,
            "hide_previous_holdings": hide_previous_holdings,
        }
        if filters:
            parameters["filters"] = filters

        job_payload = {
            "data": {
                "type": "jobs",
                "attributes": {
                    "job_type": "PORTFOLIO_QUERY",
                    "parameters": parameters,
                },
            }
        }

        response = self._post("/jobs", json=job_payload)
        data = response.json()

        job_id = data.get("data", {}).get("id")
        if not job_id:
            raise AddePyError(f"Failed to create job: {data}")

        logger.info(f"Created portfolio query job: {job_id}")
        return job_id

    def create_view_job(
        self,
        view_id: str,
        portfolio_type: str,
        portfolio_id: str,
        start_date: str,
        end_date: str,
        output_type: str = "JSON",
    ) -> str:
        """
        Submit a portfolio view job to the Addepar API.

        Args:
            view_id: ID of the saved portfolio view.
            portfolio_type: Type of portfolio. One of: ENTITY, ENTITY_FUNDS, GROUP,
                GROUP_FUNDS, FIRM, FIRM_ACCOUNTS, FIRM_CLIENTS, FIRM_HOUSEHOLDS,
                FIRM_UNVERIFIED_ACCOUNTS.
            portfolio_id: ID of the portfolio. Use "1" if portfolio_type is FIRM.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            output_type: Output format. One of: JSON, CSV, TSV, XLSX. Default: JSON.

        Returns:
            The job ID string.

        Raises:
            AddePyError: If job creation fails or no job ID is returned.
        """
        job_payload = {
            "data": {
                "type": "jobs",
                "attributes": {
                    "job_type": "portfolio_view_results",
                    "parameters": {
                        "view_id": view_id,
                        "portfolio_type": portfolio_type.lower(),
                        "portfolio_id": portfolio_id,
                        "output_type": output_type.lower(),
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            }
        }

        response = self._post("/jobs", json=job_payload)
        data = response.json()

        job_id = data.get("data", {}).get("id")
        if not job_id:
            raise AddePyError(f"Failed to create job: {data}")

        logger.info(f"Created portfolio view job: {job_id}")
        return job_id

    def create_job(self, query_dict: Dict[str, Any]) -> str:
        """
        Submit a portfolio query job using a raw query dictionary.

        This is a lower-level method that accepts the full query structure.
        For a more user-friendly interface, use create_query_job() or create_view_job().

        Args:
            query_dict: Portfolio query configuration with structure:
                       {'data': {'attributes': {...}}}

        Returns:
            The job ID string.

        Raises:
            AddePyError: If job creation fails or no job ID is returned.
        """
        job_query = {
            "data": {
                "type": "jobs",
                "attributes": {
                    "job_type": "PORTFOLIO_QUERY",
                    "parameters": query_dict["data"]["attributes"],
                },
            }
        }

        response = self._post("/jobs", json=job_query)
        data = response.json()

        job_id = data.get("data", {}).get("id")
        if not job_id:
            raise AddePyError(f"Failed to create job: {data}")

        logger.info(f"Created portfolio query job: {job_id}")
        return job_id

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a job.

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
        response = self._get(f"/jobs/{job_id}")
        data = response.json()
        status = data.get("data", {}).get("attributes", {}).get("status", "Unknown")
        logger.debug(f"Job {job_id} status: {status}")
        return data

    def get_job_results(self, job_id: str) -> requests.Response:
        """
        Download the results of a completed job.

        Note: Job results are deleted 24 hours after a job is created.

        Args:
            job_id: The ID of the completed job.

        Returns:
            The requests.Response object containing the job results.
            Use response.text or response.json() to access the data.

        Raises:
            NotFoundError: If job has not completed or doesn't return results.
            GoneError: If results have expired (after 24 hours).
        """
        logger.debug(f"Downloading results for job {job_id}")
        return self._get(f"/jobs/{job_id}/download")

    def list_jobs(self, *, page_limit: int = DEFAULT_PAGE_LIMIT) -> List[Dict[str, Any]]:
        """
        List all jobs with pagination.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of job resource objects.
        """
        jobs = list(self._paginate("/jobs", page_limit=page_limit))
        logger.debug(f"Listed {len(jobs)} jobs")
        return jobs

    def cancel_job(self, job_id: str) -> None:
        """
        Cancel a job.

        Can cancel jobs that are waiting, in progress, or already completed.
        - If 'Queued' or 'Waiting For Capacity': Job will not run
        - If 'In Progress': Cancel request is submitted
        - If 'Completed': Results are archived

        Args:
            job_id: The ID of the job to cancel.
        """
        self._delete(f"/jobs/{job_id}")
        logger.info(f"Canceled job: {job_id}")

    # =========================================================================
    # Tier 2: Orchestration Methods
    # =========================================================================

    def execute_portfolio_query_job(
        self,
        query_dict: Dict[str, Any],
        *,
        initial_wait: float = DEFAULT_INITIAL_WAIT,
        max_wait: float = DEFAULT_MAX_WAIT,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> requests.Response:
        """
        Submit a portfolio query job, poll for completion, and download results.

        This is a convenience method that combines create_job(), polling with
        get_job_status(), and get_job_results() into a single call.

        Args:
            query_dict: The portfolio query dictionary to submit.
            initial_wait: Initial polling interval in seconds (default: 30).
            max_wait: Maximum polling interval in seconds (default: 300).
            backoff_factor: Multiplier for exponential backoff (default: 1.5).
            timeout: Maximum time to wait for completion (default: 1200).

        Returns:
            Response containing the query results.

        Raises:
            AddePyError: If job creation fails or job doesn't complete successfully.
            AddePyTimeoutError: If job doesn't complete within timeout.
        """
        # Step 1: Submit the job (Tier 1)
        job_id = self.create_job(query_dict)
        return self._poll_and_download(
            job_id,
            initial_wait=initial_wait,
            max_wait=max_wait,
            backoff_factor=backoff_factor,
            timeout=timeout,
        )

    def execute_view_job(
        self,
        view_id: str,
        portfolio_type: str,
        portfolio_id: str,
        start_date: str,
        end_date: str,
        output_type: str = "JSON",
        *,
        initial_wait: float = DEFAULT_INITIAL_WAIT,
        max_wait: float = DEFAULT_MAX_WAIT,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> requests.Response:
        """
        Submit a portfolio view job, poll for completion, and download results.

        This is a convenience method that combines create_view_job(), polling with
        get_job_status(), and get_job_results() into a single call.

        Args:
            view_id: ID of the saved portfolio view.
            portfolio_type: Type of portfolio (e.g., 'ENTITY', 'GROUP', 'FIRM').
            portfolio_id: ID of the portfolio.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            output_type: Output format (JSON, CSV, TSV, XLSX). Default: JSON.
            initial_wait: Initial polling interval in seconds (default: 30).
            max_wait: Maximum polling interval in seconds (default: 300).
            backoff_factor: Multiplier for exponential backoff (default: 1.5).
            timeout: Maximum time to wait for completion (default: 1200).

        Returns:
            Response containing the view results.

        Raises:
            AddePyError: If job creation fails or job doesn't complete successfully.
            AddePyTimeoutError: If job doesn't complete within timeout.
        """
        # Step 1: Submit the job (Tier 1)
        job_id = self.create_view_job(
            view_id=view_id,
            portfolio_type=portfolio_type,
            portfolio_id=portfolio_id,
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

        Internal helper method used by execute_portfolio_query() and execute_view_job().
        """
        logger.info(f"Polling job {job_id} for completion...")

        # Step 2: Poll for completion
        def check_status(jid: str) -> str:
            data = self.get_job_status(jid)
            return data.get("data", {}).get("attributes", {}).get("status", "Unknown")

        def is_complete(status: str) -> bool:
            return status in JOB_TERMINAL_STATUSES

        final_status = self._poll_until_complete(
            job_id=job_id,
            check_status_fn=check_status,
            is_complete_fn=is_complete,
            initial_wait=initial_wait,
            max_wait=max_wait,
            backoff_factor=backoff_factor,
            timeout=timeout,
            job_type="job",
        )

        # Step 3: Verify success and download results
        if final_status not in JOB_SUCCESS_STATUSES:
            raise AddePyError(f"Job {job_id} failed with status: {final_status}")

        logger.info(f"Job {job_id} completed successfully, downloading results")
        return self.get_job_results(job_id)
