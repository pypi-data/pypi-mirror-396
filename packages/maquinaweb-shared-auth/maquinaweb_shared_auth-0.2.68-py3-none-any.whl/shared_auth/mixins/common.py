"""
Mixins comuns que combinam funcionalidades
"""

from django.db import models

from .organization import OrganizationMixin
from .user import UserMixin


class OrganizationUserMixin(OrganizationMixin, UserMixin):
    """
    Mixin combinado para models que pertencem a organização E usuário

    Adiciona tudo dos dois mixins + validações

    Usage:
        class Rascunho(OrganizationUserMixin):
            titulo = models.CharField(max_length=200)

        # Uso
        rascunho.organization  # Organização
        rascunho.user  # Usuário
        rascunho.validate_user_belongs_to_organization()  # Validação
    """

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["organization_id", "user_id"]),
        ]

    def validate_user_belongs_to_organization(self):
        """
        Valida se o usuário pertence à organização

        Returns:
            bool: True se pertence, False caso contrário
        """
        from shared_auth.utils import get_member_model

        Member = get_member_model()
        return Member.objects.filter(
            user_id=self.user_id, organization_id=self.organization_id
        ).exists()

    def user_can_access(self, user_id):
        """
        Verifica se um usuário pode acessar este registro
        (se pertence à mesma organização)
        """
        from shared_auth.utils import get_member_model

        Member = get_member_model()
        return Member.objects.filter(
            user_id=user_id, organization_id=self.organization_id
        ).exists()


class TimestampedMixin(models.Model):
    """
    Mixin para adicionar timestamps
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
