"""
Models concretos para Permission, GroupPermissions, GroupOrganizationPermissions e MemberSystemGroup
"""

from shared_auth.abstract_models.permission import (
    AbstractGroupOrganizationPermissions,
    AbstractGroupPermissions,
    AbstractMemberSystemGroup,
    AbstractPermission,
)
from shared_auth.conf import (
    GROUP_ORG_PERMISSIONS_TABLE,
    GROUP_PERMISSIONS_TABLE,
    MEMBER_SYSTEM_GROUP_TABLE,
    PERMISSION_TABLE,
)
from shared_auth.managers.permission import (
    GroupOrganizationPermissionsManager,
    MemberSystemGroupManager,
    PermissionManager,
)


class Permission(AbstractPermission):
    """
    Model READ-ONLY padrão da tabela organization_permissions
    Define permissões específicas de cada sistema

    Para customizar, crie seu próprio model herdando de AbstractPermission
    """

    objects = PermissionManager()

    class Meta(AbstractPermission.Meta):
        db_table = PERMISSION_TABLE


class GroupPermissions(AbstractGroupPermissions):
    """
    Model READ-ONLY padrão da tabela organization_grouppermissions
    Grupos base de permissões (usados nos planos)

    Para customizar, crie seu próprio model herdando de AbstractGroupPermissions
    """

    class Meta(AbstractGroupPermissions.Meta):
        db_table = GROUP_PERMISSIONS_TABLE


class GroupOrganizationPermissions(AbstractGroupOrganizationPermissions):
    """
    Model READ-ONLY padrão da tabela organization_grouporganizationpermissions
    Grupos de permissões criados pela organização para distribuir aos usuários

    Para customizar, crie seu próprio model herdando de AbstractGroupOrganizationPermissions
    """

    objects = GroupOrganizationPermissionsManager()

    class Meta(AbstractGroupOrganizationPermissions.Meta):
        db_table = GROUP_ORG_PERMISSIONS_TABLE


class MemberSystemGroup(AbstractMemberSystemGroup):
    """
    Model READ-ONLY padrão da tabela organization_membersystemgroup
    Relaciona um membro a um grupo de permissões em um sistema específico

    Para customizar, crie seu próprio model herdando de AbstractMemberSystemGroup
    """

    objects = MemberSystemGroupManager()

    class Meta(AbstractMemberSystemGroup.Meta):
        db_table = MEMBER_SYSTEM_GROUP_TABLE
