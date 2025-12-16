"""
Manager para SharedOrganization
"""

from django.db import models

from shared_auth.exceptions import OrganizationNotFoundError


class SharedOrganizationManager(models.Manager):
    """Manager para SharedOrganization com métodos úteis"""

    def get_or_fail(self, organization_id):
        """
        Busca organização ou lança exceção customizada

        Usage:
            org = SharedOrganization.objects.get_or_fail(123)
        """
        try:
            return self.get(pk=organization_id)
        except self.model.DoesNotExist:
            raise OrganizationNotFoundError(
                f"Organização com ID {organization_id} não encontrada"
            )

    def active(self):
        """Retorna apenas organizações ativas (não deletadas)"""
        return self.filter(deleted_at__isnull=True)

    def branches(self):
        """Retorna apenas filiais"""
        return self.filter(is_branch=True)

    def main_organizations(self):
        """Retorna apenas organizações principais"""
        return self.filter(is_branch=False)

    def by_cnpj(self, cnpj):
        """Busca por CNPJ"""
        import re

        clean_cnpj = re.sub(r"[^0-9]", "", cnpj)
        return self.filter(cnpj__contains=clean_cnpj).first()
