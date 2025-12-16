"""Base resource class with HTTP helpers and polling utilities."""

from ..exceptions import AddePyTimeoutError
from ..constants import (
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_INITIAL_WAIT,
    DEFAULT_MAX_WAIT,
    DEFAULT_PAGE_LIMIT,
    DEFAULT_TIMEOUT,
    MAX_PAGE_LIMIT,
)
import logging
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, Generator, Optional, TypeVar
from urllib.parse import parse_qs, urlparse

import requests

logger = logging.getLogger("addepy")


if TYPE_CHECKING:
    from ..client import AddeparClient

T = TypeVar("T")


class BaseResource:
    """
    Base class for all API resource classes.

    Provides:
    - HTTP convenience methods (_get, _post, _patch, _delete)
    - Reusable polling utility with exponential backoff
    """

    def __init__(self, client: "AddeparClient") -> None:
        self._client = client

    # =========================================================================
    # HTTP Convenience Methods
    # =========================================================================

    def _get(
            self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
        ) -> requests.Response:
        """Make a GET request."""
        return self._client._request("GET", endpoint, params=params, **kwargs)

    def _post(
            self,
            endpoint: str,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs: Any,
        ) -> requests.Response:
        """Make a POST request."""
        return self._client._request(
            "POST",
            endpoint,
            json=json,
            data=data,
            params=params,
            headers=headers,
            **kwargs,
        )

    def _patch(
            self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
        ) -> requests.Response:
        """Make a PATCH request."""
        return self._client._request("PATCH", endpoint, json=json, **kwargs)

    def _put(
            self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs: Any
        ) -> requests.Response:
        """Make a PUT request."""
        return self._client._request("PUT", endpoint, json=json, **kwargs)

    def _delete(
            self,
            endpoint: str,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs: Any,
        ) -> requests.Response:
        """Make a DELETE request."""
        return self._client._request(
            "DELETE", endpoint, json=json, data=data, params=params, headers=headers, **kwargs
        )

    # =========================================================================
    # Polling Utility
    # =========================================================================

    def _poll_until_complete(
            self,
            job_id: str,
            check_status_fn: Callable[[str], T],
            is_complete_fn: Callable[[T], bool],
            *,
            initial_wait: float = DEFAULT_INITIAL_WAIT,
            max_wait: float = DEFAULT_MAX_WAIT,
            backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
            timeout: float = DEFAULT_TIMEOUT,
            job_type: str = "job",
        ) -> T:
        """
        Poll for job completion using exponential backoff.

        This is the reusable polling pattern extracted from the reference
        implementation. It supports both portfolio jobs and import jobs.

        Args:
            job_id: The ID of the job to poll
            check_status_fn: Function that takes job_id and returns status data
            is_complete_fn: Function that takes status data and returns True if complete
            initial_wait: Initial polling interval in seconds (default: 30)
            max_wait: Maximum polling interval in seconds (default: 300)
            backoff_factor: Multiplier for exponential backoff (default: 1.5)
            timeout: Maximum total wait time in seconds (default: 1200)
            job_type: Type of job for error messages (e.g., "job", "import")

        Returns:
            The final status data when is_complete_fn returns True

        Raises:
            AddePyTimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()
        wait_time = initial_wait
        last_status: Optional[T] = None
        attempt = 1

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                logger.error(
                    f"{job_type.capitalize()} {job_id} timed out after {timeout}s"
                )
                raise AddePyTimeoutError(
                    f"{job_type.capitalize()} {job_id} did not complete within {timeout} seconds.",
                    job_id=job_id,
                    last_status=str(last_status) if last_status else None,
                )

            logger.debug(
                f"Polling {job_type} {job_id}: attempt {attempt}, "
                f"waiting {wait_time:.1f}s (elapsed: {elapsed_time:.1f}s)"
            )
            time.sleep(wait_time)

            status_data = check_status_fn(job_id)
            last_status = status_data

            if is_complete_fn(status_data):
                logger.debug(f"{job_type.capitalize()} {job_id} completed")
                return status_data

            # Exponential backoff with cap
            wait_time = min(wait_time * backoff_factor, max_wait)
            attempt += 1

    # =========================================================================
    # Pagination Utility
    # =========================================================================

    def _paginate(
            self,
            endpoint: str,
            *,
            params: Optional[Dict[str, Any]] = None,
            page_limit: int = DEFAULT_PAGE_LIMIT,
        ) -> Generator[Dict[str, Any], None, None]:
        """
        Auto-paginate through all results from a paginated endpoint.

        Yields each item from the 'data' array across all pages.
        Follows the JSON:API pagination pattern using page[limit] and page[after].

        Args:
            endpoint: API endpoint (e.g., "/entities")
            params: Additional query parameters (filters, etc.)
            page_limit: Results per page (default: 500, max: 2000)

        Yields:
            Individual resource objects from the 'data' array

        Example:
            for entity in self._paginate("/entities"):
                print(entity["id"], entity["attributes"]["name"])

            # Or collect all at once:
            all_entities = list(self._paginate("/entities"))
        """
        # Enforce max page limit
        page_limit = min(page_limit, MAX_PAGE_LIMIT)

        # Build initial params
        request_params = dict(params) if params else {}
        request_params["page[limit]"] = page_limit

        page_number = 1
        total_items = 0

        while True:
            logger.debug(f"Fetching page {page_number} from {endpoint}")
            response = self._get(endpoint, params=request_params)
            data = response.json()

            # Yield each item from the data array
            items = data.get("data", [])
            for item in items:
                total_items += 1
                yield item

            logger.debug(f"Page {page_number}: fetched {len(items)} items")

            # Check for next page
            next_url = data.get("links", {}).get("next")
            if not next_url:
                logger.debug(
                    f"Pagination complete: {total_items} total items from {page_number} pages"
                )
                break

            # Parse the page[after] cursor from the next URL
            parsed = urlparse(next_url)
            query_params = parse_qs(parsed.query)

            # Extract page[after] value
            page_after = query_params.get("page[after]", [None])[0]
            if not page_after:
                logger.debug(
                    f"Pagination complete: {total_items} total items from {page_number} pages"
                )
                break

            request_params["page[after]"] = page_after
            page_number += 1

    def _paginate_offset(
            self,
            endpoint: str,
            *,
            params: Optional[Dict[str, Any]] = None,
            page_size: int = 50,
        ) -> Generator[Dict[str, Any], None, None]:
        """
        Auto-paginate through all results using offset-based pagination.

        Yields each item from the 'data' array across all pages.
        Follows the JSON:API pagination pattern using page[size] and page[number].

        Args:
            endpoint: API endpoint (e.g., "/generated_reports")
            params: Additional query parameters (filters, etc.)
            page_size: Results per page (default: 50)

        Yields:
            Individual resource objects from the 'data' array

        Example:
            for report in self._paginate_offset("/generated_reports"):
                print(report["id"], report["attributes"]["status"])

            # Or collect all at once:
            all_reports = list(self._paginate_offset("/generated_reports"))
        """
        # Build initial params
        request_params = dict(params) if params else {}
        request_params["page[size]"] = page_size
        request_params["page[number]"] = 0

        page_number = 0
        total_items = 0

        while True:
            logger.debug(f"Fetching page {page_number} from {endpoint}")
            response = self._get(endpoint, params=request_params)
            data = response.json()

            # Yield each item from the data array
            items = data.get("data", [])
            if isinstance(items, dict):
                # Single item response
                items = [items]

            for item in items:
                total_items += 1
                yield item

            logger.debug(f"Page {page_number}: fetched {len(items)} items")

            # Check for next page
            next_url = data.get("links", {}).get("next")
            if not next_url:
                logger.debug(
                    f"Pagination complete: {total_items} total items from {page_number + 1} pages"
                )
                break

            # Increment page number for next request
            page_number += 1
            request_params["page[number]"] = page_number
