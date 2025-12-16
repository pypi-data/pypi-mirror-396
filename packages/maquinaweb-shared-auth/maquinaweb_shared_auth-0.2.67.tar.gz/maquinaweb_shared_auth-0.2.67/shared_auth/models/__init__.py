"""
Models READ-ONLY para acesso aos dados de autenticação
ATENÇÃO: Estes models NÃO devem ser usados para criar migrations

Para customizar estes models, herde dos models abstratos em shared_auth.abstract_models
e configure no settings.py. Veja a documentação em abstract_models.py
"""

# Re-export all models from submodules
from .contact import Contact, Email, Message, Phone
from .member import SharedMember
from .organization import OrganizationGroup, SharedOrganization
from .permission import (
    GroupOrganizationPermissions,
    GroupPermissions,
    MemberSystemGroup,
    Permission,
)
from .plan import Plan, Subscription, System
from .token import SharedToken
from .user import User

__all__ = [
    # Token
    "SharedToken",
    # Organization
    "SharedOrganization",
    "OrganizationGroup",
    # User
    "User",
    # Member
    "SharedMember",
    # Permission
    "Permission",
    "GroupPermissions",
    "GroupOrganizationPermissions",
    "MemberSystemGroup",
    # Plan
    "System",
    "Plan",
    "Subscription",
    # Contact
    "Contact",
    "Email",
    "Phone",
    "Message",
]
