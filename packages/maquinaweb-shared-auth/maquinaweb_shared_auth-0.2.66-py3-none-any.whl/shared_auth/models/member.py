"""
Model concreto para Member
"""

from shared_auth.abstract_models.member import AbstractSharedMember
from shared_auth.managers.member import SharedMemberManager


class SharedMember(AbstractSharedMember):
    """
    Model READ-ONLY padrão da tabela organization_member

    Para customizar, crie seu próprio model herdando de AbstractSharedMember
    """

    objects = SharedMemberManager()

    class Meta(AbstractSharedMember.Meta):
        pass
