"""
Managers para System e Subscription
"""

from django.db import models


class SystemManager(models.Manager):
    """Manager for System model"""

    def get_or_fail(self, system_id):
        """Get system or raise custom exception"""
        from shared_auth.exceptions import SharedAuthError

        try:
            return self.get(pk=system_id)
        except self.model.DoesNotExist:
            raise SharedAuthError(f"Sistema com ID {system_id} não encontrado")

    def active(self):
        """Return only active systems"""
        return self.filter(active=True)

    def by_name(self, name):
        """Search by name"""
        return self.filter(name__iexact=name).first()


class SubscriptionManager(models.Manager):
    """Manager for Subscription model"""

    def active(self):
        """Return only active subscriptions"""
        return self.filter(active=True, paid=True)

    def for_organization(self, organization_id):
        """Get subscriptions for an organization"""
        return self.filter(organization_id=organization_id)

    def for_system(self, system_id):
        """Get subscriptions for a system (via plan)"""
        return self.filter(plan__system_id=system_id)

    def valid_for_organization_and_system(self, organization_id, system_id):
        """
        Get valid subscription for organization and system.

        Returns the active, paid subscription that hasn't expired.
        """
        from django.utils import timezone

        return (
            self.filter(
                organization_id=organization_id,
                plan__system_id=system_id,
                active=True,
                paid=True,
            )
            .filter(
                models.Q(expires_at__isnull=True)
                | models.Q(expires_at__gt=timezone.now())
            )
            .first()
        )
