"""
Mixins relacionados a Organization
"""

from django.db import models
from rest_framework import status, viewsets
from rest_framework.response import Response

from shared_auth.managers.base import BaseAuthManager


class OrganizationMixin(models.Model):
    """
    Mixin para models que pertencem a uma organização

    Adiciona:
    - Campo organization_id
    - Property organization (lazy loading)
    - Métodos úteis

    Usage:
        class Rascunho(OrganizationMixin):
            titulo = models.CharField(max_length=200)

        # Uso
        rascunho.organization  # Acessa organização automaticamente
        rascunho.organization_members  # Acessa membros
    """

    organization_id = models.IntegerField(
        db_index=True,
        help_text="ID da organização no sistema de autenticação",
        null=True,
        default=None,
    )
    objects = BaseAuthManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["organization_id"]),
        ]

    @classmethod
    def prefetch_organizations(cls, queryset, request, org_ids=None):
        if not hasattr(request, "_orgs_dict"):
            from shared_auth.utils import get_organization_model

            Organization = get_organization_model()
            if org_ids is None:
                org_ids = list(
                    queryset.values_list("organization_id", flat=True).distinct()
                )
            if not org_ids:
                request._orgs_dict = {}
                return queryset

            orgs_qs = Organization.objects.filter(pk__in=org_ids)
            request._orgs_dict = {org.pk: org for org in orgs_qs}

        return queryset

    @property
    def organization(self):
        if not hasattr(self, "_cached_organization"):
            from shared_auth.utils import get_organization_model

            Organization = get_organization_model()
            self._cached_organization = Organization.objects.get_or_fail(
                self.organization_id
            )
        return self._cached_organization

    @property
    def organization_members(self):
        """Retorna membros da organização"""
        return self.organization.members

    @property
    def organization_users(self):
        """Retorna usuários da organização"""
        return self.organization.users

    def is_organization_active(self):
        """Verifica se a organização está ativa"""
        return self.organization.is_active()

    def get_organization_name(self):
        """Retorna nome da organização (safe)"""
        try:
            return self.organization.name
        except Exception:
            return None


class LoggedOrganizationPermMixin:
    """
    Mixin para ViewSets que dependem de uma organização logada.
    Integra com a lib maquinaweb-shared-auth.

    NÃO use diretamente. Use LoggedOrganizationViewSet.
    """

    def get_organization_id(self):
        """Obtém o ID da organização logada via maquinaweb-shared-auth"""
        return getattr(self.request, "organization_id", None)

    def get_organization_ids(self):
        """Obtém os IDs das organizações permitidas via maquinaweb-shared-auth"""
        return getattr(self.request, "organization_ids", [])

    def get_user(self):
        """Obtém o usuário atual autenticado"""
        return self.request.user

    def get_system_id(self):
        """
        Obtém o ID do sistema.

        Busca em:
        1. Settings SYSTEM_ID
        2. Header X-System-ID
        """
        from django.conf import settings

        system_id = getattr(settings, "SYSTEM_ID", None)
        if system_id:
            return system_id

        # Tentar pegar do header
        header_value = self.request.headers.get("X-System-ID")
        if header_value:
            try:
                return int(header_value)
            except (ValueError, TypeError):
                pass

        return None

    def check_logged_organization(self):
        """Verifica se há uma organização logada"""
        return self.get_organization_id() is not None

    def require_logged_organization(self):
        """Retorna erro se não houver organização logada"""
        if not self.check_logged_organization():
            return Response(
                {
                    "detail": "Nenhuma organização logada. Defina uma organização antes de continuar."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def get_queryset(self):
        """Filtra os objetos pela organização logada, se aplicável"""
        queryset = super().get_queryset()

        response = self.require_logged_organization()
        if response:
            return queryset.none()

        organization_id = self.get_organization_id()
        if hasattr(queryset.model, "organization_id"):
            return queryset.filter(organization_id=organization_id)
        elif hasattr(queryset.model, "organization"):
            return queryset.filter(organization_id=organization_id)
        return queryset

    def perform_create(self, serializer):
        """Define a organização automaticamente ao criar um objeto"""
        response = self.require_logged_organization()
        if response:
            # CORRIGIDO: Lançar exceção em vez de retornar Response
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Nenhuma organização logada.")

        organization_id = self.get_organization_id()

        if "organization" in serializer.fields:
            serializer.save(organization_id=organization_id)
        else:
            serializer.save()


class LoggedOrganizationMixin(LoggedOrganizationPermMixin, viewsets.ModelViewSet):
    """
    Mixin combinado para ViewSets com suporte a organização logada.
    Deve ser usado após RequirePermissionMixin na herança.
    """

    pass


class PrefetchOrganizationsMixin(LoggedOrganizationMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        return OrganizationMixin.prefetch_organizations(queryset, self.request)
