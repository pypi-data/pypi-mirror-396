"""
Manager base e mixins de QuerySet
"""

from django.db import models


class OrganizationQuerySetMixin:
    """Mixin para QuerySets com métodos de organização"""

    def for_organization(self, organization_id):
        """Filtra por organização"""
        return self.filter(organization_id=organization_id)

    def for_organizations(self, organization_ids):
        """Filtra por múltiplas organizações"""
        return self.filter(organization_id__in=organization_ids)

    def with_organization_data(self):
        """
        Pré-carrega dados de organizações (evita N+1)

        Returns:
            Lista de objetos com _cached_organization
        """
        objects = list(self.all())
        from shared_auth.utils import get_organization_model

        if not objects:
            return objects

        # Coletar IDs únicos
        org_ids = set(obj.organization_id for obj in objects)

        # Buscar todas de uma vez
        Organization = get_organization_model()
        organizations = {
            org.pk: org for org in Organization.objects.filter(pk__in=org_ids)
        }

        # Cachear nos objetos
        for obj in objects:
            obj._cached_organization = organizations.get(obj.organization_id)

        return objects


class UserQuerySetMixin:
    """Mixin para QuerySets com métodos de usuário"""

    def for_user(self, user_id):
        """Filtra por usuário"""
        return self.filter(user_id=user_id)

    def for_users(self, user_ids):
        """Filtra por múltiplos usuários"""
        return self.filter(user_id__in=user_ids)

    def with_user_data(self):
        """
        Pré-carrega dados de usuários (evita N+1)
        """
        from shared_auth.utils import get_user_model

        objects = list(self.all())

        if not objects:
            return objects

        user_ids = set(obj.user_id for obj in objects)

        User = get_user_model()
        users = {user.pk: user for user in User.objects.filter(pk__in=user_ids)}

        for obj in objects:
            obj._cached_user = users.get(obj.user_id)

        return objects


class OrganizationUserQuerySetMixin(OrganizationQuerySetMixin, UserQuerySetMixin):
    """Mixin combinado com todos os métodos"""

    def with_auth_data(self):
        """
        Pré-carrega dados de organizações E usuários (evita N+1)
        """
        from shared_auth.utils import get_organization_model, get_user_model

        objects = list(self.all())

        if not objects:
            return objects

        # Coletar IDs
        org_ids = set(obj.organization_id for obj in objects)
        user_ids = set(obj.user_id for obj in objects)

        # Buscar em batch
        Organization = get_organization_model()
        User = get_user_model()

        organizations = {
            org.pk: org for org in Organization.objects.filter(pk__in=org_ids)
        }

        users = {user.pk: user for user in User.objects.filter(pk__in=user_ids)}

        # Cachear
        for obj in objects:
            obj._cached_organization = organizations.get(obj.organization_id)
            obj._cached_user = users.get(obj.user_id)

        return objects

    def create_with_validation(self, organization_id, user_id, **kwargs):
        """
        Cria objeto com validação de organização e usuário
        """
        from shared_auth.utils import get_member_model, get_organization_model

        # Valida organização
        Organization = get_organization_model()
        Organization.objects.get_or_fail(organization_id)

        # Valida usuário pertence à organização
        Member = get_member_model()
        if not Member.objects.filter(
            user_id=user_id, organization_id=organization_id
        ).exists():
            raise ValueError(
                f"Usuário {user_id} não pertence à organização {organization_id}"
            )

        return self.create(organization_id=organization_id, user_id=user_id, **kwargs)


class BaseAuthManager(models.Manager):
    """Manager base com suporte aos mixins"""

    def get_queryset(self):
        # Detecta qual mixin está sendo usado
        model_bases = [base.__name__ for base in self.model.__bases__]

        if "OrganizationUserMixin" in model_bases:
            qs_class = type(
                "QuerySet", (OrganizationUserQuerySetMixin, models.QuerySet), {}
            )
        elif "OrganizationMixin" in model_bases:
            qs_class = type(
                "QuerySet", (OrganizationQuerySetMixin, models.QuerySet), {}
            )
        elif "UserMixin" in model_bases:
            qs_class = type("QuerySet", (UserQuerySetMixin, models.QuerySet), {})
        else:
            return super().get_queryset()

        return qs_class(self.model, using=self._db)
