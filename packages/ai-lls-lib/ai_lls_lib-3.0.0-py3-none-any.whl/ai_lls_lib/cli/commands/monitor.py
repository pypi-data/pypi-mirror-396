"""
Real-time CloudWatch log monitoring for Lambda functions
"""

import json
import time
from datetime import datetime, timedelta

import click
from botocore.exceptions import ClientError

from ai_lls_lib.cli.aws_client import AWSClient

try:
    from rich.console import Console
    from rich.panel import Panel

    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    Console = None  # type: ignore[misc,assignment]


def get_log_groups(aws_client: AWSClient, environment: str) -> list[str]:
    """Get relevant CloudWatch log groups for the environment"""
    # Map environment to stack name pattern
    stack_prefix = "landline-api-staging" if environment == "staging" else "landline-api"

    # Key Lambda functions to monitor
    lambda_functions = [
        "PhoneVerifyHandler",
        "BulkUploadHandler",
        "BulkProcessHandler",
        "PlansHandler",
        "PaymentHandler",
        "UserProfileHandler",
    ]

    log_groups = []
    for func in lambda_functions:
        log_group = f"/aws/lambda/{stack_prefix}-{func}"
        log_groups.append(log_group)

    return log_groups


def format_log_event(event: dict, use_rich: bool = True) -> str:
    """Format a CloudWatch log event for display"""
    timestamp = datetime.fromtimestamp(event.get("timestamp", 0) / 1000)
    message = event.get("message", "")

    # Try to parse JSON message
    try:
        if message.strip().startswith("{"):
            parsed = json.loads(message)

            # Check for external API calls
            if "external_api_call" in message.lower() or "landlineremover.com" in message:
                if use_rich and HAS_RICH:
                    return f"[bold green]{timestamp.strftime('%H:%M:%S')}[/bold green] [cyan]EXTERNAL API:[/cyan] {message}"
                else:
                    return f"{timestamp.strftime('%H:%M:%S')} EXTERNAL API: {message}"

            # Check for cache events
            if "cache" in message.lower():
                if use_rich and HAS_RICH:
                    return f"[bold blue]{timestamp.strftime('%H:%M:%S')}[/bold blue] [yellow]CACHE:[/yellow] {message}"
                else:
                    return f"{timestamp.strftime('%H:%M:%S')} CACHE: {message}"

            # Check for errors
            if "error" in message.lower() or "exception" in message.lower():
                if use_rich and HAS_RICH:
                    return f"[bold red]{timestamp.strftime('%H:%M:%S')}[/bold red] [red]ERROR:[/red] {message}"
                else:
                    return f"{timestamp.strftime('%H:%M:%S')} ERROR: {message}"

            # Format structured logs
            if use_rich and HAS_RICH:
                message = json.dumps(parsed, indent=2)
    except (json.JSONDecodeError, ValueError):
        pass

    # Default formatting
    if use_rich and HAS_RICH:
        return f"[dim]{timestamp.strftime('%H:%M:%S')}[/dim] {message}"
    else:
        return f"{timestamp.strftime('%H:%M:%S')} {message}"


def tail_logs(
    aws_client: AWSClient, log_groups: list[str], duration: int = 300, follow: bool = True
):
    """Tail CloudWatch logs in real-time"""
    console = Console() if HAS_RICH else None

    # Calculate start time
    start_time = int((datetime.utcnow() - timedelta(seconds=duration)).timestamp() * 1000)

    # Track last event time for each log group
    last_event_times = dict.fromkeys(log_groups, start_time)

    if console and HAS_RICH:
        console.print(
            Panel.fit(
                f"[bold cyan]Monitoring {len(log_groups)} Lambda functions[/bold cyan]\n"
                f"[dim]Press Ctrl+C to stop[/dim]",
                title="CloudWatch Log Monitor",
                border_style="cyan",
            )
        )
        console.print()
    else:
        click.echo(f"Monitoring {len(log_groups)} Lambda functions")
        click.echo("Press Ctrl+C to stop\n")

    try:
        while True:
            events_found = False

            for log_group in log_groups:
                try:
                    # Use filter_log_events for real-time tailing
                    response = aws_client.logs.filter_log_events(
                        logGroupName=log_group, startTime=last_event_times[log_group], limit=100
                    )

                    events = response.get("events", [])

                    if events:
                        events_found = True
                        # Update last event time
                        last_event_times[log_group] = events[-1]["timestamp"] + 1

                        # Display log group header
                        if console and HAS_RICH:
                            console.print(f"\n[bold magenta]═══ {log_group} ═══[/bold magenta]")
                        else:
                            click.echo(f"\n=== {log_group} ===")

                        # Display events
                        for event in events:
                            formatted = format_log_event(event, use_rich=(console is not None))
                            if console and HAS_RICH:
                                console.print(formatted)
                            else:
                                click.echo(formatted)

                except ClientError as e:
                    if e.response["Error"]["Code"] != "ResourceNotFoundException":
                        if console and HAS_RICH:
                            console.print(f"[yellow]Warning: {e}[/yellow]")
                        else:
                            click.echo(f"Warning: {e}", err=True)

            if not follow:
                break

            # Sleep briefly before next poll
            time.sleep(2 if events_found else 5)

    except KeyboardInterrupt:
        if console and HAS_RICH:
            console.print("\n[yellow]Monitoring stopped[/yellow]")
        else:
            click.echo("\nMonitoring stopped")


