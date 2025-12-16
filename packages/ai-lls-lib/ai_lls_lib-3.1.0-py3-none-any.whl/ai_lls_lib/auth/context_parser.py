"""Auth context parser for HTTP API v2.0 events."""

import functools
import json
from collections.abc import Callable
from typing import Any


def get_user_from_event(event: dict[str, Any]) -> str | None:
    """
    Extract user ID from HTTP API v2.0 event with all possible paths.
    Handles both JWT and API key authentication contexts.

    This function handles the complexities of AWS API Gateway authorizer contexts,
    especially when EnableSimpleResponses is set to false, which wraps the
    context in a 'lambda' key.

    Args:
        event: The Lambda event from API Gateway HTTP API v2.0

    Returns:
        User ID string if found, None otherwise
    """
    request_context = event.get("requestContext", {})
    auth = request_context.get("authorizer", {})

    # Handle lambda-wrapped context (EnableSimpleResponses: false)
    # When EnableSimpleResponses is false, the authorizer context is wrapped
    lam_ctx = auth.get("lambda", auth) if isinstance(auth.get("lambda"), dict) else auth

    # Try all possible paths for user_id in priority order
    user_id = (
        # Lambda authorizer paths (most common with current setup)
        lam_ctx.get("principal_id")
        or lam_ctx.get("principalId")
        or lam_ctx.get("sub")
        or lam_ctx.get("user_id")
        or
        # JWT paths (when using JWT authorizer directly)
        auth.get("jwt", {}).get("claims", {}).get("sub")
        or
        # Direct auth paths (fallback)
        auth.get("principal_id")
        or auth.get("principalId")
        or auth.get("sub")
    )

    return str(user_id) if user_id else None


def get_email_from_event(event: dict[str, Any]) -> str | None:
    """
    Extract email from HTTP API v2.0 event.

    Args:
        event: The Lambda event from API Gateway HTTP API v2.0

    Returns:
        Email string if found, None otherwise
    """
    request_context = event.get("requestContext", {})
    auth = request_context.get("authorizer", {})

    # Handle lambda-wrapped context
    lam_ctx = auth.get("lambda", auth) if isinstance(auth.get("lambda"), dict) else auth

    # Try to get email from various locations
    email = (
        lam_ctx.get("email")
        or auth.get("jwt", {}).get("claims", {}).get("email")
        or auth.get("email")
    )

    return str(email) if email else None


def is_admin(event: dict[str, Any]) -> bool:
    """
    Check if the authenticated user has admin privileges.

    The is_admin flag is set by the authorizer based on Cognito group membership.
    API key authentication never has admin access.

    Args:
        event: The Lambda event from API Gateway HTTP API v2.0

    Returns:
        True if user is an admin, False otherwise
    """
    request_context = event.get("requestContext", {})
    auth = request_context.get("authorizer", {})

    # Handle lambda-wrapped context
    lam_ctx = auth.get("lambda", auth) if isinstance(auth.get("lambda"), dict) else auth

    # Check is_admin from authorizer context (set as string 'true' or 'false')
    is_admin_str = lam_ctx.get("is_admin", "false")

    # Handle both string and boolean values
    if isinstance(is_admin_str, bool):
        return is_admin_str
    return str(is_admin_str).lower() == "true"


def get_groups_from_event(event: dict[str, Any]) -> list[str]:
    """
    Extract user groups from HTTP API v2.0 event.

    Groups are passed as a comma-separated string in the authorizer context.

    Args:
        event: The Lambda event from API Gateway HTTP API v2.0

    Returns:
        List of group names, empty list if none
    """
    request_context = event.get("requestContext", {})
    auth = request_context.get("authorizer", {})

    # Handle lambda-wrapped context
    lam_ctx = auth.get("lambda", auth) if isinstance(auth.get("lambda"), dict) else auth

    # Groups are stored as comma-separated string
    groups_str = lam_ctx.get("groups", "")

    if not groups_str:
        return []

    return [g.strip() for g in groups_str.split(",") if g.strip()]


def require_admin(func: Callable) -> Callable:
    """
    Decorator that requires admin access for a handler function.

    Returns 403 Forbidden if the user is not an admin.

    Usage:
        @require_admin
        def handler(event, context):
            # Only runs if user is admin
            ...
    """

    @functools.wraps(func)
    def wrapper(event: dict[str, Any], context: Any) -> dict[str, Any]:
        if not is_admin(event):
            return {
                "statusCode": 403,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Admin access required"}),
            }
        result: dict[str, Any] = func(event, context)
        return result

    return wrapper


def get_auth_type(event: dict[str, Any]) -> str | None:
    """
    Get the authentication type used for this request.

    Args:
        event: The Lambda event from API Gateway HTTP API v2.0

    Returns:
        'jwt' for Cognito token auth, 'api_key' for API key auth, None if unknown
    """
    request_context = event.get("requestContext", {})
    auth = request_context.get("authorizer", {})

    # Handle lambda-wrapped context
    lam_ctx = auth.get("lambda", auth) if isinstance(auth.get("lambda"), dict) else auth

    auth_type = lam_ctx.get("auth_type")
    return str(auth_type) if auth_type else None
