"""
Manager para User
"""

from django.contrib.auth.models import UserManager as DjangoUserManager

from shared_auth.exceptions import UserNotFoundError


class UserManager(DjangoUserManager):
    """Manager para User"""

    def get_or_fail(self, user_id):
        """Busca usuário ou lança exceção"""
        try:
            return self.get(pk=user_id)
        except self.model.DoesNotExist:
            raise UserNotFoundError(f"Usuário com ID {user_id} não encontrado")

    def active(self):
        """Retorna usuários ativos"""
        return self.filter(deleted_at__isnull=True, is_active=True)

    def by_email(self, email):
        """Busca por email"""
        return self.filter(email=email).first()
