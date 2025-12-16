"""
Manager para SharedMember
"""

from django.db import models


class SharedMemberManager(models.Manager):
    """Manager para SharedMember"""

    def for_user(self, user_id):
        """Retorna memberships de um usuário"""
        return self.filter(user_id=user_id)

    def for_organization(self, organization_id):
        """Retorna membros de uma organização"""
        return self.filter(organization_id=organization_id)
