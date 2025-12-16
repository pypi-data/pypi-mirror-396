"""Admin service for Cognito user management and administrative operations."""

import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any

try:
    import boto3
    from botocore.exceptions import ClientError

    HAS_BOTO3 = True
except ImportError:
    boto3 = None  # type: ignore[assignment]
    HAS_BOTO3 = False

logger = logging.getLogger(__name__)


class AdminService:
    """
    Service class for administrative operations on Cognito users.

    Provides methods for:
    - Listing all users
    - Creating users
    - Updating user attributes
    - Disabling/enabling users
    - Managing group membership
    - Credit adjustments (via CreditManager)
    """

    def __init__(
        self,
        user_pool_id: str | None = None,
        credits_table: str | None = None,
    ):
        """
        Initialize AdminService.

        Args:
            user_pool_id: Cognito User Pool ID (defaults to USER_POOL_ID env var)
            credits_table: DynamoDB credits table name (defaults to CREDITS_TABLE env var)
        """
        if not boto3:
            raise RuntimeError("boto3 is required for AdminService")

        self.cognito = boto3.client("cognito-idp")
        self.dynamodb = boto3.resource("dynamodb")

        self.user_pool_id = user_pool_id or os.environ.get("USER_POOL_ID")
        if not self.user_pool_id:
            raise ValueError("USER_POOL_ID must be provided or set as environment variable")

        self.credits_table_name = credits_table or os.environ.get("CREDITS_TABLE")
        self.credits_table = None
        if self.credits_table_name:
            try:
                self.credits_table = self.dynamodb.Table(self.credits_table_name)
            except Exception as e:
                logger.warning(f"Could not connect to credits table: {e}")

    def list_users(
        self,
        page: int = 1,
        per_page: int = 50,
        search: str | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        List all users with optional search filtering.

        Args:
            page: Page number (1-indexed)
            per_page: Number of users per page (max 60 for Cognito)
            search: Optional email search filter

        Returns:
            Tuple of (list of users, total count)
        """
        try:
            # Cognito limit is 60
            limit = min(per_page, 60)

            # Build list_users kwargs
            kwargs = {
                "UserPoolId": self.user_pool_id,
                "Limit": limit,
            }

            # Add email filter if searching
            if search:
                kwargs["Filter"] = f'email ^= "{search}"'

            # Paginate through results
            all_users = []
            pagination_token = None

            while True:
                if pagination_token:
                    kwargs["PaginationToken"] = pagination_token

                response = self.cognito.list_users(**kwargs)
                users = response.get("Users", [])

                for user in users:
                    user_data = self._parse_cognito_user(user)
                    # Fetch groups and set is_admin
                    groups = self._get_user_groups(user_data["username"])
                    user_data["groups"] = groups
                    user_data["is_admin"] = "admin" in groups
                    # Enrich with credits data if available
                    if self.credits_table:
                        credits_info = self._get_user_credits(user_data["user_id"])
                        user_data.update(credits_info)
                    all_users.append(user_data)

                pagination_token = response.get("PaginationToken")
                if not pagination_token:
                    break

            total = len(all_users)

            # Apply pagination
            start = (page - 1) * per_page
            end = start + per_page
            paginated_users = all_users[start:end]

            return paginated_users, total

        except ClientError as e:
            logger.error(f"Error listing users: {e}")
            raise

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        """
        Get a single user by their Cognito sub (user_id).

        Args:
            user_id: The Cognito sub identifier

        Returns:
            User data dict or None if not found
        """
        try:
            # Find user by sub
            response = self.cognito.list_users(
                UserPoolId=self.user_pool_id,
                Filter=f'sub = "{user_id}"',
                Limit=1,
            )

            users = response.get("Users", [])
            if not users:
                return None

            user_data = self._parse_cognito_user(users[0])

            # Get groups
            groups = self._get_user_groups(user_data["username"])
            user_data["groups"] = groups
            user_data["is_admin"] = "admin" in groups

            # Enrich with credits data
            if self.credits_table:
                credits_info = self._get_user_credits(user_id)
                user_data.update(credits_info)

            return user_data

        except ClientError as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    def create_user(
        self,
        email: str,
        password: str,
        is_admin: bool = False,
    ) -> dict[str, Any]:
        """
        Create a new Cognito user.

        Args:
            email: User's email address
            password: Initial password
            is_admin: Whether to add user to admin group

        Returns:
            Created user data
        """
        try:
            # Create user with suppressed welcome email
            response = self.cognito.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=email,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "email_verified", "Value": "true"},
                ],
                TemporaryPassword=password,
                MessageAction="SUPPRESS",
            )

            # Set permanent password
            self.cognito.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=email,
                Password=password,
                Permanent=True,
            )

            user_data = self._parse_cognito_user(response["User"])

            # Add to admin group if requested
            if is_admin:
                self._add_user_to_group(email, "admin")
                user_data["is_admin"] = True
                user_data["groups"] = ["admin"]
            else:
                user_data["is_admin"] = False
                user_data["groups"] = []

            logger.info(f"Created user {email}, admin={is_admin}")
            return user_data

        except ClientError as e:
            logger.error(f"Error creating user {email}: {e}")
            raise

    def update_user(
        self,
        user_id: str,
        email: str | None = None,
        password: str | None = None,
        is_admin: bool | None = None,
    ) -> dict[str, Any] | None:
        """
        Update an existing user.

        Args:
            user_id: Cognito sub identifier
            email: New email (optional)
            password: New password (optional)
            is_admin: Update admin status (optional)

        Returns:
            Updated user data
        """
        # Get current user to find username
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        username = user["username"]

        try:
            # Update email if provided
            if email and email != user.get("email"):
                self.cognito.admin_update_user_attributes(
                    UserPoolId=self.user_pool_id,
                    Username=username,
                    UserAttributes=[
                        {"Name": "email", "Value": email},
                        {"Name": "email_verified", "Value": "true"},
                    ],
                )
                logger.info(f"Updated email for user {user_id}")

            # Update password if provided
            if password:
                self.cognito.admin_set_user_password(
                    UserPoolId=self.user_pool_id,
                    Username=username,
                    Password=password,
                    Permanent=True,
                )
                logger.info(f"Updated password for user {user_id}")

            # Update admin status if provided
            if is_admin is not None:
                current_is_admin = user.get("is_admin", False)
                if is_admin and not current_is_admin:
                    self._add_user_to_group(username, "admin")
                    logger.info(f"Added user {user_id} to admin group")
                elif not is_admin and current_is_admin:
                    self._remove_user_from_group(username, "admin")
                    logger.info(f"Removed user {user_id} from admin group")

            # Return updated user
            return self.get_user(user_id)

        except ClientError as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise

    def disable_user(self, user_id: str) -> bool:
        """
        Disable a user account.

        Args:
            user_id: Cognito sub identifier

        Returns:
            True if successful
        """
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        try:
            self.cognito.admin_disable_user(
                UserPoolId=self.user_pool_id,
                Username=user["username"],
            )
            logger.info(f"Disabled user {user_id}")
            return True

        except ClientError as e:
            logger.error(f"Error disabling user {user_id}: {e}")
            raise

    def enable_user(self, user_id: str) -> bool:
        """
        Enable a disabled user account.

        Args:
            user_id: Cognito sub identifier

        Returns:
            True if successful
        """
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        try:
            self.cognito.admin_enable_user(
                UserPoolId=self.user_pool_id,
                Username=user["username"],
            )
            logger.info(f"Enabled user {user_id}")
            return True

        except ClientError as e:
            logger.error(f"Error enabling user {user_id}: {e}")
            raise

    def adjust_credits(
        self,
        user_id: str,
        amount: int,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """
        Adjust credits for a user (add or subtract).

        Args:
            user_id: User identifier
            amount: Credit amount (positive to add, negative to subtract)
            reason: Optional reason for audit logging

        Returns:
            Updated credits info
        """
        if not self.credits_table:
            raise RuntimeError("Credits table not configured")

        try:
            # Get current balance
            current = self._get_user_credits(user_id)
            current_balance = current.get("credits", 0)
            new_balance = current_balance + amount

            # Don't allow negative balance
            if new_balance < 0:
                raise ValueError(
                    f"Insufficient credits. Current: {current_balance}, requested: {amount}"
                )

            # Update credits
            self.credits_table.update_item(
                Key={"user_id": user_id},
                UpdateExpression="SET credits = :balance, updated_at = :now",
                ExpressionAttributeValues={
                    ":balance": Decimal(new_balance),
                    ":now": datetime.utcnow().isoformat(),
                },
                ReturnValues="ALL_NEW",
            )

            result = {
                "user_id": user_id,
                "previous_balance": current_balance,
                "adjustment": amount,
                "new_balance": new_balance,
                "reason": reason,
            }

            logger.info(
                f"Adjusted credits for {user_id}: {current_balance} -> {new_balance} ({amount:+d})",
                extra={"reason": reason},
            )

            return result

        except ClientError as e:
            logger.error(f"Error adjusting credits for {user_id}: {e}")
            raise

    def _parse_cognito_user(self, user: dict[str, Any]) -> dict[str, Any]:
        """Parse Cognito user response into standard format."""
        attributes = {attr["Name"]: attr["Value"] for attr in user.get("Attributes", [])}

        return {
            "user_id": attributes.get("sub", ""),
            "username": user.get("Username", ""),
            "email": attributes.get("email", ""),
            "email_verified": attributes.get("email_verified", "false") == "true",
            "status": user.get("UserStatus", ""),
            "enabled": user.get("Enabled", True),
            "created_at": user.get("UserCreateDate", "").isoformat()
            if user.get("UserCreateDate")
            else None,
            "updated_at": user.get("UserLastModifiedDate", "").isoformat()
            if user.get("UserLastModifiedDate")
            else None,
        }

    def _get_user_groups(self, username: str) -> list[str]:
        """Get groups for a user."""
        try:
            response = self.cognito.admin_list_groups_for_user(
                Username=username,
                UserPoolId=self.user_pool_id,
            )
            return [g["GroupName"] for g in response.get("Groups", [])]
        except ClientError as e:
            logger.error(f"Error getting groups for {username}: {e}")
            return []

    def _add_user_to_group(self, username: str, group_name: str) -> None:
        """Add a user to a group."""
        self.cognito.admin_add_user_to_group(
            UserPoolId=self.user_pool_id,
            Username=username,
            GroupName=group_name,
        )

    def _remove_user_from_group(self, username: str, group_name: str) -> None:
        """Remove a user from a group."""
        self.cognito.admin_remove_user_from_group(
            UserPoolId=self.user_pool_id,
            Username=username,
            GroupName=group_name,
        )

    def _get_user_credits(self, user_id: str) -> dict[str, Any]:
        """Get credits info for a user from DynamoDB."""
        if not self.credits_table:
            return {"credits": 0}

        try:
            response = self.credits_table.get_item(Key={"user_id": user_id})
            if "Item" in response:
                item = response["Item"]
                subscription_status = item.get("subscription_status")
                credits_val = item.get("credits", 0)
                credits_int = 0 if credits_val is None else int(Decimal(str(credits_val)))
                return {
                    "credits": credits_int,
                    "subscription_status": subscription_status,
                    "stripe_customer_id": item.get("stripe_customer_id"),
                    "has_unlimited": subscription_status == "active",
                }
            return {"credits": 0, "has_unlimited": False}
        except ClientError as e:
            logger.error(f"Error getting credits for {user_id}: {e}")
            return {"credits": 0, "has_unlimited": False}

    def set_unlimited_access(
        self,
        user_id: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """
        Set or remove unlimited access for a user.

        Args:
            user_id: User identifier
            enabled: True to grant unlimited access, False to revoke

        Returns:
            Updated subscription info
        """
        if not self.credits_table:
            raise RuntimeError("Credits table not configured")

        try:
            status = "active" if enabled else None
            now = datetime.utcnow().isoformat()

            if enabled:
                # Set subscription_status to active
                response = self.credits_table.update_item(
                    Key={"user_id": user_id},
                    UpdateExpression="SET subscription_status = :status, updated_at = :now",
                    ExpressionAttributeValues={
                        ":status": status,
                        ":now": now,
                    },
                    ReturnValues="ALL_NEW",
                )
            else:
                # Remove subscription_status
                response = self.credits_table.update_item(
                    Key={"user_id": user_id},
                    UpdateExpression="REMOVE subscription_status SET updated_at = :now",
                    ExpressionAttributeValues={
                        ":now": now,
                    },
                    ReturnValues="ALL_NEW",
                )

            item = response.get("Attributes", {})

            result = {
                "user_id": user_id,
                "has_unlimited": enabled,
                "subscription_status": item.get("subscription_status"),
            }

            logger.info(
                f"Set unlimited access for {user_id}: {enabled}",
            )

            return result

        except ClientError as e:
            logger.error(f"Error setting unlimited access for {user_id}: {e}")
            raise
