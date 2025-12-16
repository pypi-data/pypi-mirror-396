"""Payment data models with legacy shape compatibility."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PlanType(Enum):
    """Plan types matching legacy frontend expectations."""

    PREPAID = "prepaid"
    POSTPAID = "postpaid"
    INTRO = "intro"


class SubscriptionStatus(Enum):
    """Subscription statuses."""

    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"


@dataclass
class Plan:
    """
    Plan model matching legacy frontend data structure.
    Maps from Stripe Price/Product to legacy fields.
    """

    plan_reference: str  # Stripe price ID or legacy reference
    plan_type: str  # prepaid, postpaid, intro
    plan_name: str  # STANDARD, POWER, ELITE, UNLIMITED
    plan_subtitle: str
    plan_amount: float  # Price in USD
    plan_credits: int | None  # Number of credits or None for unlimited
    plan_credits_text: str  # Display text like "5,000 credits"
    percent_off: str  # Discount percentage display text

    # Additional fields for internal use
    stripe_price_id: str | None = None
    stripe_product_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "plan_reference": self.plan_reference,
            "plan_type": self.plan_type,
            "plan_name": self.plan_name,
            "plan_subtitle": self.plan_subtitle,
            "plan_amount": self.plan_amount,
            "plan_credits": self.plan_credits,
            "plan_credits_text": self.plan_credits_text,
            "percent_off": self.percent_off,
        }

        # Add variable_amount flag for VARIABLE product
        if self.plan_name == "VARIABLE":
            result["variable_amount"] = True

        return result

    @classmethod
    def from_stripe_price(cls, price: dict[str, Any], product: dict[str, Any]) -> "Plan":
        """
        Create Plan from Stripe Price and Product objects.
        Maps Stripe metadata to legacy fields.
        """
        metadata = price.get("metadata", {})

        # Determine plan type
        if price.get("recurring"):
            plan_type = "postpaid"
        else:
            plan_type = metadata.get("plan_type", "prepaid")

        # Extract credits
        credits_str = metadata.get("credits", "")
        if credits_str.lower() == "unlimited":
            plan_credits = None
            plan_credits_text = "Unlimited"
        elif credits_str:
            try:
                plan_credits = int(credits_str)
                plan_credits_text = f"{plan_credits:,} credits"
            except ValueError:
                plan_credits = None
                plan_credits_text = credits_str
        else:
            plan_credits = None
            plan_credits_text = ""

        return cls(
            plan_reference=metadata.get("plan_reference", price["id"]),
            plan_type=plan_type,
            plan_name=metadata.get("tier", product.get("name", "")).upper(),
            plan_subtitle=metadata.get("plan_subtitle", product.get("description", "")),
            plan_amount=price["unit_amount"] / 100.0,  # Convert cents to dollars
            plan_credits=plan_credits,
            plan_credits_text=metadata.get("plan_credits_text", plan_credits_text),
            percent_off=metadata.get("percent_off", ""),
            stripe_price_id=price["id"],
            stripe_product_id=product["id"],
        )
