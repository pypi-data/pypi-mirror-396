"""Stripe webhook event processing."""

import logging
from typing import Any

try:
    import stripe

    HAS_STRIPE = True
except ImportError:
    stripe = None  # type: ignore[assignment]
    HAS_STRIPE = False

from .credit_manager import CreditManager

logger = logging.getLogger(__name__)


class WebhookProcessor:
    """Process Stripe webhook events."""

    def __init__(self, webhook_secret: str, credit_manager: CreditManager):
        """Initialize with webhook secret and credit manager."""
        self.webhook_secret = webhook_secret
        self.credit_manager = credit_manager

    def verify_and_parse(self, payload: str, signature: str) -> dict[str, Any]:
        """Verify webhook signature and parse event."""
        if not HAS_STRIPE or not stripe:
            raise ImportError("stripe package not installed")

        try:
            event = stripe.Webhook.construct_event(payload, signature, self.webhook_secret)
            return dict(event)
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {e}")
            raise

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Process a verified webhook event.
        Returns response data.
        """
        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})

        logger.info(f"Processing webhook event: {event_type}")

        if event_type == "payment_intent.succeeded":
            return self._handle_payment_intent_succeeded(event_data)

        elif event_type == "checkout.session.completed":
            return self._handle_checkout_completed(event_data)

        elif event_type == "customer.subscription.created":
            return self._handle_subscription_created(event_data)

        elif event_type == "customer.subscription.updated":
            return self._handle_subscription_updated(event_data)

        elif event_type == "customer.subscription.deleted":
            return self._handle_subscription_deleted(event_data)

        elif event_type == "invoice.payment_succeeded":
            return self._handle_invoice_paid(event_data)

        elif event_type == "invoice.payment_failed":
            return self._handle_invoice_failed(event_data)

        elif event_type == "charge.dispute.created":
            return self._handle_dispute_created(event_data)

        else:
            logger.info(f"Unhandled event type: {event_type}")
            return {"message": f"Event {event_type} received but not processed"}

    def _handle_checkout_completed(self, session: dict[str, Any]) -> dict[str, Any]:
        """Handle successful checkout session for credit purchase."""
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")

        if not user_id:
            logger.error("No user_id in checkout session metadata")
            return {"error": "Missing user_id"}

        # Get line items to determine credits purchased
        if session.get("mode") == "payment":
            # One-time payment for credits
            # In production, fetch line items from Stripe to get price metadata
            # For now, extract from session metadata if available
            credits = int(metadata.get("credits", 0))

            if credits > 0:
                new_balance = self.credit_manager.add_credits(user_id, credits)
                logger.info(
                    f"Added {credits} credits to user {user_id}, new balance: {new_balance}"
                )
                return {"credits_added": credits, "new_balance": new_balance}

        return {"message": "Checkout processed"}

    def _handle_subscription_created(self, subscription: dict[str, Any]) -> dict[str, Any]:
        """Handle new subscription creation."""
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        status = str(subscription.get("status", "unknown"))

        if user_id:
            self.credit_manager.set_subscription_state(
                user_id=user_id,
                status=status,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
            )
            logger.info(f"Created subscription {subscription_id} for user {user_id}")

        return {"subscription_id": subscription_id, "status": status}

    def _handle_subscription_updated(self, subscription: dict[str, Any]) -> dict[str, Any]:
        """Handle subscription updates (pause/resume/etc)."""
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        subscription_id = subscription.get("id")
        status = str(subscription.get("status", "unknown"))

        if user_id:
            self.credit_manager.set_subscription_state(
                user_id=user_id, status=status, stripe_subscription_id=subscription_id
            )
            logger.info(f"Updated subscription {subscription_id} status to {status}")

        return {"subscription_id": subscription_id, "status": status}

    def _handle_subscription_deleted(self, subscription: dict[str, Any]) -> dict[str, Any]:
        """Handle subscription cancellation."""
        metadata = subscription.get("metadata", {})
        user_id = metadata.get("user_id")
        subscription_id = subscription.get("id")

        if user_id:
            self.credit_manager.set_subscription_state(
                user_id=user_id, status="cancelled", stripe_subscription_id=subscription_id
            )
            logger.info(f"Cancelled subscription {subscription_id} for user {user_id}")

        return {"subscription_id": subscription_id, "status": "cancelled"}

    def _handle_invoice_paid(self, invoice: dict[str, Any]) -> dict[str, Any]:
        """Handle successful subscription payment."""
        # For monthly subscriptions, could grant monthly credit allotment here
        # For now, just log the payment
        customer_id = invoice.get("customer")
        amount = invoice.get("amount_paid", 0) / 100.0
        logger.info(f"Invoice paid: ${amount} from customer {customer_id}")
        return {"amount_paid": amount}

    def _handle_invoice_failed(self, invoice: dict[str, Any]) -> dict[str, Any]:
        """Handle failed subscription payment."""
        customer_id = invoice.get("customer")
        logger.warning(f"Invoice payment failed for customer {customer_id}")
        # Could pause subscription or send notification here
        return {"status": "payment_failed"}

    def _handle_payment_intent_succeeded(self, payment_intent: dict[str, Any]) -> dict[str, Any]:
        """Handle successful payment intent (credit purchase)."""
        metadata = payment_intent.get("metadata", {})
        user_id = metadata.get("user_id")

        if not user_id:
            logger.error("No user_id in payment_intent metadata")
            return {"error": "Missing user_id"}

        # Check if this is a verification charge ($1)
        if metadata.get("type") == "verification":
            # This was the $1 verification, credits already added in payment_setup handler
            logger.info(f"Verification charge completed for user {user_id}")
            return {"type": "verification", "status": "completed"}

        # Get credits from metadata (set during payment creation)
        credits = int(metadata.get("credits", 0))

        if credits > 0:
            new_balance = self.credit_manager.add_credits(user_id, credits)
            logger.info(f"Added {credits} credits to user {user_id}, new balance: {new_balance}")
            return {"credits_added": credits, "new_balance": new_balance}

        return {"message": "Payment processed"}

    def _handle_dispute_created(self, dispute: dict[str, Any]) -> dict[str, Any]:
        """Handle charge dispute (mark account as disputed)."""
        # Get the charge and its metadata
        charge_id = dispute.get("charge")

        if not charge_id:
            logger.error("No charge_id in dispute")
            return {"error": "Missing charge_id"}

        # In production, would fetch the charge from Stripe to get metadata
        # For now, log the dispute for manual handling
        amount = dispute.get("amount", 0) / 100.0
        reason = dispute.get("reason", "unknown")

        logger.warning(f"Dispute created for charge {charge_id}: ${amount}, reason: {reason}")

        # TODO: Mark user account as disputed in CreditsTable
        # This would prevent new purchases until resolved

        return {"dispute_id": dispute.get("id"), "status": "created", "amount": amount}
