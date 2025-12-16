"""Stripe management CLI commands."""

import json
from typing import Any

import click

from ..env_loader import get_stripe_key


@click.group(name="stripe")
def stripe_group() -> None:
    """Manage Stripe products and prices."""
    pass


@stripe_group.command("seed")
@click.option("--environment", type=click.Choice(["staging", "production"]), required=True)
@click.option("--api-key", help="Stripe API key (overrides environment)")
@click.option("--dry-run", is_flag=True, help="Show what would be created without making changes")
def seed_products(environment: str, api_key: str | None, dry_run: bool) -> None:
    """Create or update Stripe products and prices with metadata."""
    try:
        import stripe
    except ImportError:
        click.echo("Error: stripe package not installed. Run: pip install stripe", err=True)
        return

    # Load API key from environment if not provided
    if not api_key:
        api_key = get_stripe_key(environment)
        if not api_key:
            env_prefix = "STAGING" if environment == "staging" else "PROD"
            click.echo(f"Error: No Stripe API key found for {environment} environment", err=True)
            click.echo(f"Set {env_prefix}_STRIPE_SECRET_KEY or STRIPE_SECRET_KEY", err=True)
            return
        click.echo(f"Using Stripe key for {environment} environment", err=True)

    stripe.api_key = api_key

    # Define the products and prices to create
    products_config: list[dict[str, Any]] = [
        {
            "name": "Landline Scrubber - STANDARD",
            "description": "One-time purchase",
            "metadata": {
                "product_type": "landline_scrubber",
                "environment": environment,
                "tier": "STANDARD",
            },
            "price": {
                "unit_amount": 1000,  # $10.00
                "currency": "usd",
                "metadata": {
                    "product_type": "landline_scrubber",
                    "environment": environment,
                    "plan_type": "prepaid",
                    "tier": "STANDARD",
                    "credits": "50000",
                    "plan_credits_text": "50,000 credits",
                    "percent_off": "",
                    "active": "true",
                },
            },
        },
        {
            "name": "Landline Scrubber - POWER",
            "description": "Best value",
            "metadata": {
                "product_type": "landline_scrubber",
                "environment": environment,
                "tier": "POWER",
            },
            "price": {
                "unit_amount": 5000,  # $50.00
                "currency": "usd",
                "metadata": {
                    "product_type": "landline_scrubber",
                    "environment": environment,
                    "plan_type": "prepaid",
                    "tier": "POWER",
                    "credits": "285000",
                    "plan_credits_text": "285,000 credits",
                    "percent_off": "12.5% OFF",
                    "active": "true",
                },
            },
        },
        {
            "name": "Landline Scrubber - ELITE",
            "description": "Maximum savings",
            "metadata": {
                "product_type": "landline_scrubber",
                "environment": environment,
                "tier": "ELITE",
            },
            "price": {
                "unit_amount": 10000,  # $100.00
                "currency": "usd",
                "metadata": {
                    "product_type": "landline_scrubber",
                    "environment": environment,
                    "plan_type": "prepaid",
                    "tier": "ELITE",
                    "credits": "666660",
                    "plan_credits_text": "666,660 credits",
                    "percent_off": "25% OFF",
                    "active": "true",
                },
            },
        },
        {
            "name": "Landline Scrubber - UNLIMITED",
            "description": "Monthly subscription",
            "metadata": {
                "product_type": "landline_scrubber",
                "environment": environment,
                "tier": "UNLIMITED",
            },
            "price": {
                "unit_amount": 300000,  # $3000.00
                "currency": "usd",
                "recurring": {"interval": "month"},
                "metadata": {
                    "product_type": "landline_scrubber",
                    "environment": environment,
                    "plan_type": "postpaid",
                    "tier": "UNLIMITED",
                    "credits": "unlimited",
                    "plan_credits_text": "Unlimited",
                    "percent_off": "",
                    "active": "true",
                },
            },
        },
    ]

    if dry_run:
        click.echo("DRY RUN - Would create the following:")
        for config in products_config:
            click.echo(f"\nProduct: {config['name']}")
            click.echo(f"  Description: {config['description']}")
            click.echo(f"  Price: ${config['price']['unit_amount'] / 100:.2f}")
            if "recurring" in config["price"]:
                click.echo("  Billing: Monthly subscription")
            else:
                click.echo("  Billing: One-time payment")
        return

    created_prices = []

    for config in products_config:
        try:
            # Check if product already exists
            existing_products = stripe.Product.list(limit=100)
            product = None
            for p in existing_products.data:
                if (
                    p.metadata.get("product_type") == "landline_scrubber"
                    and p.metadata.get("environment") == environment
                    and p.metadata.get("tier") == config["metadata"]["tier"]
                    and p.active
                ):  # Only use active products
                    product = p
                    click.echo(f"Found existing product: {product.name}")
                    break

            if not product:
                # Create new product
                product = stripe.Product.create(
                    name=config["name"],
                    description=config["description"],
                    metadata=config["metadata"],
                )
                click.echo(f"Created product: {product.name}")

            # Create price (always create new prices, don't modify existing)
            price_data = {
                "product": product.id,
                "unit_amount": config["price"]["unit_amount"],
                "currency": config["price"]["currency"],
                "metadata": config["price"]["metadata"],
            }

            if "recurring" in config["price"]:
                price_data["recurring"] = config["price"]["recurring"]

            price = stripe.Price.create(**price_data)
            created_prices.append(price.id)
            amount = (price.unit_amount or 0) / 100
            click.echo(f"  Created price: {price.id} (${amount:.2f})")

        except stripe.error.StripeError as e:
            click.echo(f"Error creating {config['name']}: {e}", err=True)

    if created_prices:
        click.echo(f"\nCreated {len(created_prices)} prices for {environment} environment")
        click.echo("\nPrice IDs:")
        for price_id in created_prices:
            click.echo(f"  {price_id}")


