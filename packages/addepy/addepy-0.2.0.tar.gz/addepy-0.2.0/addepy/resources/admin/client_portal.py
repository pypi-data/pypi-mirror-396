"""Client Portal resource for the Addepar API."""
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseResource

logger = logging.getLogger("addepy")


class ClientPortalResource(BaseResource):
    """
    Resource for Addepar Client Portal API.

    Publish files to the Client Portal and optionally notify contacts.

    Methods:
        - publish_files() - Publish files to client portal
    """

    def publish_files(
        self,
        files_id: List[int],
        portal_publishing: str,
        contact_notification: str,
        *,
        publish_override_contact_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Publish files to the Client Portal.

        Args:
            files_id: List of file IDs to publish (max 500).
            portal_publishing: Publishing scope. One of:
                - "do_not_publish" - Do not publish to portal
                - "use_contact_preference" - Use each contact's preference
                - "publish" - Publish to all contacts
            contact_notification: Notification scope. One of:
                - "do_not_notify" - Do not send email notifications
                - "use_contact_preference" - Use each contact's preference
                - "notify" - Notify all contacts
            publish_override_contact_ids: Optional list of contact IDs that will
                always have files published, regardless of portal_publishing value.

        Returns:
            List of publish result objects containing:
            - file_id: The file ID
            - publish_status: "success" or "fail"
            - notify_status: "success" or "fail"
            - error: List of error objects (if any failures)

        Note:
            The API returns 200 even on partial failures. Check publish_status
            and notify_status in the response to determine actual results.

        Example:
            results = client.admin.client_portal.publish_files(
                files_id=[37, 38, 39],
                portal_publishing="publish",
                contact_notification="notify"
            )

            # With override contacts
            results = client.admin.client_portal.publish_files(
                files_id=[37],
                portal_publishing="use_contact_preference",
                contact_notification="do_not_notify",
                publish_override_contact_ids=[23, 25]
            )
        """
        attributes: Dict[str, Any] = {
            "files_id": files_id,
            "portal_publishing": portal_publishing.upper(),
            "contact_notification": contact_notification.upper(),
        }

        if publish_override_contact_ids is not None:
            attributes["publish_override_contact_ids"] = publish_override_contact_ids

        payload = {
            "data": {
                "type": "publish_portal_files_request",
                "attributes": attributes,
            }
        }

        response = self._post("/portal/publish_files", json=payload)
        data = response.json()
        results = data.get("data", [])
        logger.info(f"Published {len(files_id)} files to client portal")
        return results
