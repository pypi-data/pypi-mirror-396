"""
Middleware de verificação de pagamento
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class PaymentVerificationMiddleware(MiddlewareMixin):
    """
    Middleware que verifica se a organização possui assinatura ativa.

    Bloqueia acesso se:
    - Usuário não está em OrganizationGroup
    - OrganizationGroup não tem subscription ativa e paga

    Usage em settings.py:
        MIDDLEWARE = [
            'shared_auth.middleware.SharedAuthMiddleware',
            'shared_auth.middleware.OrganizationMiddleware',
            'shared_auth.middleware.PaymentVerificationMiddleware',  # Adicionar por último
        ]

        # Caminhos permitidos sem pagamento
        PAYMENT_EXEMPT_PATHS = [
            '/api/auth/',
            '/api/checkout/',
            '/admin/',
        ]
    """

    # Caminhos padrão permitidos sem verificação de pagamento
    DEFAULT_ALLOWED_PATHS = [
        "/api/auth/",
        "/api/checkout/",
        "/admin/",
        "/health/",
        "/docs/",
        "/static/",
        "/api/schema/",
    ]

    def process_request(self, request):
        from django.conf import settings

        # Ignora se não autenticado
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return None

        # Ignora superusers
        if request.user.is_superuser:
            return None

        # Pega caminhos permitidos do settings ou usa padrão
        allowed_paths = getattr(
            settings, "PAYMENT_EXEMPT_PATHS", self.DEFAULT_ALLOWED_PATHS
        )

        # Verifica se path é permitido
        if any(request.path.startswith(path) for path in allowed_paths):
            return None

        # Busca OrganizationGroup do usuário
        from shared_auth.utils import (
            get_organization_group_model,
            get_subscription_model,
        )

        OrganizationGroup = get_organization_group_model()
        Subscription = get_subscription_model()

        # Tenta encontrar OrganizationGroup onde usuário é owner
        organization_group = OrganizationGroup.objects.filter(
            owner_id=request.user.id
        ).first()

        if not organization_group:
            return JsonResponse(
                {
                    "error": "no_organization_group",
                    "message": "Usuário não possui grupo de organização. Complete o onboarding.",
                    "redirect": "/onboarding/",
                },
                status=403,
            )

        # Verifica se tem subscription ativa e paga
        has_active_subscription = Subscription.objects.filter(
            organization_group_id=organization_group.pk, active=True, paid=True
        ).exists()

        if not has_active_subscription:
            return JsonResponse(
                {
                    "error": "no_active_subscription",
                    "message": "Não há assinatura ativa. Realize o pagamento para continuar.",
                    "redirect": "/checkout/",
                },
                status=402,  # Payment Required
            )

        return None
