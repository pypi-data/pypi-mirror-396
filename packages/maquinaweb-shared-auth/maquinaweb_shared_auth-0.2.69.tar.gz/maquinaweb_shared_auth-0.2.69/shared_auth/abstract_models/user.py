"""
Abstract model para User
"""

from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.db import models

from shared_auth.conf import USER_TABLE
from shared_auth.exceptions import OrganizationNotFoundError
from shared_auth.storage_backend import Storage


class AbstractUser(DjangoAbstractUser):
    """
    Model abstrato READ-ONLY da tabela auth_user

    Para customizar, crie um model no seu app:

    from shared_auth.abstract_models import AbstractUser

    class CustomUser(AbstractUser):
        # Adicione campos customizados
        custom_field = models.CharField(max_length=100)

        class Meta(AbstractUser.Meta):
            pass

    E configure no settings.py:
    SHARED_AUTH_USER_MODEL = 'seu_app.CustomUser'
    """

    date_joined = models.DateTimeField()
    last_login = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(storage=Storage, blank=True, null=True)

    # Campos customizados
    createdat = models.DateTimeField()
    updatedat = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        managed = False
        db_table = USER_TABLE

    @property
    def organizations(self):
        """
        Retorna todas as organizações associadas ao usuário.
        """
        from shared_auth.utils import get_member_model, get_organization_model

        Organization = get_organization_model()
        Member = get_member_model()

        return Organization.objects.filter(
            id__in=Member.objects.filter(user_id=self.id).values_list(
                "organization_id", flat=True
            )
        )

    def get_org(self, organization_id):
        """
        Retorna a organização especificada pelo ID, se o usuário for membro.
        """
        from shared_auth.utils import get_member_model, get_organization_model

        Organization = get_organization_model()
        Member = get_member_model()

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            raise OrganizationNotFoundError(
                f"Organização com ID {organization_id} não encontrada."
            )

        if not Member.objects.filter(
            user_id=self.id, organization_id=organization.id
        ).exists():
            raise OrganizationNotFoundError("Usuário não é membro desta organização.")

        return organization
