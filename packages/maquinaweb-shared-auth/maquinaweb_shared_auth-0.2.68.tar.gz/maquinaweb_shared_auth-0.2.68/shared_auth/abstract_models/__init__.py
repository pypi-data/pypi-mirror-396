"""
Abstract models para customização
Estes models podem ser herdados nos apps clientes para adicionar campos e métodos customizados
"""

# Re-export all abstract models from submodules
from .contact import AbstractContact, AbstractEmail, AbstractMessage, AbstractPhone
from .member import AbstractSharedMember
from .organization import (
    AbstractOrganizationGroup,
    AbstractSharedOrganization,
    organization_image_path,
)
from .permission import (
    AbstractGroupOrganizationPermissions,
    AbstractGroupPermissions,
    AbstractMemberSystemGroup,
    AbstractPermission,
)
from .pivot import (
    GroupOrgPermissionsPermission,
    GroupPermissionsPermission,
    PlanGroupPermission,
)
from .plan import AbstractPlan, AbstractSubscription, AbstractSystem
from .token import AbstractSharedToken
from .user import AbstractUser

__all__ = [
    # Token
    "AbstractSharedToken",
    # Organization
    "AbstractSharedOrganization",
    "AbstractOrganizationGroup",
    "organization_image_path",
    # User
    "AbstractUser",
    # Member
    "AbstractSharedMember",
    # Permission
    "AbstractPermission",
    "AbstractGroupPermissions",
    "AbstractGroupOrganizationPermissions",
    "AbstractMemberSystemGroup",
    # Plan
    "AbstractSystem",
    "AbstractPlan",
    "AbstractSubscription",
    # Contact
    "AbstractContact",
    "AbstractEmail",
    "AbstractPhone",
    "AbstractMessage",
    # Pivot
    "GroupPermissionsPermission",
    "PlanGroupPermission",
    "GroupOrgPermissionsPermission",
]
