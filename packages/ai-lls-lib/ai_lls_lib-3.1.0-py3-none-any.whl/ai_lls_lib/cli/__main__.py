"""
Landline Scrubber CLI entry point
"""

import os
import sys
from pathlib import Path

import click

from ai_lls_lib.cli.commands import admin, cache, monitor, stripe, test_stack, verify
from ai_lls_lib.cli.env_loader import load_env_file


def load_env_files(verbose=False):
    """Load .env files from ~/.lls and current directory"""
    # Load from ~/.lls/.env
    home_env = Path.home() / ".lls" / ".env"
    if home_env.exists():
        env_vars = load_env_file(home_env)
        for key, value in env_vars.items():
            if key not in os.environ:  # Don't override existing env vars
                os.environ[key] = value
        if env_vars and verbose:
            click.echo(f"Loaded {len(env_vars)} variables from {home_env}", err=True)

    # Load from current directory .env
    local_env = Path(".env")
    if local_env.exists():
        env_vars = load_env_file(local_env)
        for key, value in env_vars.items():
            if key not in os.environ:  # Don't override existing env vars
                os.environ[key] = value
        if env_vars and verbose:
            click.echo(f"Loaded {len(env_vars)} variables from {local_env}", err=True)

    # Set default environment to 'prod' if not set
    if "ENVIRONMENT" not in os.environ:
        os.environ["ENVIRONMENT"] = "prod"
        if verbose:
            click.echo("Set default ENVIRONMENT=prod", err=True)


@click.group()
@click.version_option(version="0.1.0", prog_name="ai-lls")
def cli():
    """Landline Scrubber CLI - Administrative and debugging tools"""
    # Load environment files at startup
    load_env_files()


# Register command groups
cli.add_command(verify.verify_group)
cli.add_command(cache.cache_group)
cli.add_command(admin.admin_group)
cli.add_command(test_stack.test_stack_group)
cli.add_command(stripe.stripe_group)
cli.add_command(monitor.monitor_group)


def main():
    """Main entry point"""
    try:
        cli()
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
