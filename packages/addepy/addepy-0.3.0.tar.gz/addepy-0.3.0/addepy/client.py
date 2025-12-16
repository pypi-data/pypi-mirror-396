"""Main Addepar API client."""
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

import requests
from dotenv import load_dotenv

from .constants import DEFAULT_CONTENT_TYPE
from .exceptions import (
    AddePyError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    GoneError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

if TYPE_CHECKING:
    from .resources.admin import AdminNamespace
    from .resources.ownership import OwnershipNamespace
    from .resources.portfolio import PortfolioNamespace


class AddePy:
    """
    Main client for interacting with the Addepar API.

    Usage:
        client = AddePy()  # Uses env vars
        client = AddePy(firm_name="acme", firm_id="123", api_key="xxx")

        # Access resources
        client.portfolio.jobs.create_job(...)
        client.admin.import_tool.create_import(...)

        # Context manager support
        with AddePy() as client:
            client.portfolio.jobs.create_job(...)
    """

    def __init__(
            self,
            firm_name: Optional[str] = None,
            firm_id: Optional[str] = None,
            api_key: Optional[str] = None,
            load_env: bool = True,
        ) -> None:
        """
        Initialize the Addepar client.

        Args:
            firm_name: Addepar firm name (or set ADDEPAR_FIRM_NAME env var)
            firm_id: Addepar firm ID (or set ADDEPAR_FIRM_ID env var)
            api_key: Base64-encoded API key (or set ADDEPAR_API_KEY env var)
            load_env: Whether to load environment variables from .env file
        """
        if load_env:
            load_dotenv()

        self._firm_name = firm_name or os.getenv("ADDEPAR_FIRM_NAME")
        self._firm_id = firm_id or os.getenv("ADDEPAR_FIRM_ID")
        self._api_key = api_key or os.getenv("ADDEPAR_API_KEY")

        # Validate required configuration
        if not all([self._firm_name, self._firm_id, self._api_key]):
            missing = []
            if not self._firm_name:
                missing.append("firm_name/ADDEPAR_FIRM_NAME")
            if not self._firm_id:
                missing.append("firm_id/ADDEPAR_FIRM_ID")
            if not self._api_key:
                missing.append("api_key/ADDEPAR_API_KEY")
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        self._base_url = f"https://{self._firm_name}.addepar.com/api/v1"

        # Create session for connection pooling
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Content-Type": DEFAULT_CONTENT_TYPE,
                "Addepar-Firm": self._firm_id,
                "Authorization": f"Basic {self._api_key}",
            }
        )

        # Lazy-loaded namespaces
        self._portfolio: Optional["PortfolioNamespace"] = None
        self._admin: Optional["AdminNamespace"] = None
        self._ownership: Optional["OwnershipNamespace"] = None

    @property
    def portfolio(self) -> "PortfolioNamespace":
        """Access portfolio resources (jobs, etc.)."""
        if self._portfolio is None:
            from .resources.portfolio import PortfolioNamespace

            self._portfolio = PortfolioNamespace(self)
        return self._portfolio

    @property
    def admin(self) -> "AdminNamespace":
        """Access admin resources (import_tool, etc.)."""
        if self._admin is None:
            from .resources.admin import AdminNamespace

            self._admin = AdminNamespace(self)
        return self._admin

    @property
    def ownership(self) -> "OwnershipNamespace":
        """Access ownership resources (entities, groups, etc.)."""
        if self._ownership is None:
            from .resources.ownership import OwnershipNamespace

            self._ownership = OwnershipNamespace(self)
        return self._ownership

    def _request(
            self,
            method: str,
            endpoint: str,
            *,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[str] = None,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs: Any,
        ) -> requests.Response:
        """
        Make an HTTP request to the Addepar API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., "/jobs", "/imports")
            json: JSON body (for application/vnd.api+json)
            data: Raw body data (for text/plain, like CSV)
            params: Query parameters
            headers: Additional headers (merged with session headers)
            **kwargs: Additional arguments passed to requests

        Returns:
            requests.Response object

        Raises:
            AuthenticationError: On 401 responses
            RateLimitError: On 429 responses
            ValidationError: On 400/422 responses
            NotFoundError: On 404 responses
            AddePyError: On other error responses
        """
        url = f"{self._base_url}{endpoint}"

        response = self._session.request(
            method=method,
            url=url,
            json=json,
            data=data,
            params=params,
            headers=headers,
            **kwargs,
        )

        # Handle error responses
        if not response.ok:
            self._handle_error_response(response)

        return response

    def _handle_error_response(self, response: requests.Response) -> None:
        """Raise appropriate exception based on response status code."""
        status = response.status_code
        try:
            error_data = response.json()
            message = str(error_data)
        except Exception:
            message = response.text or f"HTTP {status} error"

        if status == 401:
            raise AuthenticationError(message, response)
        elif status == 403:
            raise ForbiddenError(message, response)
        elif status == 404:
            raise NotFoundError(message, response)
        elif status == 409:
            raise ConflictError(message, response)
        elif status == 410:
            raise GoneError(message, response)
        elif status == 429:
            retry_after = response.headers.get("X-RateLimit-Retry-After")
            raise RateLimitError(
                message,
                response,
                retry_after=int(retry_after) if retry_after else None,
            )
        elif status in (400, 422):
            raise ValidationError(message, response)
        else:
            raise AddePyError(message, response)

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()

    def __enter__(self) -> "AddePy":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        self.close()
