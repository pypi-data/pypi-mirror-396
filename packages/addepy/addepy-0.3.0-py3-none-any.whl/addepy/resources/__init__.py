"""Resource namespaces for the Addepy SDK."""
from .admin import AdminNamespace
from .ownership import OwnershipNamespace
from .portfolio import PortfolioNamespace

__all__ = [
    "PortfolioNamespace",
    "AdminNamespace",
    "OwnershipNamespace",
]