def start_live_tail(aws_client: AWSClient, log_groups: list[str]):
    """Start a CloudWatch Logs Live Tail session (requires AWS SDK v2)"""
    console = Console() if HAS_RICH else None

    try:
        # Start live tail session
        response = aws_client.logs.start_live_tail(
            logGroupIdentifiers=log_groups, logStreamNamePrefixes=[], logEventFilterPattern=""
        )

        session_id = response.get("sessionId")
        response.get("sessionUrl")

        if console and HAS_RICH:
            console.print(
                Panel.fit(
                    f"[bold green]Live Tail session started[/bold green]\n"
                    f"Session ID: {session_id}\n"
                    f"[dim]Note: Live Tail API requires WebSocket support[/dim]",
                    title="CloudWatch Live Tail",
                    border_style="green",
                )
            )
        else:
            click.echo("Live Tail session started")
            click.echo(f"Session ID: {session_id}")
            click.echo("Note: Live Tail API requires WebSocket support")

        # Note: Full WebSocket implementation would be needed here
        # For now, fall back to filter_log_events polling
        click.echo("\nFalling back to standard log polling...")
        tail_logs(aws_client, log_groups, duration=300, follow=True)

    except ClientError as e:
        if "start_live_tail" in str(e):
            # Fall back to regular tailing if Live Tail not available
            if console and HAS_RICH:
                console.print(
                    "[yellow]Live Tail API not available, using standard polling[/yellow]"
                )
            else:
                click.echo("Live Tail API not available, using standard polling")
            tail_logs(aws_client, log_groups, duration=300, follow=True)
        else:
            raise


@click.group(name="monitor")
def monitor_group():
    """Monitor CloudWatch logs in real-time"""
    pass


@monitor_group.command()
@click.option("--staging", is_flag=True, help="Monitor staging environment (default: production)")
@click.option("--production", is_flag=True, help="Monitor production environment")
@click.option("--duration", default=300, help="How far back to start (seconds, default: 300)")
@click.option(
    "--follow", is_flag=True, default=True, help="Follow logs in real-time (default: true)"
)
@click.option("--filter", "filter_pattern", help="CloudWatch filter pattern to apply")
@click.option("--profile", help="AWS profile to use")
@click.option("--region", default="us-east-1", help="AWS region")
def logs(staging, production, duration, follow, filter_pattern, profile, region):
    """Tail CloudWatch logs for Lambda functions

    Examples:
        ai-lls monitor logs --staging
        ai-lls monitor logs --production
        ai-lls monitor logs --staging --filter "ERROR"
        ai-lls monitor logs --duration 600 --follow
    """
    # Determine environment
    if staging and production:
        raise click.ClickException("Cannot specify both --staging and --production")

    environment = "staging" if staging else "production"

    # Show warning if Rich not installed
    if not HAS_RICH:
        click.echo("Warning: Install 'rich' library for better output formatting", err=True)
        click.echo("Run: pip install rich", err=True)
        click.echo()

    # Initialize AWS client
    aws_client = AWSClient(region=region, profile=profile)

    # Get log groups
    log_groups = get_log_groups(aws_client, environment)

    click.echo(f"Monitoring {environment} environment...")
    click.echo(f"Log groups: {', '.join([g.split('/')[-1] for g in log_groups])}")
    click.echo()

    # Start tailing logs
    tail_logs(aws_client, log_groups, duration=duration, follow=follow)


@monitor_group.command()
@click.option("--staging", is_flag=True, help="Monitor staging environment")
@click.option("--production", is_flag=True, help="Monitor production environment")
@click.option("--profile", help="AWS profile to use")
@click.option("--region", default="us-east-1", help="AWS region")
def live(staging, production, profile, region):
    """Start CloudWatch Logs Live Tail session (experimental)

    Uses the CloudWatch Logs Live Tail API for real-time streaming.
    Falls back to standard polling if Live Tail is not available.

    Examples:
        ai-lls monitor live --staging
        ai-lls monitor live --production
    """
    # Determine environment
    if staging and production:
        raise click.ClickException("Cannot specify both --staging and --production")

    environment = "staging" if staging else "production"

    # Initialize AWS client
    aws_client = AWSClient(region=region, profile=profile)

    # Get log groups
    log_groups = get_log_groups(aws_client, environment)

    click.echo(f"Starting Live Tail for {environment} environment...")

    # Start live tail
    start_live_tail(aws_client, log_groups)


# Export the group for registration
__all__ = ["monitor_group"]
