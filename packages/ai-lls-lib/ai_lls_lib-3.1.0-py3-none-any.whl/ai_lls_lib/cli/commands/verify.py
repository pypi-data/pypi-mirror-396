"""
Verification commands - direct phone verification bypassing API
"""

import json

import click

from ai_lls_lib.cli.aws_client import AWSClient
from ai_lls_lib.core.cache import DynamoDBCache
from ai_lls_lib.core.verifier import PhoneVerifier
from ai_lls_lib.providers import ExternalAPIProvider


@click.group(name="verify")
def verify_group():
    """Phone verification commands"""
    pass


@verify_group.command(name="phone")
@click.argument("phone_number")
@click.option(
    "--output",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="json",
    help="Output format",
)
@click.option("--no-cache", is_flag=True, help="Disable caching even if AWS is available")
@click.option("--stack", default="landline-api", help="CloudFormation stack name (for caching)")
@click.option("--profile", help="AWS profile to use (for caching)")
@click.option("--region", help="AWS region (for caching)")
@click.option("--verbose", is_flag=True, help="Show detailed output")
def verify_phone(phone_number, output, no_cache, stack, profile, region, verbose):
    """
    Verify a phone number (works with or without AWS).

    Accepts phone numbers in various formats:
      - 6197966726 (10 digits)
      - 16197966726 (11 digits with 1)
      - +16197966726 (E.164 format)
      - 619-796-6726 (with dashes)
      - (619) 796-6726 (with parentheses)
    """
    provider_instance = ExternalAPIProvider()
    if verbose:
        click.echo("Using ExternalAPIProvider (real API calls)")

    # Try to set up caching if not explicitly disabled
    cache = None

    if not no_cache:
        try:
            aws = AWSClient(region=region, profile=profile)
            cache_table = aws.get_table_name(stack, "PhoneCacheTable")
            cache = DynamoDBCache(table_name=cache_table)
            if verbose:
                click.echo(f"Using DynamoDB cache table: {cache_table}")
        except Exception as e:
            if verbose:
                click.echo(f"Cache not available: {e}")
                click.echo("Continuing without cache (direct API calls)")
    else:
        if verbose:
            click.echo("Cache explicitly disabled with --no-cache")

    # Initialize verifier (works with or without cache)
    verifier = PhoneVerifier(cache=cache, provider=provider_instance)

    try:
        # Verify the phone number
        result = verifier.verify(phone_number)
        result_dict = result.dict() if hasattr(result, "dict") else result

        # Prepare clean output
        # Extract line type value if it's an enum
        line_type = result_dict["line_type"]
        if hasattr(line_type, "value"):
            line_type = line_type.value

        # Build clean output dictionary
        output_data = {
            "phone": result_dict["phone_number"],
            "line_type": line_type,
            "dnc": result_dict["dnc"],
            "cached": result_dict.get("cached", False),
            "verified_at": str(result_dict.get("verified_at", "Unknown")),
        }

        if output == "json":
            # JSON output (default for composability)
            click.echo(json.dumps(output_data, indent=2))
        else:
            # Text output (human-readable)
            click.echo(f"Phone: {output_data['phone']}")
            click.echo(f"Line Type: {output_data['line_type']}")
            click.echo(f"DNC: {output_data['dnc']}")
            click.echo(f"Cached: {output_data['cached']}")
            click.echo(f"Verified: {output_data['verified_at']}")

    except ValueError as e:
        if output == "json":
            error_data = {"error": str(e)}
            click.echo(json.dumps(error_data), err=True)
        else:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nSupported formats:", err=True)
            click.echo("  6197966726      (10 digits)", err=True)
            click.echo("  16197966726     (11 digits)", err=True)
            click.echo("  +16197966726    (E.164)", err=True)
            click.echo("  619-796-6726    (with dashes)", err=True)
            click.echo("  (619) 796-6726  (with parentheses)", err=True)
        import sys

        sys.exit(1)
    except Exception as e:
        if output == "json":
            error_data = {"error": str(e)}
            click.echo(json.dumps(error_data), err=True)
        else:
            click.echo(f"Verification failed: {e}", err=True)
            if verbose:
                import traceback

                click.echo(traceback.format_exc(), err=True)
        import sys

        sys.exit(1)


@verify_group.command(name="bulk")
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--output", "-o", help="Output CSV file")
@click.option("--no-cache", is_flag=True, help="Disable caching even if AWS is available")
@click.option("--stack", default="landline-api", help="CloudFormation stack name (for caching)")
@click.option("--profile", help="AWS profile to use (for caching)")
@click.option("--region", help="AWS region (for caching)")
@click.option("--verbose", is_flag=True, help="Show detailed output")
def verify_bulk(csv_file, output, no_cache, stack, profile, region, verbose):
    """Process a CSV file for bulk verification"""
    from ai_lls_lib.core.processor import BulkProcessor

    provider_instance = ExternalAPIProvider()
    if verbose:
        click.echo("Using ExternalAPIProvider (real API calls)")

    # Try to set up caching if not explicitly disabled
    cache = None

    if not no_cache:
        try:
            aws = AWSClient(region=region, profile=profile)
            cache_table = aws.get_table_name(stack, "PhoneCacheTable")
            cache = DynamoDBCache(table_name=cache_table)
            if verbose:
                click.echo(f"Using DynamoDB cache table: {cache_table}")
        except Exception as e:
            if verbose:
                click.echo(f"Cache not available: {e}")
                click.echo("Continuing without cache (direct API calls)")
    else:
        if verbose:
            click.echo("Cache explicitly disabled with --no-cache")

    # Initialize verifier (works with or without cache)
    verifier = PhoneVerifier(cache=cache, provider=provider_instance)
    processor = BulkProcessor(verifier=verifier)

    click.echo(f"Processing {csv_file}...")

    try:
        # Process CSV
        results = processor.process_csv_sync(csv_file)
        click.echo(f"\nProcessed {len(results)} phone numbers")

        # Show summary
        mobile_count = sum(1 for r in results if r.line_type == "mobile")
        landline_count = sum(1 for r in results if r.line_type == "landline")
        dnc_count = sum(1 for r in results if r.dnc)
        cached_count = sum(1 for r in results if r.cached)

        click.echo("\nSummary:")
        click.echo(f"  Mobile: {mobile_count}")
        click.echo(f"  Landline: {landline_count}")
        click.echo(f"  On DNC: {dnc_count}")
        if cache:
            click.echo(f"  From Cache: {cached_count}")

        # Generate output if requested
        if output:
            processor.generate_results_csv(csv_file, results, output)
            click.echo(f"\nResults saved to: {output}")

    except Exception as e:
        click.echo(f"Bulk processing failed: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
