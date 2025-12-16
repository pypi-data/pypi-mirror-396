"""
Model concreto para Token
"""

from shared_auth.abstract_models.token import AbstractSharedToken


class SharedToken(AbstractSharedToken):
    """
    Model READ-ONLY padrão da tabela authtoken_token

    Para customizar, crie seu próprio model herdando de AbstractSharedToken
    """

    class Meta(AbstractSharedToken.Meta):
        pass
