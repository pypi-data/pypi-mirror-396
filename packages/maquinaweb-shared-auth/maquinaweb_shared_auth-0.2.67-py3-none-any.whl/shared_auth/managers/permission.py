"""
Managers para Permission, GroupOrganizationPermissions e MemberSystemGroup
"""

from django.db import models


class PermissionManager(models.Manager):
    """Manager for Permission model"""

    def get_or_fail(self, permission_id):
        """Get permission or raise exception"""
        from shared_auth.exceptions import SharedAuthError

        try:
            return self.get(pk=permission_id)
        except self.model.DoesNotExist:
            raise SharedAuthError(f"Permissão com ID {permission_id} não encontrada")

    def for_system(self, system_id):
        """Get permissions for a system"""
        return self.filter(system_id=system_id)

    def by_codename(self, codename, system_id=None):
        """Search by codename"""
        qs = self.filter(codename=codename)
        if system_id:
            qs = qs.filter(system_id=system_id)
        return qs.first()


class GroupOrganizationPermissionsManager(models.Manager):
    """Manager for GroupOrganizationPermissions model"""

    def for_organization(self, organization_id):
        """Get groups for an organization"""
        return self.filter(organization_id=organization_id)

    def for_system(self, system_id):
        """Get groups for a system"""
        return self.filter(system_id=system_id)

    def for_organization_and_system(self, organization_id, system_id):
        """Get groups for organization and system"""
        return self.filter(organization_id=organization_id, system_id=system_id)


class MemberSystemGroupManager(models.Manager):
    """Manager for MemberSystemGroup model"""

    def for_member(self, member_id):
        """Get groups for a member"""
        return self.filter(member_id=member_id)

    def for_system(self, system_id):
        """Get assignments for a system"""
        return self.filter(system_id=system_id)

    def get_group_for_member_and_system(self, member_id, system_id):
        """
        Get the group assigned to a member for a specific system.

        Returns the MemberSystemGroup object or None.
        """
        return self.filter(member_id=member_id, system_id=system_id).first()
