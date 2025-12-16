from shared_auth.conf import get_db_router


class SharedAuthRouter:
    """
    Direciona queries dos models compartilhados para o banco correto
    """

    route_app_labels = {"shared_auth", "auth", "admin", "contenttypes"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return get_db_router()
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return get_db_router()
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Bloqueia migrations"""
        if app_label in self.route_app_labels:
            return False
        return None
