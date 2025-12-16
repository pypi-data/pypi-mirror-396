"""
Mixin relacionado a Contact
"""

from django.db import models

from shared_auth.managers.base import BaseAuthManager


class ContactMixin(models.Model):
    """
    Mixin para adicionar campos de contato
    """

    contact_id = models.IntegerField(db_index=True, null=True, default=None)
    objects = BaseAuthManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["contact_id"]),
        ]

    @property
    def contact(self):
        """Retorna contato do banco de auth (lazy loading com cache)"""
        if not hasattr(self, "_cached_contact"):
            from shared_auth.utils import get_contact_model

            Contact = get_contact_model()
            self._cached_contact = Contact.objects.get_or_fail(self.contact_id)
        return self._cached_contact
