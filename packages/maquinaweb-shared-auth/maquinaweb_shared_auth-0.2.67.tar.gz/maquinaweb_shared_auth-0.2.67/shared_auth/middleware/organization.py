"""
Middleware de organização
"""

from django.utils.deprecation import MiddlewareMixin

from shared_auth.authentication import SharedTokenAuthentication
from shared_auth.utils import get_member_model, get_organization_model


def get_member(user_id, organization_id):
    """Busca membro usando o model configurado"""
    Member = get_member_model()
    return Member.objects.filter(
        user_id=user_id, organization_id=organization_id
    ).first()


class OrganizationMiddleware(MiddlewareMixin):
    """
    Middleware que adiciona organização logada ao request

    Adiciona:
    - request.organization (objeto SharedOrganization)
    """

    def process_request(self, request) -> None:
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip:
            ip = ip.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")

        organization_id = self._determine_organization_id(request)
        user = self._authenticate_user(request)

        if not organization_id and not user:
            return

        if organization_id and user:
            organization_id = self._validate_organization_membership(
                user, organization_id
            )
            if not organization_id:
                return

        organization_ids = self._determine_organization_ids(request)

        request.organization_id = organization_id
        request.organization_ids = organization_ids
        Organization = get_organization_model()
        request.organization = Organization.objects.filter(pk=organization_id).first()

        if user and organization_id:
            system_id = self._get_system_id(request)
            if system_id:
                from shared_auth.permissions.cache import warmup_permissions_cache

                warmup_permissions_cache(user.id, organization_id, system_id, request)

    @staticmethod
    def _authenticate_user(request):
        try:
            data = SharedTokenAuthentication().authenticate(request)
        except Exception:
            return None

        return data[0] if data else None

    def _determine_organization_id(self, request):
        org_id = self._get_organization_from_header(request)
        if org_id:
            return org_id

        return self._get_organization_from_user(request)

    def _determine_organization_ids(self, request):
        return self._get_organization_ids_from_user(request)

    @staticmethod
    def _get_organization_from_header(request):
        if header_value := request.headers.get("X-Organization"):
            try:
                return int(header_value)
            except (ValueError, TypeError):
                pass
        return None

    @staticmethod
    def _get_organization_from_user(request):
        """
        Retorna a primeira organização do usuário autenticado
        """
        if not request.user.is_authenticated:
            return None

        # Buscar a primeira organização que o usuário pertence
        Member = get_member_model()
        member = Member.objects.filter(user_id=request.user.pk).first()

        return member.organization_id if member else None

    @staticmethod
    def _get_organization_ids_from_user(request):
        if not request.user.is_authenticated:
            return None

        Member = get_member_model()
        member = Member.objects.filter(user_id=request.user.pk)

        return (
            list(member.values_list("organization_id", flat=True)) if member else None
        )

    @staticmethod
    def _validate_organization_membership(user, organization_id):
        try:
            member = get_member(user.pk, organization_id)
            if not member and not user.is_superuser:
                return None
            return organization_id
        except Exception:
            return None

    @staticmethod
    def _get_system_id(request):
        """
        Obtém o system_id para warm-up de permissões.

        Busca em:
        1. Settings SYSTEM_ID
        2. Header X-System-ID
        """
        from django.conf import settings

        system_id = getattr(settings, "SYSTEM_ID", None)
        if system_id:
            return system_id

        # Tentar pegar do header
        header_value = request.headers.get("X-System-ID")
        if header_value:
            try:
                return int(header_value)
            except (ValueError, TypeError):
                pass

        return None
