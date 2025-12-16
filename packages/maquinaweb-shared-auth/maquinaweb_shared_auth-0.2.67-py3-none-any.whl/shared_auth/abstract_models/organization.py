"""
Abstract models para Organization e OrganizationGroup
"""

import os

from django.db import models

from shared_auth.conf import ORGANIZATION_TABLE
from shared_auth.storage_backend import Storage


def organization_image_path(instance, filename):
    return os.path.join(
        "organization",
        str(instance.pk),
        "images",
        filename,
    )


class AbstractSharedOrganization(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization
    Usado para acessar dados de organizações em outros sistemas

    Para customizar, crie um model no seu app:

    from shared_auth.abstract_models import AbstractSharedOrganization

    class CustomOrganization(AbstractSharedOrganization):
        # Adicione campos customizados
        custom_field = models.CharField(max_length=100)

        class Meta(AbstractSharedOrganization.Meta):
            pass

    E configure no settings.py:
    SHARED_AUTH_ORGANIZATION_MODEL = 'seu_app.CustomOrganization'
    """

    # Campos principais
    name = models.CharField(max_length=255)
    fantasy_name = models.CharField(max_length=255, blank=True, null=True)
    cnpj = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    cellphone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    image_organization = models.ImageField(
        storage=Storage, upload_to=organization_image_path, null=True
    )
    logo = models.ImageField(
        storage=Storage, upload_to=organization_image_path, null=True
    )

    # Relacionamentos
    organization_group_id = models.IntegerField(null=True, blank=True)
    main_organization_id = models.IntegerField(null=True, blank=True)
    is_branch = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict)

    # Metadados
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        managed = False
        db_table = ORGANIZATION_TABLE

    def __str__(self):
        return self.fantasy_name or self.name or f"Org #{self.pk}"

    @property
    def organization_group(self):
        """
        Acessa grupo de organização (lazy loading)

        Usage:
            if org.organization_group:
                print(org.organization_group.name)
        """
        from shared_auth.utils import get_organization_group_model

        if self.organization_group_id:
            OrganizationGroup = get_organization_group_model()
            return OrganizationGroup.objects.get_or_fail(self.organization_group_id)
        return None

    @property
    def main_organization(self):
        """
        Acessa organização principal (lazy loading)

        Usage:
            if org.is_branch:
                main = org.main_organization
        """
        from shared_auth.utils import get_organization_model

        if self.main_organization_id:
            Organization = get_organization_model()
            return Organization.objects.get_or_fail(self.main_organization_id)
        return None

    @property
    def branches(self):
        """
        Retorna filiais desta organização

        Usage:
            branches = org.branches
        """
        from shared_auth.utils import get_organization_model

        Organization = get_organization_model()
        return Organization.objects.filter(main_organization_id=self.pk)

    @property
    def members(self):
        """
        Retorna membros desta organização

        Usage:
            members = org.members
            for member in members:
                print(member.user.email)
        """
        from shared_auth.utils import get_member_model

        Member = get_member_model()
        return Member.objects.for_organization(self.pk)

    @property
    def users(self):
        """
        Retorna usuários desta organização

        Usage:
            users = org.users
        """
        from shared_auth.utils import get_user_model

        User = get_user_model()
        return User.objects.filter(
            id__in=self.members.values_list("user_id", flat=True)
        )

    def is_active(self):
        """Verifica se organização está ativa"""
        return self.deleted_at is None

    def get_permissions_for_system(self, system):
        """
        Retorna permissões do sistema baseado na assinatura do grupo de organizações.
        Se a organização não pertence a um grupo, retorna vazio.

        Args:
            system: Instance do System model ou system_id (int)

        Returns:
            QuerySet de Permission objects

        Usage:
            from shared_auth.utils import get_system_model

            System = get_system_model()
            system = System.objects.get(name='MeuSistema')
            permissions = organization.get_permissions_for_system(system)
        """
        from shared_auth.utils import get_permission_model, get_subscription_model

        # Se não pertence a um grupo, sem permissões
        if not self.organization_group_id:
            Permission = get_permission_model()
            return Permission.objects.none()

        # Extrai system_id se foi passado um objeto
        system_id = system.id if hasattr(system, "id") else system

        Subscription = get_subscription_model()
        Permission = get_permission_model()

        # Busca assinatura ativa do grupo
        subscription = (
            Subscription.objects.filter(
                organization_group_id=self.organization_group_id,
                plan__system_id=system_id,
                active=True,
                paid=True,
            )
            .select_related("plan")
            .order_by("-started_at")
            .first()
        )

        if not subscription:
            return Permission.objects.none()

        # Coleta todas as permissões dos grupos de permissões do plano
        permission_ids = set()
        for group in subscription.plan.group_permissions.all():
            permission_ids.update(group.permissions.values_list("id", flat=True))

        return Permission.objects.filter(id__in=permission_ids, system_id=system_id)


class AbstractOrganizationGroup(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_organizationgroup
    Representa um grupo de organizações com assinatura compartilhada

    Para customizar, crie um model no seu app:

    from shared_auth.abstract_models import AbstractOrganizationGroup

    class CustomOrganizationGroup(AbstractOrganizationGroup):
        custom_field = models.CharField(max_length=100)

        class Meta(AbstractOrganizationGroup.Meta):
            pass

    E configure no settings.py:
    SHARED_AUTH_ORGANIZATION_GROUP_MODEL = 'seu_app.CustomOrganizationGroup'
    """

    owner_id = models.IntegerField()
    name = models.CharField(
        max_length=255, help_text="Nome do grupo (ex: 'Empresas do João', 'Grupo Acme')"
    )

    # Campos de billing (usados para pagamentos)
    document = models.CharField(
        max_length=20, blank=True, null=True, help_text="CPF/CNPJ"
    )
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    # Organização padrão do grupo
    default_organization_id = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = models.Manager()

    class Meta:
        abstract = True
        managed = False
        db_table = "organization_organizationgroup"  # Will be imported from conf in concrete model

    def __str__(self):
        return f"{self.name} (Owner: {self.owner_id})"

    @property
    def owner(self):
        """Acessa usuário (lazy loading)"""
        from shared_auth.utils import get_user_model

        if not hasattr(self, "_cached_owner"):
            User = get_user_model()
            self._cached_owner = User.objects.get_or_fail(self.owner_id)
        return self._cached_owner

    @property
    def default_organization(self):
        """Acessa organização padrão (lazy loading)"""
        from shared_auth.utils import get_organization_model

        if not self.default_organization_id:
            return None

        if not hasattr(self, "_cached_default_organization"):
            Organization = get_organization_model()
            try:
                self._cached_default_organization = Organization.objects.get(
                    pk=self.default_organization_id
                )
            except Organization.DoesNotExist:
                self._cached_default_organization = None
        return self._cached_default_organization

    @property
    def organizations(self):
        """Retorna organizações pertencentes a este grupo"""
        from shared_auth.utils import get_organization_model

        Organization = get_organization_model()
        return Organization.objects.filter(organization_group_id=self.pk)

    @property
    def subscriptions(self):
        """Retorna assinaturas ativas deste grupo"""
        from shared_auth.utils import get_subscription_model

        Subscription = get_subscription_model()
        return Subscription.objects.filter(organization_group_id=self.pk)

    def has_active_subscription(self, system_id=None):
        """
        Verifica se o grupo tem assinatura ativa.

        Args:
            system_id: Opcional. ID do sistema para verificar assinatura específica.
        """
        from shared_auth.utils import get_subscription_model

        Subscription = get_subscription_model()
        qs = Subscription.objects.filter(
            organization_group_id=self.pk, active=True, paid=True
        )

        if system_id:
            qs = qs.filter(plan__system_id=system_id)

        return qs.exists()
