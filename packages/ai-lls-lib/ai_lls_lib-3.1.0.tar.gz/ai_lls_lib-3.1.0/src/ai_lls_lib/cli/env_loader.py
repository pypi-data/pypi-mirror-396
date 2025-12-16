"""Environment variable loader for CLI commands."""

import os
from pathlib import Path

import click


def load_env_file(env_path: Path, verbose: bool = False) -> dict[str, str]:
    """Load environment variables from a .env file."""
    env_vars = {}
    if env_path.exists():
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Remove quotes if present
                        value = value.strip().strip('"').strip("'")
                        env_vars[key.strip()] = value
        except Exception as e:
            if verbose:
                click.echo(f"Warning: Could not read {env_path}: {e}", err=True)
    return env_vars


def load_environment_config() -> dict[str, str]:
    """
    Load environment variables from multiple sources in order:
    1. ~/.lls/.env (user global config)
    2. ./.env (project local config)
    3. System environment variables (highest priority)

    Returns merged dictionary with system env taking precedence.
    """
    env_vars = {}

    # Load from ~/.lls/.env
    home_env = Path.home() / ".lls" / ".env"
    if home_env.exists():
        home_vars = load_env_file(home_env)
        env_vars.update(home_vars)
        click.echo(f"Loaded {len(home_vars)} variables from {home_env}", err=True)

    # Load from ./.env
    local_env = Path(".env")
    if local_env.exists():
        local_vars = load_env_file(local_env)
        env_vars.update(local_vars)
        click.echo(f"Loaded {len(local_vars)} variables from {local_env}", err=True)

    # System environment variables override file-based ones
    env_vars.update(os.environ)

    return env_vars


def get_stripe_key(environment: str, env_vars: dict[str, str] | None = None) -> str | None:
    """
    Get Stripe API key for the specified environment.

    Looks for keys in this order:
    1. STAGING_STRIPE_SECRET_KEY or PROD_STRIPE_SECRET_KEY (based on environment)
    2. STRIPE_SECRET_KEY (fallback)

    Args:
        environment: 'staging' or 'production'
        env_vars: Optional pre-loaded environment variables

    Returns:
        Stripe API key or None if not found
    """
    if env_vars is None:
        env_vars = load_environment_config()

    # Map environment names to prefixes
    env_prefix_map = {"staging": "STAGING", "production": "PROD"}
    if environment not in env_prefix_map:
        raise ValueError(f"Invalid environment '{environment}'. Must be 'staging' or 'production'")
    env_prefix = env_prefix_map[environment]

    # Try environment-specific key first
    env_key = f"{env_prefix}_STRIPE_SECRET_KEY"
    if env_key in env_vars:
        return env_vars[env_key]

    # Fall back to generic key
    if "STRIPE_SECRET_KEY" in env_vars:
        return env_vars["STRIPE_SECRET_KEY"]

    return None


def get_env_variable(
    key: str, environment: str | None = None, env_vars: dict[str, str] | None = None
) -> str | None:
    """
    Get an environment variable, optionally with environment prefix.

    Args:
        key: Variable name (e.g., 'API_URL')
        environment: Optional environment ('staging' or 'production')
        env_vars: Optional pre-loaded environment variables

    Returns:
        Variable value or None if not found
    """
    if env_vars is None:
        env_vars = load_environment_config()

    if environment:
        env_prefix_map = {"staging": "STAGING", "production": "PROD"}
        if environment not in env_prefix_map:
            raise ValueError(
                f"Invalid environment '{environment}'. Must be 'staging' or 'production'"
            )
        env_prefix = env_prefix_map[environment]

        # Try environment-specific key first
        env_key = f"{env_prefix}_{key}"
        if env_key in env_vars:
            return env_vars[env_key]

    # Fall back to non-prefixed key
    return env_vars.get(key)
