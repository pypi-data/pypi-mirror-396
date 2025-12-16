"""
Model concreto para User
"""

from shared_auth.abstract_models.user import AbstractUser
from shared_auth.managers.user import UserManager


class User(AbstractUser):
    """
    Model READ-ONLY padrão da tabela auth_user

    Para customizar, crie seu próprio model herdando de AbstractUser
    """

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        pass