@stripe_group.command("clean")
@click.option("--environment", type=click.Choice(["staging", "production"]), default="staging")
@click.option("--api-key", help="Stripe API key (overrides environment)")
@click.option("--force", is_flag=True, help="Skip confirmation")
def clean_products(environment: str, api_key: str | None, force: bool) -> None:
    """Remove all Landline Scrubber products and prices."""
    import stripe

    # Load API key from environment if not provided
    if not api_key:
        api_key = get_stripe_key(environment)
        if not api_key:
            click.echo(f"Error: No Stripe API key found for {environment} environment", err=True)
            return

    stripe.api_key = api_key

    if not force:
        if not click.confirm(
            f"This will DELETE all Landline Scrubber products in {environment}. Continue?"
        ):
            return

    try:
        # List all products
        products = stripe.Product.list(limit=100)
        deleted_count = 0

        for product in products.data:
            if (
                product.metadata.get("product_type") == "landline_scrubber"
                and product.metadata.get("environment") == environment
            ):
                # Archive all prices first
                prices = stripe.Price.list(product=product.id, limit=100)
                for price in prices.data:
                    if price.active:
                        stripe.Price.modify(price.id, active=False)
                        click.echo(f"  Archived price: {price.id}")

                # Archive the product
                stripe.Product.modify(product.id, active=False)
                click.echo(f"Archived product: {product.name}")
                deleted_count += 1

        click.echo(f"\nArchived {deleted_count} products in {environment} environment")

    except stripe.error.StripeError as e:
        click.echo(f"Error: {e}", err=True)


@stripe_group.command("list")
@click.option("--environment", type=click.Choice(["staging", "production"]), default="staging")
@click.option("--api-key", help="Stripe API key (overrides environment)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def list_products(environment: str, api_key: str | None, output_json: bool) -> None:
    """List all products and prices with metadata."""
    try:
        from ai_lls_lib.payment import StripeManager
    except ImportError:
        click.echo("Error: Payment module not found", err=True)
        return

    # Load API key from environment if not provided
    if not api_key:
        api_key = get_stripe_key(environment)
        if not api_key:
            env_prefix = "STAGING" if environment == "staging" else "PROD"
            click.echo(f"Error: No Stripe API key found for {environment} environment", err=True)
            click.echo(f"Set {env_prefix}_STRIPE_SECRET_KEY or STRIPE_SECRET_KEY", err=True)
            return

    try:
        manager = StripeManager(api_key=api_key, environment=environment)
        plans = manager.list_plans()

        if output_json:
            output = [plan.to_dict() for plan in plans]
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"Active plans for {environment} environment:\n")
            for plan in plans:
                click.echo(f"{plan.plan_name}:")
                click.echo(f"  Price: ${plan.plan_amount:.2f}")
                click.echo(f"  Credits: {plan.plan_credits_text}")
                click.echo(f"  Type: {plan.plan_type}")
                click.echo(f"  Reference: {plan.plan_reference}")
                if plan.percent_off:
                    click.echo(f"  Discount: {plan.percent_off}")
                click.echo()

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@stripe_group.command("webhook")
@click.option("--endpoint-url", help="Webhook endpoint URL")
@click.option("--environment", type=click.Choice(["staging", "production"]), default="staging")
@click.option("--api-key", help="Stripe API key (overrides environment)")
@click.option("--print-secret", is_flag=True, help="Print the webhook signing secret")
def setup_webhook(
    endpoint_url: str | None, environment: str, api_key: str | None, print_secret: bool
) -> None:
    """Configure or display webhook endpoint."""
    try:
        import stripe
    except ImportError:
        click.echo("Error: stripe package not installed. Run: pip install stripe", err=True)
        return

    # Load API key from environment if not provided
    if not api_key:
        api_key = get_stripe_key(environment)
        if not api_key:
            env_prefix = "STAGING" if environment == "staging" else "PROD"
            click.echo(f"Error: No Stripe API key found for {environment} environment", err=True)
            click.echo(f"Set {env_prefix}_STRIPE_SECRET_KEY or STRIPE_SECRET_KEY", err=True)
            return

    stripe.api_key = api_key
    env_prefix = "STAGING" if environment == "staging" else "PROD"

    if print_secret:
        # List existing webhooks
        webhooks = stripe.WebhookEndpoint.list(limit=10)
        if webhooks.data:
            click.echo("Existing webhook endpoints:\n")
            for webhook in webhooks.data:
                click.echo(f"URL: {webhook.url}")
                click.echo(f"ID: {webhook.id}")
                click.echo(f"Secret: {webhook.secret}")
                click.echo(f"Status: {webhook.status}")
                click.echo()
        else:
            click.echo("No webhook endpoints configured")
        return

    if not endpoint_url:
        click.echo("Error: --endpoint-url required to create webhook", err=True)
        return

    try:
        # Create webhook endpoint
        webhook = stripe.WebhookEndpoint.create(
            url=endpoint_url,
            enabled_events=[
                "checkout.session.completed",
                "customer.subscription.created",
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "invoice.payment_succeeded",
                "invoice.payment_failed",
            ],
        )

        click.echo("Webhook endpoint created:")
        click.echo(f"  URL: {webhook.url}")
        click.echo(f"  ID: {webhook.id}")
        click.echo(f"  Secret: {webhook.secret}")
        click.echo("\nAdd this to your environment:")
        click.echo(f"  {env_prefix}_STRIPE_WEBHOOK_SECRET={webhook.secret}")

    except stripe.error.StripeError as e:
        click.echo(f"Error creating webhook: {e}", err=True)
