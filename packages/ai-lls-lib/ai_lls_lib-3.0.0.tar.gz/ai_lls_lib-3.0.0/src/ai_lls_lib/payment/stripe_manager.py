"""Stripe API management with metadata conventions."""

import logging
import os
from typing import Any

try:
    import stripe

    HAS_STRIPE = True
except ImportError:
    stripe = None  # type: ignore[assignment]
    HAS_STRIPE = False

from .models import Plan

logger = logging.getLogger(__name__)


class StripeManager:
    """
    Manages Stripe resources with metadata conventions.
    Uses metadata to discover and filter products/prices.
    """

    METADATA_SCHEMA = {
        "product_type": "landline_scrubber",
        "environment": None,  # Set at runtime
        "tier": None,
        "credits": None,
        "active": "true",
    }

    def __init__(self, api_key: str | None = None, environment: str | None = None):
        """Initialize with Stripe API key and environment."""
        if not HAS_STRIPE or not stripe:
            raise ImportError("stripe package not installed. Run: pip install stripe")

        self.api_key = api_key or os.environ.get("STRIPE_SECRET_KEY")
        if not self.api_key:
            raise ValueError("Stripe API key not provided and STRIPE_SECRET_KEY not set")

        stripe.api_key = self.api_key
        self.environment = environment or os.environ.get("ENVIRONMENT", "staging")

    def list_plans(self) -> list[Plan]:
        """
        Fetch active plans from Stripe using metadata.
        Returns list of Plan objects sorted by price.
        """
        try:
            # Fetch all active prices with expanded product data
            prices = stripe.Price.list(active=True, expand=["data.product"], limit=100)

            plans = []
            for price in prices.data:
                metadata = price.metadata or {}

                # Filter by our metadata conventions
                if (
                    metadata.get("product_type") == "landline_scrubber"
                    and metadata.get("active") == "true"
                ):
                    # Convert to Plan object
                    # price.product is expanded to Product object due to expand param
                    product = price.product
                    if isinstance(product, str):
                        # Shouldn't happen with expand, but handle gracefully
                        continue
                    plan = Plan.from_stripe_price(price, product)  # type: ignore[arg-type]
                    plans.append(plan)

            # Sort by price amount
            plans.sort(key=lambda p: p.plan_amount)

            logger.info(f"Found {len(plans)} active plans for environment {self.environment}")
            return plans

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error listing plans: {e}")
            # Let error propagate - no fallback to mock data
            raise

    def create_setup_intent(self, user_id: str) -> dict[str, str]:
        """
        Create a SetupIntent for secure payment method collection.
        Frontend will confirm this with Stripe Elements.
        """
        try:
            # Get or create customer
            customer = self._get_or_create_customer(user_id)

            # Create SetupIntent
            setup_intent = stripe.SetupIntent.create(
                customer=customer.id, metadata={"user_id": user_id, "environment": self.environment}
            )

            return {
                "client_secret": setup_intent.client_secret,
                "setup_intent_id": setup_intent.id,
                "customer_id": customer.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating setup intent: {e}")
            raise

    def attach_payment_method(
        self, user_id: str, payment_method_id: str, billing_details: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Attach a payment method to customer (legacy path).
        Returns whether this is the first card.
        """
        try:
            # Get or create customer
            customer = self._get_or_create_customer(user_id)

            # Attach payment method to customer
            stripe.PaymentMethod.attach(payment_method_id, customer=customer.id)

            # Update billing details if provided
            if billing_details:
                stripe.PaymentMethod.modify(
                    payment_method_id,
                    billing_details=billing_details,  # type: ignore[arg-type]
                )

            # Check if this is the first payment method
            payment_methods = stripe.PaymentMethod.list(customer=customer.id, type="card")

            first_card = len(payment_methods.data) == 1

            # Set as default if first card
            if first_card:
                stripe.Customer.modify(
                    customer.id, invoice_settings={"default_payment_method": payment_method_id}
                )

            return {
                "payment_method_id": payment_method_id,
                "first_card": first_card,
                "customer_id": customer.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error attaching payment method: {e}")
            raise

    def verify_payment_method(self, user_id: str, payment_method_id: str) -> dict[str, Any]:
        """
        Perform $1 verification charge on new payment method.
        """
        try:
            customer = self._get_or_create_customer(user_id)

            # Create $1 verification charge
            payment_intent = stripe.PaymentIntent.create(
                amount=100,  # $1.00 in cents
                currency="usd",
                customer=customer.id,
                payment_method=payment_method_id,
                off_session=True,
                confirm=True,
                description="Card verification - $1 charge",
                metadata={
                    "user_id": user_id,
                    "type": "verification",
                    "environment": self.environment,
                },
            )

            return {"status": payment_intent.status, "payment_intent_id": payment_intent.id}

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error verifying payment method: {e}")
            raise

    def charge_prepaid(
        self, user_id: str, reference_code: str, amount: float | None = None
    ) -> dict[str, Any]:
        """
        Charge saved payment method for credit purchase.
        Supports both fixed-price and metadata-based variable-amount plans.
        """
        try:
            customer = self._get_or_create_customer(user_id)

            # Look up price from Stripe
            prices = stripe.Price.list(active=True, limit=100, expand=["data.product"])
            price = None

            for p in prices.data:
                metadata = p.metadata or {}
                # Match by price ID or plan_reference in metadata
                if (
                    p.id == reference_code
                    or metadata.get("plan_reference") == reference_code
                    or (
                        metadata.get("tier") == reference_code
                        and metadata.get("environment") == self.environment
                    )
                ):
                    price = p
                    break

            if not price:
                raise ValueError(f"Invalid plan reference: {reference_code}")

            price_metadata = price.metadata or {}

            # Check if this is a variable amount plan
            if price_metadata.get("variable_amount") == "true":
                # Variable amount plan - validate amount
                if not amount:
                    raise ValueError("Amount required for variable-amount plan")

                # Get validation rules from metadata
                min_amount = float(price_metadata.get("min_amount", "5"))
                if amount < min_amount:
                    raise ValueError(f"Amount ${amount} is below minimum ${min_amount}")

                # Check against default amounts if specified
                default_amounts_str = price_metadata.get("default_amounts", "")
                if default_amounts_str:
                    allowed_amounts = [float(x.strip()) for x in default_amounts_str.split(",")]
                    # Allow default amounts OR any amount >= minimum
                    if amount not in allowed_amounts and amount < max(allowed_amounts):
                        logger.info(
                            f"Amount ${amount} not in defaults {allowed_amounts}, but allowed as >= ${min_amount}"
                        )

                # Calculate credits based on credits_per_dollar
                credits_per_dollar = float(price_metadata.get("credits_per_dollar", "285"))
                credits_to_add = int(amount * credits_per_dollar)
                charge_amount = int(amount * 100)  # Convert to cents

            else:
                # Fixed price plan
                charge_amount = price.unit_amount or 0
                credits_str = price_metadata.get("credits", "0")
                if credits_str.lower() == "unlimited":
                    credits_to_add = 0  # Subscription handles this differently
                else:
                    credits_to_add = int(credits_str)

            # Get default payment method
            invoice_settings = customer.invoice_settings
            default_pm = (
                invoice_settings.get("default_payment_method") if invoice_settings else None
            )
            if not default_pm:
                # Try to get first payment method
                payment_methods = stripe.PaymentMethod.list(
                    customer=customer.id, type="card", limit=1
                )
                if not payment_methods.data:
                    raise ValueError("No payment method on file")
                default_pm = payment_methods.data[0].id

            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=charge_amount,
                currency="usd",
                customer=customer.id,
                payment_method=default_pm,
                off_session=True,
                confirm=True,
                description=f"Credit purchase - {credits_to_add} credits",
                metadata={
                    "user_id": user_id,
                    "credits": str(credits_to_add),
                    "reference_code": reference_code,
                    "environment": self.environment,
                },
            )

            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "credits_added": credits_to_add,
                "amount_charged": charge_amount / 100,  # Convert back to dollars
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error processing payment: {e}")
            raise

    def customer_has_payment_method(self, stripe_customer_id: str) -> bool:
        """
        Check if customer has any saved payment methods.
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=stripe_customer_id, type="card", limit=1
            )
            return len(payment_methods.data) > 0
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error checking payment methods: {e}")
            return False

    def list_payment_methods(self, stripe_customer_id: str) -> dict[str, Any]:
        """
        List all payment methods for a customer.
        """
        try:
            # Get customer to find default payment method
            customer = stripe.Customer.retrieve(stripe_customer_id)
            invoice_settings = customer.invoice_settings
            default_pm_id = (
                invoice_settings.get("default_payment_method") if invoice_settings else None
            )

            # List all payment methods
            payment_methods = stripe.PaymentMethod.list(customer=stripe_customer_id, type="card")

            items = []
            for pm in payment_methods.data:
                card = pm.card
                if card:
                    items.append(
                        {
                            "id": pm.id,
                            "brand": card.brand,
                            "last4": card.last4,
                            "exp_month": card.exp_month,
                            "exp_year": card.exp_year,
                            "is_default": pm.id == default_pm_id,
                        }
                    )

            return {"items": items, "default_payment_method_id": default_pm_id}

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error listing payment methods: {e}")
            return {"items": [], "default_payment_method_id": None}

    def _get_or_create_customer(self, user_id: str, email: str | None = None) -> Any:
        """
        Get existing Stripe customer or create new one.
        First checks by user_id in metadata, then by email if provided.
        """
        try:
            # First try to find by user_id in metadata
            search_results = stripe.Customer.search(
                query=f'metadata["user_id"]:"{user_id}"', limit=1
            )

            if search_results.data:
                return search_results.data[0]

            # If email provided, try to find by email
            if email:
                email_results = stripe.Customer.list(email=email, limit=1)
                if email_results.data:
                    # Update metadata with user_id
                    customer = email_results.data[0]
                    stripe.Customer.modify(customer.id, metadata={"user_id": user_id})
                    return customer

            # Create new customer (email is optional)
            create_params: dict[str, Any] = {
                "metadata": {"user_id": user_id, "environment": self.environment}
            }
            if email:
                create_params["email"] = email
            return stripe.Customer.create(**create_params)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting/creating customer: {e}")
            raise

    def create_subscription(self, user_id: str, email: str, price_id: str) -> dict[str, Any]:
        """Create a subscription for unlimited access."""
        try:
            # Create or retrieve customer
            customers = stripe.Customer.list(email=email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                customer = stripe.Customer.create(email=email, metadata={"user_id": user_id})

            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{"price": price_id}],
                metadata={"user_id": user_id, "environment": self.environment},
            )

            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "customer_id": customer.id,
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating subscription: {e}")
            raise

    def pause_subscription(self, subscription_id: str) -> dict[str, str]:
        """Pause a subscription."""
        try:
            stripe.Subscription.modify(
                subscription_id, pause_collection={"behavior": "mark_uncollectible"}
            )
            return {"message": "Subscription paused", "status": "paused"}
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error pausing subscription: {e}")
            raise

    def resume_subscription(self, subscription_id: str) -> dict[str, str]:
        """Resume a paused subscription."""
        try:
            stripe.Subscription.modify(
                subscription_id,
                pause_collection="",  # Remove pause
            )
            return {"message": "Subscription resumed", "status": "active"}
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error resuming subscription: {e}")
            raise

    def cancel_subscription(self, subscription_id: str) -> dict[str, str]:
        """Cancel a subscription."""
        try:
            stripe.Subscription.cancel(subscription_id)
            return {"message": "Subscription cancelled", "status": "cancelled"}
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error cancelling subscription: {e}")
            raise

    def _get_mock_plans(self) -> list[Plan]:
        """Return mock plans for development/testing."""
        return [
            Plan(
                plan_reference="price_standard_mock",
                plan_type="prepaid",
                plan_name="STANDARD",
                plan_subtitle="One-time purchase",
                plan_amount=10.0,
                plan_credits=5000,
                plan_credits_text="5,000 credits",
                percent_off="",
            ),
            Plan(
                plan_reference="price_power_mock",
                plan_type="prepaid",
                plan_name="POWER",
                plan_subtitle="Best value",
                plan_amount=50.0,
                plan_credits=28500,
                plan_credits_text="28,500 credits",
                percent_off="12.5% OFF",
            ),
            Plan(
                plan_reference="price_elite_mock",
                plan_type="prepaid",
                plan_name="ELITE",
                plan_subtitle="Maximum savings",
                plan_amount=100.0,
                plan_credits=66666,
                plan_credits_text="66,666 credits",
                percent_off="25% OFF",
            ),
            Plan(
                plan_reference="price_unlimited_mock",
                plan_type="postpaid",
                plan_name="UNLIMITED",
                plan_subtitle="Monthly subscription",
                plan_amount=299.0,
                plan_credits=None,
                plan_credits_text="Unlimited",
                percent_off="",
            ),
        ]
