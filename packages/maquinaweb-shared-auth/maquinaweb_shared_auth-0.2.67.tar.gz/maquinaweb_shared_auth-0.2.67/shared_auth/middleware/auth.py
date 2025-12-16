"""
Middleware de autenticação
"""

from django.utils.deprecation import MiddlewareMixin

from shared_auth.utils import get_token_model, get_user_model


class SharedAuthMiddleware(MiddlewareMixin):
    """
    Middleware que autentica usuário baseado no token do header

    Usage em settings.py:
        MIDDLEWARE = [
            ...
            'shared_auth.middleware.SharedAuthMiddleware',
        ]

    O middleware busca o token em:
    - Header: Authorization: Token <token>
    - Header: X-Auth-Token: <token>
    - Cookie: auth_token
    """

    def process_request(self, request):
        from shared_auth.permissions.cache import init_permissions_cache

        init_permissions_cache(request)

        # Caminhos que não precisam de autenticação
        exempt_paths = getattr(
            request,
            "auth_exempt_paths",
            [
                "/api/auth/login/",
                "/api/auth/register/",
                "/health/",
                "/static/",
            ],
        )

        if any(request.path.startswith(path) for path in exempt_paths):
            return None

        # Extrair token
        token = self._get_token_from_request(request)

        if not token:
            # request.user = None
            request.auth = None
            return None

        # Validar token e buscar usuário
        Token = get_token_model()
        User = get_user_model()

        try:
            token_obj = Token.objects.get(key=token)
            user = User.objects.get(pk=token_obj.user_id)

            if not user.is_active or user.deleted_at is not None:
                # request.user = None
                request.auth = None
                return None

            # Adicionar ao request
            if user:
                request.user = user
                request.auth = token_obj

        except (Token.DoesNotExist, User.DoesNotExist):
            # request.user = None
            request.auth = None

        return None

    def _get_token_from_request(self, request):
        """Extrai token do request"""
        # Header: Authorization: Token <token>
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Token "):
            return auth_header.split(" ")[1]

        # Header: X-Auth-Token
        token = request.META.get("HTTP_X_AUTH_TOKEN")
        if token:
            return token

        # Cookie
        token = request.COOKIES.get("auth_token")
        if token:
            return token

        return None


class RequireAuthMiddleware(MiddlewareMixin):
    """
    Middleware que FORÇA autenticação em todas as rotas
    Retorna 401 se não estiver autenticado

    Usage em settings.py:
        MIDDLEWARE = [
            'shared_auth.middleware.SharedAuthMiddleware',
            'shared_auth.middleware.RequireAuthMiddleware',
        ]
    """

    def process_request(self, request):
        from django.http import JsonResponse

        # Caminhos públicos
        public_paths = getattr(
            request,
            "public_paths",
            [
                "/api/auth/",
                "/health/",
                "/docs/",
                "/static/",
            ],
        )

        if any(request.path.startswith(path) for path in public_paths):
            return None

        # Verificar se está autenticado
        if not hasattr(request, "user") or request.user is None:
            return JsonResponse(
                {
                    "error": "Autenticação necessária",
                    "detail": "Token não fornecido ou inválido",
                },
                status=401,
            )

        return None
