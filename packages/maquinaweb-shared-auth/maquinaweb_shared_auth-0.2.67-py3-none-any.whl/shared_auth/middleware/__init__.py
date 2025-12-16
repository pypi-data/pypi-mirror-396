"""
Middlewares para autenticação compartilhada
"""

# Re-export all middlewares
from .auth import RequireAuthMiddleware, SharedAuthMiddleware
from .organization import OrganizationMiddleware, get_member
from .payment import PaymentVerificationMiddleware

__all__ = [
    # Auth
    "SharedAuthMiddleware",
    "RequireAuthMiddleware",
    # Organization
    "OrganizationMiddleware",
    "get_member",
    # Payment
    "PaymentVerificationMiddleware",
]
