"""
Pivot/ManyToMany intermediate models
"""

from django.db import models

from shared_auth.conf import (
    GROUP_ORG_PERMISSIONS_PERMISSIONS_TABLE,
    GROUP_PERMISSIONS_PERMISSIONS_TABLE,
    PLAN_GROUP_PERMISSIONS_TABLE,
)


class GroupPermissionsPermission(models.Model):
    grouppermissions_id = models.BigIntegerField()
    permissions_id = models.BigIntegerField()

    class Meta:
        db_table = GROUP_PERMISSIONS_PERMISSIONS_TABLE
        managed = False
        unique_together = ("grouppermissions_id", "permissions_id")
        app_label = "shared_auth"

    def __str__(self):
        return f"GroupPerm {self.grouppermissions_id} → Perm {self.permissions_id}"


class PlanGroupPermission(models.Model):
    plan_id = models.BigIntegerField()
    grouppermissions_id = models.BigIntegerField()

    class Meta:
        db_table = PLAN_GROUP_PERMISSIONS_TABLE
        managed = False
        unique_together = ("plan_id", "grouppermissions_id")
        app_label = "shared_auth"

    def __str__(self):
        return f"Plan {self.plan_id} → GroupPerm {self.grouppermissions_id}"


class GroupOrgPermissionsPermission(models.Model):
    grouporganizationpermissions_id = models.BigIntegerField()
    permissions_id = models.BigIntegerField()

    class Meta:
        db_table = GROUP_ORG_PERMISSIONS_PERMISSIONS_TABLE
        managed = False
        unique_together = ("grouporganizationpermissions_id", "permissions_id")
        app_label = "shared_auth"

    def __str__(self):
        return f"OrgGroup {self.grouporganizationpermissions_id} → Perm {self.permissions_id}"
