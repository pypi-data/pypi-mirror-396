"""Import Tool resource for the Addepar API."""
import io
import logging
from typing import Any, Dict

import pandas as pd

from ...constants import (
    ALL_VALID_IMPORT_TYPES,
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_INITIAL_WAIT,
    DEFAULT_MAX_WAIT,
    DEFAULT_TIMEOUT,
    IMPORT_COMPLETED_STATUSES,
    IMPORT_RESULT_READY_STATUSES,
    VALID_DELETE_IMPORT_TYPES,
    AddeparImportType,
)
from ...exceptions import AddePyError, ValidationError
from ..base import BaseResource

logger = logging.getLogger("addepy")


class ImportToolResource(BaseResource):
    """
    Resource for Addepar Import Tool.

    Tier 1 (CRUD wrappers):
        - create_import() - Submit an import job
        - get_import_status() - Check import status
        - get_import_results() - Get import results

    Tier 2 (Orchestration):
        - execute_import() - Submit, poll, and fetch results in one call
    """

    # =========================================================================
    # Tier 1: CRUD Wrappers
    # =========================================================================

    def create_import(
            self,
            import_dataframe: pd.DataFrame,
            import_type: AddeparImportType,
            *,
            is_dry_run: bool = True,
            ignore_warnings: bool = False,
        ) -> str:
        """
        Submit an import job to the Addepar Imports API.

        Args:
            import_dataframe: Pandas DataFrame containing data to import.
            import_type: Type of data being imported (e.g., 'ATTRIBUTES', 'TRANSACTIONS').
            is_dry_run: If True, performs validation without saving (default: True).
            ignore_warnings: If True, proceed despite warnings (default: False).

        Returns:
            The import ID string.

        Raises:
            ValidationError: If import_type is invalid.
            AddePyError: If import creation fails or no import ID is returned.
        """
        normalized_type = import_type.upper()

        # Validate import type
        if normalized_type not in ALL_VALID_IMPORT_TYPES:
            raise ValidationError(
                f"Invalid import_type '{import_type}'. "
                f"Must be one of: {', '.join(sorted(ALL_VALID_IMPORT_TYPES))}"
            )

        # Determine HTTP method based on import type
        if normalized_type in VALID_DELETE_IMPORT_TYPES:
            http_method = "DELETE"
        else:
            http_method = "POST"

        # Build endpoint with query parameters
        endpoint = "/imports"
        params = {
            "import_type": normalized_type,
            "is_dry_run": str(is_dry_run).lower(),
            "ignore_warnings": str(ignore_warnings).lower(),
        }

        # Convert DataFrame to CSV
        csv_buffer = io.StringIO()
        import_dataframe.to_csv(csv_buffer, index=False, encoding="utf-8")
        csv_payload = csv_buffer.getvalue()

        # Override Content-Type for CSV payload
        headers = {"Content-Type": "text/plain"}

        # Make request
        response = self._client._request(
            method=http_method,
            endpoint=endpoint,
            data=csv_payload,
            params=params,
            headers=headers,
        )

        # Extract import ID
        try:
            import_id = response.json().get("data", {}).get("id")
        except Exception:
            import_id = None

        if not import_id:
            raise AddePyError(f"Failed to create import: {response.text}")

        mode = "dry run" if is_dry_run else "live"
        logger.info(f"Created {normalized_type} import ({mode}): {import_id}")
        return import_id

    def get_import_status(self, import_id: str) -> str:
        """
        Check the status of an import job.

        Args:
            import_id: The ID of the import job to check.

        Returns:
            Status string. Possible values:
            - 'UPLOADING': Data is being uploaded (initial state)
            - 'IN_QUEUE': Import is queued for processing
            - 'VALIDATING': Data is being validated
            - 'IMPORTING': Validated data is being imported
            - 'ERRORS_READY_FOR_REVIEW': Errors found, review required
            - 'WARNINGS_READY_FOR_REVIEW': Warnings found, review recommended
            - 'ERRORS_AND_WARNINGS_READY_FOR_REVIEW': Both errors and warnings found
            - 'DRY_RUN_SUCCESSFUL': Dry run completed successfully
            - 'IMPORT_SUCCESSFUL': Import completed successfully
            - 'VALIDATION_FAILED': Validation failed due to unknown error
            - 'IMPORT_FAILED': Import failed due to unknown error
        """
        response = self._get(f"/imports/{import_id}")
        data = response.json()
        status = data.get("data", {}).get("attributes", {}).get("status", "UNKNOWN_STATUS")
        logger.debug(f"Import {import_id} status: {status}")
        return status

    def get_import_results(self, import_id: str) -> Dict[str, Any]:
        """
        Get the results of a completed import job.

        Args:
            import_id: The ID of the completed import job.

        Returns:
            Dictionary with keys:
            - 'digests': List of summary strings (e.g., ["1 attribute will be created"])
            - 'warnings': List of warning objects with 'message', 'type', 'affected_members'
            - 'errors': List of error objects with 'message', 'type', 'affected_members'
        """
        logger.debug(f"Fetching results for import {import_id}")
        response = self._get(f"/import_results/{import_id}")
        data = response.json()
        attributes = data.get("data", {}).get("attributes", {})

        return {
            "digests": attributes.get("digests", []),
            "warnings": attributes.get("warnings", []),
            "errors": attributes.get("errors", []),
        }

    # =========================================================================
    # Tier 2: Orchestration Methods
    # =========================================================================

    def execute_import(
            self,
            import_dataframe: pd.DataFrame,
            import_type: AddeparImportType,
            *,
            is_dry_run: bool = True,
            ignore_warnings: bool = False,
            initial_wait: float = DEFAULT_INITIAL_WAIT,
            max_wait: float = DEFAULT_MAX_WAIT,
            backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
            timeout: float = DEFAULT_TIMEOUT,
        ) -> Dict[str, Any]:
        """
        Submit an import, poll for completion, and fetch results.

        This is a convenience method that combines create_import(), polling with
        get_import_status(), and get_import_results() into a single call.

        Args:
            import_dataframe: Pandas DataFrame containing data to import.
            import_type: Type of data being imported.
            is_dry_run: If True, performs validation without saving (default: True).
            ignore_warnings: If True, proceed despite warnings (default: False).
            initial_wait: Initial polling interval in seconds (default: 30).
            max_wait: Maximum polling interval in seconds (default: 300).
            backoff_factor: Multiplier for exponential backoff (default: 1.5).
            timeout: Maximum time to wait for completion (default: 1200).

        Returns:
            Dictionary with 'digests', 'warnings', and 'errors' keys.

        Raises:
            ValidationError: If import_type is invalid.
            AddePyError: If import fails or doesn't complete successfully.
            AddePyTimeoutError: If import doesn't complete within timeout.
        """
        # Step 1: Submit the import (Tier 1)
        import_id = self.create_import(
            import_dataframe=import_dataframe,
            import_type=import_type,
            is_dry_run=is_dry_run,
            ignore_warnings=ignore_warnings,
        )
        logger.info(f"Polling import {import_id} for completion...")

        # Step 2: Poll for completion
        def check_status(iid: str) -> str:
            return self.get_import_status(iid)

        def is_complete(status: str) -> bool:
            return status in IMPORT_COMPLETED_STATUSES

        final_status = self._poll_until_complete(
            job_id=import_id,
            check_status_fn=check_status,
            is_complete_fn=is_complete,
            initial_wait=initial_wait,
            max_wait=max_wait,
            backoff_factor=backoff_factor,
            timeout=timeout,
            job_type="import",
        )

        # Step 3: Verify success and fetch results
        if final_status not in IMPORT_RESULT_READY_STATUSES:
            raise AddePyError(f"Import {import_id} failed with status: {final_status}")

        logger.info(f"Import {import_id} completed with status: {final_status}")
        return self.get_import_results(import_id)
