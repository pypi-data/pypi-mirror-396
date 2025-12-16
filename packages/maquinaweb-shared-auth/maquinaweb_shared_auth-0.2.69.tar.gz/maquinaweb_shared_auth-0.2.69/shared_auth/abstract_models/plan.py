"""
Abstract models para System, Plan e Subscription
"""

from django.db import models
from django.utils import timezone

from shared_auth.conf import PLAN_TABLE, SUBSCRIPTION_TABLE, SYSTEM_TABLE


class AbstractSystem(models.Model):
    """
    Model abstrato READ-ONLY da tabela plans_system
    Representa um sistema externo que usa este serviço de autenticação

    Para customizar, crie um model no seu app:

    from shared_auth.abstract_models import AbstractSystem

    class CustomSystem(AbstractSystem):
        custom_field = models.CharField(max_length=100)

        class Meta(AbstractSystem.Meta):
            pass

    E configure no settings.py:
    SHARED_AUTH_SYSTEM_MODEL = 'seu_app.CustomSystem'
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = models.Manager()  # Will be replaced by SystemManager in concrete model

    class Meta:
        abstract = True
        managed = False
        db_table = SYSTEM_TABLE

    def __str__(self):
        return self.name


class AbstractPlan(models.Model):
    """
    Model abstrato READ-ONLY da tabela plans_plan
    Planos oferecidos por cada sistema, com conjunto de permissões

    Para customizar, configure:
    SHARED_AUTH_PLAN_MODEL = 'seu_app.CustomPlan'
    """

    name = models.CharField(max_length=100)
    slug = models.SlugField()
    system_id = models.IntegerField()
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    recurrence = models.CharField(max_length=10)

    # Campos de desconto - aplicados nas primeiras recorrências
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valor de desconto aplicado nas primeiras recorrências",
    )
    discount_duration = models.PositiveIntegerField(
        null=True, blank=True, help_text="Número de recorrências com desconto"
    )

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = models.Manager()

    class Meta:
        abstract = True
        managed = False
        db_table = PLAN_TABLE

    def __str__(self):
        return f"{self.name} - {self.system.name if hasattr(self, 'system') else self.system_id}"

    @property
    def system(self):
        """Acessa sistema (lazy loading)"""
        from shared_auth.utils import get_system_model

        if not hasattr(self, "_cached_system"):
            System = get_system_model()
            self._cached_system = System.objects.get_or_fail(self.system_id)
        return self._cached_system

    @property
    def group_permissions(self):
        from shared_auth.abstract_models.pivot import PlanGroupPermission

        from shared_auth.utils import get_group_permissions_model

        GroupPermissions = get_group_permissions_model()

        group_ids = (
            PlanGroupPermission.objects.using("auth_db")
            .filter(plan_id=self.pk)
            .values_list("grouppermissions_id", flat=True)
        )

        return GroupPermissions.objects.using("auth_db").filter(id__in=group_ids)

    def get_price_for_subscription(self, payment_count=0):
        """
        Calcula o preço considerando desconto aplicado.

        Args:
            payment_count: Número de pagamentos já realizados para esta subscription.
                          Se for o primeiro pagamento (count=0), aplica desconto se houver.

        Returns:
            Decimal: Preço do plano, com desconto se aplicável.
        """
        if self.discount_amount and self.discount_duration:
            if payment_count < self.discount_duration:
                return self.price - self.discount_amount
        return self.price


class AbstractSubscription(models.Model):
    """
    Model abstrato READ-ONLY da tabela plans_subscription
    Assinatura de plano por grupo de organizações.
    Uma assinatura cobre TODAS as organizações do grupo.

    Modelo simplificado: 1 subscription por plano que renova continuamente.
    Histórico de pagamentos é mantido no model Payment.

    Para customizar, configure:
    SHARED_AUTH_SUBSCRIPTION_MODEL = 'seu_app.CustomSubscription'
    """

    organization_group_id = models.IntegerField(
        help_text="Grupo de organizações cobertas por esta assinatura"
    )
    plan_id = models.IntegerField()
    payment_date = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True)
    started_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    objects = models.Manager()  # Will be replaced by SubscriptionManager

    class Meta:
        abstract = True
        managed = False
        db_table = SUBSCRIPTION_TABLE

    def __str__(self):
        return f"Subscription {self.pk} - Group {self.organization_group_id}"

    @property
    def organization_group(self):
        """Acessa grupo de organizações (lazy loading)"""
        from shared_auth.utils import get_organization_group_model

        if not hasattr(self, "_cached_organization_group"):
            OrganizationGroup = get_organization_group_model()
            try:
                self._cached_organization_group = OrganizationGroup.objects.get(
                    pk=self.organization_group_id
                )
            except OrganizationGroup.DoesNotExist:
                self._cached_organization_group = None
        return self._cached_organization_group

    @property
    def plan(self):
        """Acessa plano (lazy loading)"""
        from shared_auth.utils import get_plan_model

        if not hasattr(self, "_cached_plan"):
            Plan = get_plan_model()
            try:
                self._cached_plan = Plan.objects.get(pk=self.plan_id)
            except Plan.DoesNotExist:
                self._cached_plan = None
        return self._cached_plan

    def is_valid(self):
        """Verifica se assinatura está ativa, paga e não expirada (DEPRECATED: use is_active_and_valid)"""
        return self.is_active_and_valid()

    def is_active_and_valid(self):
        """
        Verifica se subscription está ativa, paga e dentro do prazo.
        Considera também se foi cancelada.
        """
        if not self.active or not self.paid:
            return False

        if self.canceled_at:
            # Se cancelada, ainda é válida até expirar
            if self.expires_at and self.expires_at < timezone.now():
                return False
            return True

        if self.expires_at and self.expires_at < timezone.now():
            return False

        return True

    def is_expired(self):
        """Verifica se a assinatura está expirada"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def needs_renewal(self):
        """
        Verifica se a subscription precisa de renovação.
        Retorna True se auto_renew ativo e expiração atingida/próxima.
        """
        if not self.auto_renew:
            return False
        if not self.expires_at:
            return False
        return timezone.now() >= self.expires_at

    def set_paid(self):
        """Marca assinatura como paga (apenas para referência, não salva)"""
        self.paid = True
        self.payment_date = timezone.now()

    def cancel(self):
        """Cancela assinatura - mantém ativa até expirar (apenas para referência, não salva)"""
        self.auto_renew = False
        self.canceled_at = timezone.now()
