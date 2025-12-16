"""
Base protocol for verification providers
"""

from typing import Protocol

from ..core.models import LineType


class VerificationProvider(Protocol):
    """
    Protocol for phone verification providers.
    All providers must implement this interface.
    """

    def verify_phone(self, phone: str) -> tuple[LineType, bool]:
        """
        Verify a phone number's line type and DNC status.

        Args:
            phone: E.164 formatted phone number

        Returns:
            Tuple of (line_type, is_on_dnc_list)

        Raises:
            ValueError: If phone format is invalid
            Exception: For provider-specific errors
        """
        ...
