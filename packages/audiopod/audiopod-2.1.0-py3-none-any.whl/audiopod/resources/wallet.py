"""
Wallet Service - API Wallet & Billing
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import AudioPod


class Wallet:
    """API wallet and billing service."""

    def __init__(self, client: "AudioPod"):
        self._client = client

    def get_balance(self) -> Dict[str, Any]:
        """
        Get current wallet balance.

        Returns:
            Balance information including balance_cents, balance_usd, etc.

        Example:
            >>> balance = client.wallet.get_balance()
            >>> print(f"Balance: {balance['balance_usd']}")
        """
        return self._client.get("/api/v1/api-wallet/balance")

    def get_usage(
        self,
        *,
        page: int = 1,
        limit: int = 50,
        api_key_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get usage history.

        Args:
            page: Page number
            limit: Items per page
            api_key_id: Filter by specific API key
        """
        return self._client.get(
            "/api/v1/api-wallet/usage",
            params={"page": page, "limit": limit, "api_key_id": api_key_id},
        )

    def get_pricing(self) -> Dict[str, Any]:
        """
        Get pricing information for all services.

        Returns:
            Pricing table with rates per service
        """
        return self._client.get("/api/v1/api-wallet/pricing")

    def estimate_cost(
        self, service_type: str, duration_seconds: int
    ) -> Dict[str, Any]:
        """
        Estimate cost for an operation.

        Args:
            service_type: Service type (e.g., 'transcription', 'stem_extraction')
            duration_seconds: Duration in seconds

        Returns:
            Cost estimate with cost_cents and cost_usd

        Example:
            >>> estimate = client.wallet.estimate_cost(
            ...     service_type="transcription",
            ...     duration_seconds=3600,
            ... )
            >>> print(f"Estimated cost: {estimate['cost_usd']}")
        """
        return self._client.post(
            "/api/v1/api-wallet/estimate",
            json_data={
                "service_type": service_type,
                "duration_seconds": duration_seconds,
            },
        )

    def check_balance(
        self, service_type: str, duration_seconds: int
    ) -> Dict[str, Any]:
        """
        Check if balance is sufficient for an operation.

        Args:
            service_type: Service type
            duration_seconds: Duration in seconds

        Returns:
            Object with 'sufficient' boolean and cost details
        """
        return self._client.post(
            "/api/v1/api-wallet/check-balance",
            json_data={
                "service_type": service_type,
                "duration_seconds": duration_seconds,
            },
        )




