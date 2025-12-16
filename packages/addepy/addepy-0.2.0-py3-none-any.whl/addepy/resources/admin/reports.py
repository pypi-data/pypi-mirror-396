"""Reports resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class ReportsResource(BaseResource):
    """
    Resource for Addepar Reports APIs.

    Manage reports in Addepar, including listing report definitions,
    running reports, and accessing generated report results.

    Report List Methods:
        - list_reports() - List available report definitions

    Report Generation Methods:
        - create_report_generation_job() - Run a report for portfolios

    Generated Reports Methods:
        - get_generated_report() - Get completed report by job ID
        - list_generated_reports() - List all completed reports
        - get_report_creator() - Get user who ran the report
        - get_zipped_file() - Get zip file metadata
        - download_zipped_file() - Download zip binary
    """

    # =========================================================================
    # Report List Methods
    # =========================================================================

    def list_reports(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
        modified_after: Optional[str] = None,
        modified_before: Optional[str] = None,
        name: Optional[str] = None,
        entity_id: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all report definitions with optional filters.

        Args:
            page_limit: Results per page (default: 500, max: 2000).
            created_after: Reports created after timestamp (ISO 8601).
            created_before: Reports created before timestamp (ISO 8601).
            modified_after: Reports modified after timestamp (ISO 8601).
            modified_before: Reports modified before timestamp (ISO 8601).
            name: Filter by report name (substring match).
            entity_id: Filter by associated entity ID.
            group_id: Filter by associated group ID.

        Returns:
            List of report resource objects containing id, type, and attributes
            (report_id, report_name, created_on_date, last_update_date,
            num_associated_portfolios).
        """
        params: Dict[str, Any] = {}

        if created_after is not None:
            params["filter[createdAfter]"] = created_after
        if created_before is not None:
            params["filter[createdBefore]"] = created_before
        if modified_after is not None:
            params["filter[modifiedAfter]"] = modified_after
        if modified_before is not None:
            params["filter[modifiedBefore]"] = modified_before
        if name is not None:
            params["filter[name]"] = name
        if entity_id is not None:
            params["filter[entityId]"] = entity_id
        if group_id is not None:
            params["filter[groupId]"] = group_id

        reports = list(
            self._paginate("/reports", page_limit=page_limit, params=params if params else None)
        )
        logger.debug(f"Listed {len(reports)} reports")
        return reports

    # =========================================================================
    # Report Generation Methods
    # =========================================================================

    def create_report_generation_job(
        self,
        report_id: str,
        portfolios: List[Dict[str, str]],
        start_date: str,
        end_date: str,
        *,
        portal_publishing: Optional[str] = None,
        contact_notification: Optional[str] = None,
        label: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Run a report for the specified portfolios.

        Args:
            report_id: The ID of the report to run.
            portfolios: List of portfolios to run the report for. Each portfolio
                should be a dict with 'portfolio_type' ("entity" or "group") and
                'portfolio_id' (string ID).
            start_date: Report start date (YYYY-MM-DD format).
            end_date: Report end date (YYYY-MM-DD format).
            portal_publishing: Optional publishing preference - "PUBLISH",
                "DO_NOT_PUBLISH", or "USE_CONTACT_PREFERENCE".
            contact_notification: Optional notification preference - "NOTIFY",
                "DO_NOT_NOTIFY", or "USE_CONTACT_PREFERENCE".
            label: Optional list of label IDs to attach to generated PDFs.

        Returns:
            Job resource object containing the job ID for tracking.

        Example:
            job = client.admin.reports.create_report_generation_job(
                report_id="42",
                portfolios=[
                    {"portfolio_type": "entity", "portfolio_id": "22"},
                    {"portfolio_type": "group", "portfolio_id": "3"}
                ],
                start_date="2024-01-01",
                end_date="2024-03-31",
                portal_publishing="PUBLISH",
                contact_notification="NOTIFY"
            )
        """
        attributes: Dict[str, Any] = {
            "report_id": report_id,
            "portfolios": portfolios,
            "start_date": start_date,
            "end_date": end_date,
        }

        if portal_publishing is not None:
            attributes["portal_publishing"] = portal_publishing
        if contact_notification is not None:
            attributes["contact_notification"] = contact_notification
        if label is not None:
            attributes["label"] = label

        payload = {
            "data": {
                "type": "report_generation_job",
                "attributes": attributes,
            }
        }

        response = self._post("/report_generation_job", json=payload)
        data = response.json()
        job = data.get("data", {})
        job_id = job.get("id", "unknown")
        logger.info(f"Created report generation job: {job_id}")
        return job

    # =========================================================================
    # Generated Reports Methods
    # =========================================================================

    def get_generated_report(self, job_id: str) -> Dict[str, Any]:
        """
        Get a generated report by job ID.

        Args:
            job_id: The ID of the report generation job.

        Returns:
            Generated report resource object containing id, type, attributes
            (report_id, report_name, status, started_at, completed_at, job_type,
            generated_portfolios, failed_portfolios), and relationships.
        """
        response = self._get(f"/generated_reports/{job_id}")
        data = response.json()
        report = data.get("data", {})
        logger.debug(f"Retrieved generated report {job_id}")
        return report

    def list_generated_reports(
        self,
        *,
        page_size: int = 50,
        completed_after: Optional[str] = None,
        completed_before: Optional[str] = None,
        status: Optional[str] = None,
        entity_id: Optional[str] = None,
        group_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all generated reports with optional filters.

        Args:
            page_size: Results per page (default: 50).
            completed_after: Reports completed after timestamp (ISO 8601).
            completed_before: Reports completed before timestamp (ISO 8601).
            status: Filter by status - comma-separated list of "FINISHED",
                "ERROR", and/or "CANCELED".
            entity_id: Filter by portfolio entity ID.
            group_id: Filter by portfolio group ID.

        Returns:
            List of generated report resource objects sorted in reverse
            chronological order of completion time.
        """
        params: Dict[str, Any] = {}

        if completed_after is not None:
            params["filter[completed_after]"] = completed_after
        if completed_before is not None:
            params["filter[completed_before]"] = completed_before
        if status is not None:
            params["filter[status]"] = status
        if entity_id is not None:
            params["filter[entityId]"] = entity_id
        if group_id is not None:
            params["filter[groupId]"] = group_id

        reports = list(
            self._paginate_offset(
                "/generated_reports", page_size=page_size, params=params if params else None
            )
        )
        logger.debug(f"Listed {len(reports)} generated reports")
        return reports

    def get_report_creator(self, job_id: str) -> Dict[str, Any]:
        """
        Get the user who created the report generation job.

        Args:
            job_id: The ID of the report generation job.

        Returns:
            User resource object containing id, type, attributes
            (first_name, last_name, email, etc.), and relationships.
        """
        response = self._get(f"/generated_reports/{job_id}/creator")
        data = response.json()
        creator = data.get("data", {})
        logger.debug(f"Retrieved creator for generated report {job_id}")
        return creator

    def get_zipped_file(self, job_id: str) -> Dict[str, Any]:
        """
        Get the zipped file metadata for a generated report.

        Args:
            job_id: The ID of the report generation job.

        Returns:
            File resource object containing id, type, attributes
            (content_type, bytes, name, created_at), and relationships.
        """
        response = self._get(f"/generated_reports/{job_id}/zipped_file")
        data = response.json()
        file = data.get("data", {})
        logger.debug(f"Retrieved zipped file metadata for job {job_id}")
        return file

    def download_zipped_file(self, job_id: str) -> bytes:
        """
        Download the zipped report file.

        Args:
            job_id: The ID of the report generation job.

        Returns:
            Raw binary content of the zip file.
        """
        response = self._get(f"/generated_reports/{job_id}/zipped_file/download")
        logger.debug(f"Downloaded zipped file for job {job_id}")
        return response.content
