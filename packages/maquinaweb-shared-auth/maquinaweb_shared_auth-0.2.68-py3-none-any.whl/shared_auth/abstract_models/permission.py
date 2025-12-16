"""
Abstract models para Permission, GroupPermissions, GroupOrganizationPermissions, MemberSystemGroup
"""

from django.db import models

from shared_auth.conf import (
    GROUP_ORG_PERMISSIONS_TABLE,
    GROUP_PERMISSIONS_TABLE,
    PERMISSION_TABLE,
)


class AbstractPermission(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_permissions
    Define permissões específicas de cada sistema

    Para customizar, crie um model no seu app e configure:
    SHARED_AUTH_PERMISSION_MODEL = 'seu_app.CustomPermission'
    """

    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.TextField()
    scope = models.CharField(max_length=100, blank=True, default="")
    scope_label = models.CharField(max_length=100, blank=True, default="")
    model = models.CharField(max_length=100, blank=True, default="")
    model_label = models.CharField(max_length=100, blank=True, default="")
    system_id = models.IntegerField()

    objects = models.Manager()

    class Meta:
        abstract = True
        managed = False
        db_table = PERMISSION_TABLE

    def __str__(self):
        return f"{self.codename} ({self.name})"

    @property
    def system(self):
        """Acessa sistema (lazy loading)"""
        from shared_auth.utils import get_system_model

        if not hasattr(self, "_cached_system"):
            System = get_system_model()
            self._cached_system = System.objects.get_or_fail(self.system_id)
        return self._cached_system


class AbstractGroupPermissions(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_grouppermissions
    Grupos base de permissões (usados nos planos)

    Para customizar, configure:
    SHARED_AUTH_GROUP_PERMISSIONS_MODEL = 'seu_app.CustomGroupPermissions'
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    system_id = models.IntegerField()

    objects = models.Manager()

    class Meta:
        abstract = True
        managed = False
        db_table = GROUP_PERMISSIONS_TABLE

    def __str__(self):
        return self.name

    @property
    def system(self):
        """Acessa sistema (lazy loading)"""
        from shared_auth.utils import get_system_model

        if not hasattr(self, "_cached_system"):
            System = get_system_model()
            self._cached_system = System.objects.get_or_fail(self.system_id)
        return self._cached_system

    @property
    def permissions(self):
        from shared_auth.abstract_models.pivot import GroupPermissionsPermission

        from shared_auth.utils import get_permission_model

        Permission = get_permission_model()

        perm_ids = (
            GroupPermissionsPermission.objects.using("auth_db")
            .filter(grouppermissions_id=self.pk)
            .values_list("permissions_id", flat=True)
        )

        return Permission.objects.using("auth_db").filter(id__in=perm_ids)


class AbstractGroupOrganizationPermissions(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_grouporganizationpermissions
    Grupos de permissões criados pela organização para distribuir aos usuários

    Para customizar, configure:
    SHARED_AUTH_GROUP_ORG_PERMISSIONS_MODEL = 'seu_app.CustomGroupOrgPermissions'
    """

    organization_id = models.IntegerField()
    system_id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    objects = (
        models.Manager()
    )  # Will be replaced by GroupOrganizationPermissionsManager

    class Meta:
        abstract = True
        managed = False
        db_table = GROUP_ORG_PERMISSIONS_TABLE

    def __str__(self):
        return f"{self.name} (Org {self.organization_id})"

    @property
    def organization(self):
        """Acessa organização (lazy loading)"""
        from shared_auth.utils import get_organization_model

        if not hasattr(self, "_cached_organization"):
            Organization = get_organization_model()
            self._cached_organization = Organization.objects.get_or_fail(
                self.organization_id
            )
        return self._cached_organization

    @property
    def system(self):
        """Acessa sistema (lazy loading)"""
        from shared_auth.utils import get_system_model

        if not hasattr(self, "_cached_system"):
            System = get_system_model()
            self._cached_system = System.objects.get_or_fail(self.system_id)
        return self._cached_system

    @property
    def permissions(self):
        from shared_auth.abstract_models.pivot import GroupOrgPermissionsPermission

        from shared_auth.utils import get_permission_model

        Permission = get_permission_model()

        perm_ids = (
            GroupOrgPermissionsPermission.objects.using("auth_db")
            .filter(grouporganizationpermissions_id=self.pk)
            .values_list("permissions_id", flat=True)
        )

        return Permission.objects.using("auth_db").filter(id__in=perm_ids)


class AbstractMemberSystemGroup(models.Model):
    """
    Model abstrato READ-ONLY da tabela organization_membersystemgroup
    Relaciona um membro a um grupo de permissões em um sistema específico

    Para customizar, configure:
    SHARED_AUTH_MEMBER_SYSTEM_GROUP_MODEL = 'seu_app.CustomMemberSystemGroup'
    """

    member_id = models.IntegerField()
    group_id = models.IntegerField()
    system_id = models.IntegerField()
    created_at = models.DateTimeField()

    objects = models.Manager()  # Will be replaced by MemberSystemGroupManager

    class Meta:
        abstract = True
        managed = False
        db_table = GROUP_ORG_PERMISSIONS_TABLE

    def __str__(self):
        return (
            f"Member {self.member_id} - Group {self.group_id} - System {self.system_id}"
        )

    @property
    def member(self):
        """Acessa membro (lazy loading)"""
        from shared_auth.utils import get_member_model

        if not hasattr(self, "_cached_member"):
            Member = get_member_model()
            try:
                self._cached_member = Member.objects.get(pk=self.member_id)
            except Member.DoesNotExist:
                self._cached_member = None
        return self._cached_member

    @property
    def group(self):
        """Acessa grupo (lazy loading)"""
        from shared_auth.utils import get_group_organization_permissions_model

        if not hasattr(self, "_cached_group"):
            GroupOrgPermissions = get_group_organization_permissions_model()
            try:
                self._cached_group = GroupOrgPermissions.objects.get(pk=self.group_id)
            except GroupOrgPermissions.DoesNotExist:
                self._cached_group = None
        return self._cached_group

    @property
    def system(self):
        """Acessa sistema (lazy loading)"""
        from shared_auth.utils import get_system_model

        if not hasattr(self, "_cached_system"):
            System = get_system_model()
            self._cached_system = System.objects.get_or_fail(self.system_id)
        return self._cached_system
