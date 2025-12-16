"""
Sistema de permissões para shared_auth
"""

# Re-export from helpers
# Re-export from cache
from .cache import (
    clear_permissions_cache,
    get_cached_all_permissions,
    get_cached_group_permissions,
    get_cached_member,
    get_cached_member_group,
    get_cached_permission_codenames,
    init_permissions_cache,
    warmup_permissions_cache,
)
from .helpers import (
    get_organization_permission_codenames,
    get_organization_permissions,
    get_user_permission_codenames,
    get_user_permissions,
    user_has_all_permissions,
    user_has_any_permission,
    user_has_permission,
)

__all__ = [
    # Helpers
    "user_has_permission",
    "get_user_permissions",
    "get_user_permission_codenames",
    "get_organization_permissions",
    "get_organization_permission_codenames",
    "user_has_any_permission",
    "user_has_all_permissions",
    # Cache
    "get_cached_member",
    "get_cached_member_group",
    "get_cached_group_permissions",
    "get_cached_permission_codenames",
    "get_cached_all_permissions",
    "warmup_permissions_cache",
    "clear_permissions_cache",
    "init_permissions_cache",
]
