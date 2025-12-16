"""
AWS client utilities for CLI operations
"""

import os
from typing import Any

import boto3
import click
from botocore.exceptions import ClientError


class AWSClient:
    """Wrapper for AWS operations with proper error handling"""

    def __init__(self, region: str | None = None, profile: str | None = None):
        """Initialize AWS clients"""
        self.region = region or os.environ.get("AWS_REGION", "us-east-1")
        self.profile = profile

        # Create session
        if profile:
            self.session = boto3.Session(profile_name=profile, region_name=self.region)
        else:
            self.session = boto3.Session(region_name=self.region)

        # Lazy-load clients
        self._dynamodb: Any = None
        self._s3: Any = None
        self._sqs: Any = None
        self._secretsmanager: Any = None
        self._cloudformation: Any = None
        self._logs: Any = None

    @property
    def dynamodb(self) -> Any:
        """Get DynamoDB client"""
        if not self._dynamodb:
            self._dynamodb = self.session.resource("dynamodb")
        return self._dynamodb

    @property
    def s3(self) -> Any:
        """Get S3 client"""
        if not self._s3:
            self._s3 = self.session.client("s3")
        return self._s3

    @property
    def sqs(self) -> Any:
        """Get SQS client"""
        if not self._sqs:
            self._sqs = self.session.client("sqs")
        return self._sqs

    @property
    def secretsmanager(self) -> Any:
        """Get Secrets Manager client"""
        if not self._secretsmanager:
            self._secretsmanager = self.session.client("secretsmanager")
        return self._secretsmanager

    @property
    def cloudformation(self) -> Any:
        """Get CloudFormation client"""
        if not self._cloudformation:
            self._cloudformation = self.session.client("cloudformation")
        return self._cloudformation

    @property
    def logs(self) -> Any:
        """Get CloudWatch Logs client"""
        if not self._logs:
            self._logs = self.session.client("logs")
        return self._logs

    def get_stack_outputs(self, stack_name: str) -> dict[str, str]:
        """Get CloudFormation stack outputs"""
        try:
            response = self.cloudformation.describe_stacks(StackName=stack_name)
            stack = response["Stacks"][0]
            outputs = {}
            for output in stack.get("Outputs", []):
                outputs[output["OutputKey"]] = output["OutputValue"]
            return outputs
        except ClientError as e:
            if e.response["Error"]["Code"] == "ValidationError":
                raise click.ClickException(f"Stack '{stack_name}' not found") from None
            raise

    def get_table_name(self, stack_name: str, logical_name: str) -> str:
        """Get actual table name from stack"""
        try:
            response = self.cloudformation.describe_stack_resource(
                StackName=stack_name, LogicalResourceId=logical_name
            )
            return str(response["StackResourceDetail"]["PhysicalResourceId"])
        except ClientError:
            # Fallback to conventional naming
            return f"{stack_name}-{logical_name.lower()}"

    def scan_table(self, table_name: str, limit: int = 100) -> list[Any]:
        """Scan DynamoDB table"""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.scan(Limit=limit)
            return list(response.get("Items", []))
        except ClientError as e:
            raise click.ClickException(f"Error scanning table: {e}") from e

    def put_item(self, table_name: str, item: dict[str, Any]) -> None:
        """Put item to DynamoDB"""
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=item)
        except ClientError as e:
            raise click.ClickException(f"Error putting item: {e}") from e

    def delete_item(self, table_name: str, key: dict[str, Any]) -> None:
        """Delete item from DynamoDB"""
        try:
            table = self.dynamodb.Table(table_name)
            table.delete_item(Key=key)
        except ClientError as e:
            raise click.ClickException(f"Error deleting item: {e}") from e
