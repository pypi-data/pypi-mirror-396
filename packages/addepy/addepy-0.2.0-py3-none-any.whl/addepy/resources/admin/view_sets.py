"""View Sets resource for the Addepar API."""
import logging
from typing import Any, Dict, List

from ...constants import DEFAULT_PAGE_LIMIT
from ..base import BaseResource

logger = logging.getLogger("addepy")


class ViewSetsResource(BaseResource):
    """
    Resource for Addepar View Sets API.

    View sets are groups of views that determine what contacts see in the
    Client Portal. This is a read-only API.

    Methods:
        - get_view_set() - Get a single view set
        - list_view_sets() - List all view sets
    """

    def get_view_set(self, view_set_id: str) -> Dict[str, Any]:
        """
        Get a view set by ID.

        Args:
            view_set_id: The ID of the view set.

        Returns:
            View set resource object containing id, type, and attributes
            (name, views). The views attribute is a list of view objects
            with id, name, and type.

        Example:
            view_set = client.admin.view_sets.get_view_set(view_set_id="2000")
            print(view_set["attributes"]["name"])
            for view in view_set["attributes"]["views"]:
                print(f"  {view['name']} ({view['type']})")
        """
        response = self._get(f"/view_sets/{view_set_id}")
        data = response.json()
        view_set = data.get("data", {})
        logger.debug(f"Retrieved view set {view_set_id}")
        return view_set

    def list_view_sets(
        self,
        *,
        page_limit: int = DEFAULT_PAGE_LIMIT,
    ) -> List[Dict[str, Any]]:
        """
        List all view sets.

        Args:
            page_limit: Results per page (default: 500, max: 2000).

        Returns:
            List of view set resource objects containing id, type, and
            attributes (name, views).

        Example:
            view_sets = client.admin.view_sets.list_view_sets()
            for vs in view_sets:
                print(f"{vs['id']}: {vs['attributes']['name']}")
        """
        view_sets = list(self._paginate("/view_sets", page_limit=page_limit))
        logger.debug(f"Listed {len(view_sets)} view sets")
        return view_sets
