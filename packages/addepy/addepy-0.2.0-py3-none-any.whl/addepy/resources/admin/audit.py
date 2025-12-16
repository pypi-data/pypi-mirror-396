"""Audit resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")

# Valid object types for audit queries
AUDIT_OBJECT_TYPES = {"login_attempt", "attribute", "transaction", "permission"}

# Valid user types
AUDIT_USER_TYPES = {"firmusers", "addeparusers", "anyone", "custom"}

# Valid actions (for attribute, transaction, permission queries)
AUDIT_ACTIONS = {"Add", "Modify", "Remove"}


class AuditResource(BaseResource):
    """
    Resource for Addepar Audit API.

    Audit logs track changes to attribute values, transactions, reports,
    and user roles/permissions. Each entry represents an addition,
    modification, or deletion.

    Methods:
        - get_audit_entry() - Get a specific audit log entry by ID
        - query_login_attempts() - Query login attempts
        - query_attribute_changes() - Query attribute value changes
        - query_transaction_changes() - Query transaction/snapshot/valuation changes
        - query_permission_changes() - Query role/permission changes
    """

    def _query_audit_logs(
        self,
        object_type: str,
        start_date: str,
        end_date: str,
        *,
        actions: Optional[List[str]] = None,
        user_type: Optional[str] = None,
        users: Optional[List[str]] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Internal method to query audit logs with pagination.

        Args:
            object_type: Type of audit log (login_attempt, attribute, transaction, permission).
            start_date: Start date (YYYY-MM-DD or ISO 8601 with timezone).
            end_date: End date (YYYY-MM-DD or ISO 8601 with timezone).
            actions: Filter by action types (Add, Modify, Remove).
            user_type: Who to include (firmusers, addeparusers, anyone, custom).
            users: List of user IDs (when user_type="custom").
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of audit log entries.
        """
        attributes: Dict[str, Any] = {
            "object_type": object_type,
            "start_date": start_date,
            "end_date": end_date,
        }

        if actions is not None:
            attributes["actions"] = actions
        if user_type is not None:
            attributes["user_type"] = user_type
        if users is not None:
            attributes["users"] = users

        payload = {
            "data": {
                "type": "audit_trail",
                "attributes": attributes,
            }
        }

        # Initial POST request
        params = {"page[limit]": page_limit}
        response = self._post("/audit_trail", json=payload, params=params)
        data = response.json()

        results = data.get("data", [])
        next_link = data.get("links", {}).get("next")

        # Follow pagination links (subsequent requests are GET)
        while next_link:
            response = self._client._session.get(
                f"{self._client._base_url}{next_link}",
                headers=self._client._headers,
            )
            response.raise_for_status()
            data = response.json()
            results.extend(data.get("data", []))
            next_link = data.get("links", {}).get("next")

        return results

    # =========================================================================
    # Public Methods
    # =========================================================================

    def get_audit_entry(self, entry_id: str) -> Dict[str, Any]:
        """
        Get a specific audit log entry by ID.

        Args:
            entry_id: The ID of the audit log entry.

        Returns:
            The audit log entry resource object.
        """
        response = self._get(f"/audit_trail/{entry_id}")
        data = response.json()
        entry = data.get("data", {})
        logger.debug(f"Retrieved audit entry {entry_id}")
        return entry

    def query_login_attempts(
        self,
        start_date: str,
        end_date: str,
        *,
        user_type: Optional[str] = None,
        users: Optional[List[str]] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Query login attempts.

        Retrieves a list of attempts by users to sign into the application,
        Help Center, or Client Portal using Addepar credentials, SSO,
        or two-factor authentication.

        Args:
            start_date: Start date (YYYY-MM-DD or ISO 8601 with timezone).
            end_date: End date (YYYY-MM-DD or ISO 8601 with timezone).
            user_type: Who to include (firmusers, addeparusers, anyone, custom).
            users: List of user IDs (when user_type="custom").
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of login attempt audit entries.

        Example:
            attempts = client.admin.audit.query_login_attempts(
                start_date="2021-03-26",
                end_date="2021-03-30"
            )
        """
        results = self._query_audit_logs(
            object_type="login_attempt",
            start_date=start_date,
            end_date=end_date,
            user_type=user_type,
            users=users,
            page_limit=page_limit,
        )
        logger.debug(f"Queried {len(results)} login attempts")
        return results

    def query_attribute_changes(
        self,
        start_date: str,
        end_date: str,
        *,
        actions: Optional[List[str]] = None,
        user_type: Optional[str] = None,
        users: Optional[List[str]] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Query attribute value changes.

        Retrieves a list of user changes to attribute values applied at
        the asset- and position-level.

        Args:
            start_date: Start date (YYYY-MM-DD or ISO 8601 with timezone).
            end_date: End date (YYYY-MM-DD or ISO 8601 with timezone).
            actions: Filter by action types ("Add", "Modify", "Remove").
            user_type: Who to include (firmusers, addeparusers, anyone, custom).
            users: List of user IDs (when user_type="custom").
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of attribute change audit entries.

        Example:
            changes = client.admin.audit.query_attribute_changes(
                start_date="2021-02-01",
                end_date="2021-02-28",
                actions=["Add", "Modify"]
            )
        """
        results = self._query_audit_logs(
            object_type="attribute",
            start_date=start_date,
            end_date=end_date,
            actions=actions,
            user_type=user_type,
            users=users,
            page_limit=page_limit,
        )
        logger.debug(f"Queried {len(results)} attribute changes")
        return results

    def query_transaction_changes(
        self,
        start_date: str,
        end_date: str,
        *,
        actions: Optional[List[str]] = None,
        user_type: Optional[str] = None,
        users: Optional[List[str]] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Query transaction, snapshot, and valuation changes.

        Retrieves a list of user changes to transactions, snapshots,
        and valuations.

        Args:
            start_date: Start date (YYYY-MM-DD or ISO 8601 with timezone).
            end_date: End date (YYYY-MM-DD or ISO 8601 with timezone).
            actions: Filter by action types ("Add", "Modify", "Remove").
            user_type: Who to include (firmusers, addeparusers, anyone, custom).
            users: List of user IDs (when user_type="custom").
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of transaction/snapshot/valuation change audit entries.

        Example:
            changes = client.admin.audit.query_transaction_changes(
                start_date="2021-03-15",
                end_date="2021-04-30",
                actions=["Modify"]
            )
        """
        results = self._query_audit_logs(
            object_type="transaction",
            start_date=start_date,
            end_date=end_date,
            actions=actions,
            user_type=user_type,
            users=users,
            page_limit=page_limit,
        )
        logger.debug(f"Queried {len(results)} transaction changes")
        return results

    def query_permission_changes(
        self,
        start_date: str,
        end_date: str,
        *,
        actions: Optional[List[str]] = None,
        user_type: Optional[str] = None,
        users: Optional[List[str]] = None,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        Query role and permission changes.

        Retrieves a list of user changes to roles and user permissions.

        Args:
            start_date: Start date (YYYY-MM-DD or ISO 8601 with timezone).
            end_date: End date (YYYY-MM-DD or ISO 8601 with timezone).
            actions: Filter by action types ("Add", "Modify", "Remove").
            user_type: Who to include (firmusers, addeparusers, anyone, custom).
            users: List of user IDs (when user_type="custom").
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of permission change audit entries.

        Example:
            changes = client.admin.audit.query_permission_changes(
                start_date="2021-03-15",
                end_date="2021-03-30",
                user_type="custom",
                users=["627858", "826728"]
            )
        """
        results = self._query_audit_logs(
            object_type="permission",
            start_date=start_date,
            end_date=end_date,
            actions=actions,
            user_type=user_type,
            users=users,
            page_limit=page_limit,
        )
        logger.debug(f"Queried {len(results)} permission changes")
        return results
