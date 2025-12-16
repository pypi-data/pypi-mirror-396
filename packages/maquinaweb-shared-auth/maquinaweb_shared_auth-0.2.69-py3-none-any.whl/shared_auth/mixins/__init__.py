"""
Mixins para facilitar a criação de models com referências ao sistema de auth
"""

# Re-export all mixins from submodules
from .common import OrganizationUserMixin, TimestampedMixin
from .contact import ContactMixin
from .organization import (
    LoggedOrganizationMixin,
    LoggedOrganizationPermMixin,
    OrganizationMixin,
    PrefetchOrganizationsMixin,
)
from .permission import RequirePermissionMixin
from .user import UserMixin

__all__ = [
    # Organization
    "OrganizationMixin",
    "LoggedOrganizationPermMixin",
    "LoggedOrganizationMixin",
    "PrefetchOrganizationsMixin",
    # User
    "UserMixin",
    # Common
    "OrganizationUserMixin",
    "TimestampedMixin",
    # Permission
    "RequirePermissionMixin",
    # Contact
    "ContactMixin",
]
