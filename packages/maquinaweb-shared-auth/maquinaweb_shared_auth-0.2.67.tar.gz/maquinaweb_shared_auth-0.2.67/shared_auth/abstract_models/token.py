"""
Abstract model para Token
"""

from django.db import models

from shared_auth.conf import TOKEN_TABLE


class AbstractSharedToken(models.Model):
    """
    Model abstrato READ-ONLY da tabela authtoken_token
    Usado para validar tokens em outros sistemas

    Para customizar, crie um model no seu app:

    from shared_auth.abstract_models import AbstractSharedToken

    class CustomToken(AbstractSharedToken):
        # Adicione campos customizados
        custom_field = models.CharField(max_length=100)

        class Meta(AbstractSharedToken.Meta):
            pass

    E configure no settings.py:
    SHARED_AUTH_TOKEN_MODEL = 'seu_app.CustomToken'
    """

    key = models.CharField(max_length=40, primary_key=True)
    user_id = models.IntegerField()
    created = models.DateTimeField()

    objects = models.Manager()

    class Meta:
        abstract = True
        managed = False
        db_table = TOKEN_TABLE

    def __str__(self):
        return self.key

    @property
    def user(self):
        """Acessa usuário do token"""
        from shared_auth.utils import get_user_model

        if not hasattr(self, "_cached_user"):
            User = get_user_model()
            self._cached_user = User.objects.get_or_fail(self.user_id)
        return self._cached_user

    def is_valid(self):
        """Verifica se token ainda é válido"""
        # Implementar lógica de expiração se necessário
        return True
