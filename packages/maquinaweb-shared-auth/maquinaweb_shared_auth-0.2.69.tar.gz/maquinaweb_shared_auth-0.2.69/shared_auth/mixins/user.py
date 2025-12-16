"""
Mixin relacionado a User
"""

from django.db import models

from shared_auth.managers.base import BaseAuthManager


class UserMixin(models.Model):
    """
    Mixin para models que pertencem a um usuário

    Adiciona:
    - Campo user_id
    - Property user (lazy loading)
    - Métodos úteis

    Usage:
        class Rascunho(UserMixin):
            titulo = models.CharField(max_length=200)

        # Uso
        rascunho.user  # Acessa usuário automaticamente
        rascunho.user_email  # Acessa email
    """

    user_id = models.IntegerField(
        db_index=True,
        help_text="ID do usuário no sistema de autenticação",
        null=True,
        default=None,
    )
    objects = BaseAuthManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["user_id"]),
        ]

    @property
    def user(self):
        """
        Acessa usuário do banco de auth (lazy loading com cache)
        """
        if not hasattr(self, "_cached_user"):
            from shared_auth.utils import get_user_model

            User = get_user_model()
            self._cached_user = User.objects.get_or_fail(self.user_id)
        return self._cached_user

    @property
    def user_email(self):
        """Retorna email do usuário (safe)"""
        try:
            return self.user.email
        except Exception:
            return None

    @property
    def user_full_name(self):
        """Retorna nome completo do usuário (safe)"""
        try:
            return self.user.get_full_name()
        except Exception:
            return None

    @property
    def user_organizations(self):
        """Retorna organizações do usuário"""
        return self.user.organizations

    def is_user_active(self):
        """Verifica se o usuário está ativo"""
        try:
            return self.user.is_active and self.user.deleted_at is None
        except Exception:
            return False
