"""
Models concretos para System, Plan e Subscription
"""

from shared_auth.abstract_models.plan import (
    AbstractPlan,
    AbstractSubscription,
    AbstractSystem,
)
from shared_auth.conf import PLAN_TABLE, SUBSCRIPTION_TABLE, SYSTEM_TABLE
from shared_auth.managers.plan import SubscriptionManager, SystemManager


class System(AbstractSystem):
    """
    Model READ-ONLY padrão da tabela plans_system
    Representa um sistema externo que usa este serviço de autenticação

    Para customizar, crie seu próprio model herdando de AbstractSystem
    """

    objects = SystemManager()

    class Meta(AbstractSystem.Meta):
        db_table = SYSTEM_TABLE


class Plan(AbstractPlan):
    """
    Model READ-ONLY padrão da tabela plans_plan
    Planos oferecidos por cada sistema, com conjunto de permissões

    Para customizar, crie seu próprio model herdando de AbstractPlan
    """

    class Meta(AbstractPlan.Meta):
        db_table = PLAN_TABLE


class Subscription(AbstractSubscription):
    """
    Model READ-ONLY padrão da tabela plans_subscription
    Assinatura de uma organização a um plano

    Para customizar, crie seu próprio model herdando de AbstractSubscription
    """

    objects = SubscriptionManager()

    class Meta(AbstractSubscription.Meta):
        db_table = SUBSCRIPTION_TABLE
