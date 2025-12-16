"""
External API provider for production phone verification
"""

import os

import httpx
from aws_lambda_powertools import Logger

from ..core.models import LineType

logger = Logger()


class ExternalAPIProvider:
    """
    Production provider that calls external verification APIs.
    Uses landlineremover.com which returns both line type and DNC status in a single call.
    """

    def __init__(self, timeout: float = 10.0):
        """
        Initialize external API provider.

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.api_key = os.environ.get("LANDLINE_REMOVER_API_KEY", "")
        if not self.api_key:
            logger.warning("LANDLINE_REMOVER_API_KEY not set")

        self.api_url = "https://app.landlineremover.com/api/check-number"
        self.timeout = timeout
        self.http_client = httpx.Client(timeout=timeout)

    def verify_phone(self, phone: str) -> tuple[LineType, bool]:
        """
        Verify phone using landlineremover.com API.

        This API returns both line type and DNC status in a single call,
        which is more efficient than making two separate API calls.

        Args:
            phone: E.164 formatted phone number

        Returns:
            Tuple of (line_type, is_on_dnc_list)

        Raises:
            httpx.HTTPError: For API communication errors
            ValueError: For invalid responses
        """
        logger.debug(f"Verifying phone {phone[:6]}*** via external API")

        if not self.api_key:
            raise ValueError("API key not configured")

        try:
            # Make single API call that returns both line type and DNC status
            # The API may redirect, so we need to follow redirects
            response = self.http_client.get(
                self.api_url,
                params={"apikey": self.api_key, "number": phone},
                follow_redirects=True,
            )

            # Raise for HTTP errors
            response.raise_for_status()

            # Parse response
            json_response = response.json()

            # Extract data from response wrapper
            if "data" in json_response:
                data = json_response["data"]
            else:
                data = json_response

            # Map line type from API response
            line_type = self._map_line_type(data)

            # Map DNC status - API uses "DNCType" field
            # Values can be "dnc", "clean", etc.
            dnc_type = data.get("DNCType", data.get("dnc_type", "")).lower()
            is_dnc = dnc_type != "clean" and dnc_type != ""

            logger.debug(
                f"Verification complete for {phone[:6]}***",
                extra={"line_type": line_type.value, "is_dnc": is_dnc, "dnc_type": dnc_type},
            )

            return line_type, is_dnc

        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"API request failed with status {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error: {str(e)}")
            raise ValueError(f"Network error during API call: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during verification: {str(e)}")
            raise

    def _map_line_type(self, data: dict) -> LineType:
        """
        Map API response to LineType enum.

        Args:
            data: API response dictionary

        Returns:
            LineType enum value
        """
        # API uses "LineType" (capitalized) field
        line_type_str = data.get("LineType", data.get("line_type", "")).lower()

        # Map common line types
        line_type_map = {
            "mobile": LineType.MOBILE,
            "landline": LineType.LANDLINE,
            "voip": LineType.VOIP,
            "wireless": LineType.MOBILE,  # Some APIs return "wireless" for mobile
            "fixed": LineType.LANDLINE,  # Some APIs return "fixed" for landline
        }

        return line_type_map.get(line_type_str, LineType.UNKNOWN)

    def __del__(self) -> None:
        """Cleanup HTTP client"""
        if hasattr(self, "http_client"):
            self.http_client.close()
