"""
Managers customizados para os models compartilhados
"""

# Re-export all managers from submodules
from .base import (
    BaseAuthManager,
    OrganizationQuerySetMixin,
    OrganizationUserQuerySetMixin,
    UserQuerySetMixin,
)
from .member import SharedMemberManager
from .organization import SharedOrganizationManager
from .permission import (
    GroupOrganizationPermissionsManager,
    MemberSystemGroupManager,
    PermissionManager,
)
from .plan import SubscriptionManager, SystemManager
from .user import UserManager

__all__ = [
    # Base
    "BaseAuthManager",
    "OrganizationQuerySetMixin",
    "UserQuerySetMixin",
    "OrganizationUserQuerySetMixin",
    # Organization
    "SharedOrganizationManager",
    # User
    "UserManager",
    # Member
    "SharedMemberManager",
    # Permission
    "PermissionManager",
    "GroupOrganizationPermissionsManager",
    "MemberSystemGroupManager",
    # Plan
    "SystemManager",
    "SubscriptionManager",
]
