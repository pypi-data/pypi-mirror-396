"""Arguments resource for the Addepar API."""
import logging
from typing import Any, Dict, List

from ..base import BaseResource

logger = logging.getLogger("addepy")


class ArgumentsResource(BaseResource):
    """
    Resource for Addepar Arguments API.

    Arguments are possible settings that can be applied to each instance
    of an attribute. Use this API in conjunction with the Attributes API
    to discover available attribute arguments for Portfolio Query requests.

    Methods:
        - get_argument() - Get a single argument
        - list_arguments() - List all arguments
    """

    def get_argument(self, argument_id: str) -> Dict[str, Any]:
        """
        Get an argument by ID.

        Args:
            argument_id: The argument ID (e.g., "period", "currency").

        Returns:
            Argument resource object containing id, type, and attributes
            (values, default_value, arg_type).

        Example:
            arg = client.portfolio.arguments.get_argument("cost_basis_type")
            print(f"Values: {arg['attributes']['values']}")
            print(f"Default: {arg['attributes']['default_value']}")
        """
        response = self._get(f"/arguments/{argument_id}")
        data = response.json()
        result = data.get("data", {})
        logger.debug(f"Retrieved argument: {argument_id}")
        return result

    def list_arguments(self) -> List[Dict[str, Any]]:
        """
        List all attribute arguments.

        Returns:
            List of argument resource objects containing id, type, and
            attributes (values, default_value, arg_type).

        Example:
            args = client.portfolio.arguments.list_arguments()
            for arg in args:
                print(f"{arg['id']}: {arg['attributes'].get('arg_type', 'N/A')}")
        """
        response = self._get("/arguments")
        data = response.json()
        results = data.get("data", [])
        logger.debug(f"Listed {len(results)} arguments")
        return results
