"""
Abstract model para Member
"""

from django.db import models

from shared_auth.conf import MEMBER_TABLE


class AbstractSharedMember(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_member
    Relacionamento entre User e Organization

    Para customizar, crie um model no seu app:

    from shared_auth.abstract_models import AbstractSharedMember

    class CustomMember(AbstractSharedMember):
        # Adicione campos customizados
        custom_field = models.CharField(max_length=100)

        class Meta(AbstractSharedMember.Meta):
            pass

    E configure no settings.py:
    SHARED_AUTH_MEMBER_MODEL = 'seu_app.CustomMember'
    """

    user_id = models.IntegerField()
    organization_id = models.IntegerField()
    metadata = models.JSONField(default=dict)

    class Meta:
        abstract = True
        managed = False
        db_table = MEMBER_TABLE

    def __str__(self):
        return f"Member: User {self.user_id} - Org {self.organization_id}"

    @property
    def user(self):
        """
        Acessa usuário (lazy loading)

        Usage:
            member = SharedMember.objects.first()
            user = member.user
            print(user.email)
        """
        from shared_auth.utils import get_user_model

        User = get_user_model()
        return User.objects.get_or_fail(self.user_id)

    @property
    def organization(self):
        """
        Acessa organização (lazy loading)

        Usage:
            member = SharedMember.objects.first()
            org = member.organization
            print(org.name)
        """
        from shared_auth.utils import get_organization_model

        Organization = get_organization_model()
        return Organization.objects.get_or_fail(self.organization_id)
