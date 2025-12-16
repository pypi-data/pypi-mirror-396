"""
Models concretos para Organization e OrganizationGroup
"""

from shared_auth.abstract_models.organization import (
    AbstractOrganizationGroup,
    AbstractSharedOrganization,
)
from shared_auth.conf import ORGANIZATION_GROUP_TABLE
from shared_auth.managers.organization import SharedOrganizationManager


class SharedOrganization(AbstractSharedOrganization):
    """
    Model READ-ONLY padrão da tabela organization

    Para customizar, crie seu próprio model herdando de AbstractSharedOrganization
    """

    objects = SharedOrganizationManager()

    class Meta(AbstractSharedOrganization.Meta):
        pass


class OrganizationGroup(AbstractOrganizationGroup):
    """
    Model READ-ONLY padrão da tabela organization_organizationgroup
    Representa um grupo de organizações com assinatura compartilhada

    Para customizar, crie seu próprio model herdando de AbstractOrganizationGroup
    """

    class Meta(AbstractOrganizationGroup.Meta):
        db_table = ORGANIZATION_GROUP_TABLE
