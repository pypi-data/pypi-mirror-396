"""
Mixin para verificação de permissões
"""

from rest_framework import status
from rest_framework.response import Response


class RequirePermissionMixin:
    required_permission = None
    required_permissions = None
    base_permission = None
    translate_action_to_perm = {
        "list": "view",
        "retrieve": "view",
        "create": "add",
        "update": "change",
        "partial_update": "change",
        "destroy": "delete",
    }

    def check_permissions(self, request):
        if hasattr(super(), "check_permissions"):
            super().check_permissions(request)

        if self.base_permission and self.action in self.translate_action_to_perm:
            perm = f"{self.translate_action_to_perm.get(self.action)}_{self.base_permission}"
            if not self.check_permission(perm):
                self.permission_denied(
                    request, message=f"Permissão '{perm}' necessária."
                )
        if self.required_permission:
            if not self.check_permission(self.required_permission):
                self.permission_denied(
                    request,
                    message=f"Permissão '{self.required_permission}' necessária.",
                )
        if self.required_permissions:
            has_any = any(
                self.check_permission(perm) for perm in self.required_permissions
            )
            if not has_any:
                self.permission_denied(
                    request,
                    message=f"Uma das permissões necessárias: {', '.join(self.required_permissions)}",
                )

    def check_permission(self, permission_codename):
        """
        Verifica se usuário tem permissão específica.

        OTIMIZADO: Passa request para habilitar cache de permissões.

        Args:
            permission_codename: Código da permissão (ex: 'create_invoices')

        Returns:
            bool: True se tem permissão

        Usage:
            if self.check_permission('create_invoices'):
                # Usuário pode criar faturas
                pass
        """
        from shared_auth.permissions import user_has_permission

        system_id = self.get_system_id()
        if not system_id:
            return False

        organization_id = self.get_organization_id()
        if not organization_id:
            return False

        user = self.get_user()
        if not user or not user.is_authenticated:
            return False

        return user_has_permission(
            user.id,
            organization_id,
            permission_codename,
            system_id,
            request=getattr(self, "request", None),
        )

    def require_permission(self, permission_codename):
        """
        Retorna erro se usuário não tiver permissão.

        Args:
            permission_codename: Código da permissão

        Returns:
            Response com erro 403 ou None se tem permissão

        Usage:
            response = self.require_permission('create_invoices')
            if response:
                return response
        """
        if not self.check_permission(permission_codename):
            return Response(
                {"detail": f"Permissão '{permission_codename}' necessária."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def get_user_permissions(self):
        """
        Lista todas as permissões do usuário no sistema atual.

        Returns:
            list[Permission]: Permissões do usuário

        Usage:
            perms = self.get_user_permissions()
            for perm in perms:
                print(perm.codename)
        """
        from shared_auth.permissions import get_user_permissions

        system_id = self.get_system_id()
        if not system_id:
            return []

        organization_id = self.get_organization_id()
        if not organization_id:
            return []

        user = self.get_user()
        if not user or not user.is_authenticated:
            return []

        return get_user_permissions(
            user.id, organization_id, system_id, request=getattr(self, "request", None)
        )

    def get_user_permission_codenames(self):
        """
        Lista codenames das permissões do usuário.

        Returns:
            List[str]: Lista de codenames

        Usage:
            codenames = self.get_user_permission_codenames()
            # ['create_invoices', 'edit_invoices']
        """
        return [perm.codename for perm in self.get_user_permissions()]
