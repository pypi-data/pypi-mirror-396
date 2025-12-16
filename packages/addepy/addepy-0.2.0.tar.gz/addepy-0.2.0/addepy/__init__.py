"""
Addepy - Python SDK for the Addepar API.

Usage:
    from addepy import AddePy

    client = AddePy()

    # Portfolio jobs
    job_id = client.portfolio.jobs.create_job(query_dict)
    results = client.portfolio.jobs.execute_portfolio_query(query_dict)

    # Import tool
    import_id = client.admin.import_tool.create_import(df, 'TRANSACTIONS')
    results = client.admin.import_tool.execute_import(df, 'TRANSACTIONS')

Logging:
    import logging
    logging.getLogger("addepy").setLevel(logging.DEBUG)
    logging.getLogger("addepy").addHandler(logging.StreamHandler())
"""
import logging

from .client import AddePy
from .exceptions import (
    AddePyError,
    AddePyTimeoutError,
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    GoneError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

# Create logger for the package
logger = logging.getLogger("addepy")
logger.addHandler(logging.NullHandler())  # Prevent "no handler" warnings

__version__ = "0.2.0"

__all__ = [
    "AddePy",
    "AddePyError",
    "AddePyTimeoutError",
    "AuthenticationError",
    "ConflictError",
    "ForbiddenError",
    "GoneError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
]
