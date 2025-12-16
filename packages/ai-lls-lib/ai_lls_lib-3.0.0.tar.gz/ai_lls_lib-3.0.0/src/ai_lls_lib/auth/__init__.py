"""Auth module for handling authentication and authorization."""

from .context_parser import (
    get_auth_type,
    get_email_from_event,
    get_groups_from_event,
    get_user_from_event,
    is_admin,
    require_admin,
)

__all__ = [
    "get_user_from_event",
    "get_email_from_event",
    "is_admin",
    "require_admin",
    "get_groups_from_event",
    "get_auth_type",
]
