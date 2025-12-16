from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skribble.client import SkribbleClient


class MonitoringClient:
    """
    Client for monitoring-related endpoints:
    - Callbacks for SignatureRequests
    - System health
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    def create_signature_request_with_callbacks(
            self,
            *,
            title: str,
            content: str,
            signatures: List[Dict[str, Any]],
            callback_success_url: str,
            callback_update_url: str,
            callback_error_url: str,
            **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Convenience wrapper for creating a SignatureRequest with all possible callbacks,
        similar to the "Create a signature request with all possible callbacks" example.

        This simply calls SignatureRequestsClient.create(...) under the hood.
        """
        return self._client.signature_requests.create(
            title=title,
            content=content,
            signatures=signatures,
            callback_success_url=callback_success_url,
            callback_update_url=callback_update_url,
            callback_error_url=callback_error_url,
            **extra_fields,
        )

    def system_health(self) -> Dict[str, Any]:
        """
        Check Skribble system health.

        Mirrors GET /management/health which returns e.g. {"status": "UP"}.
        """
        resp = self._client.request(
            "GET",
            "/health",
            management=True,
            auth=False,  # health endpoint typically doesn't require auth
        )
        return resp.json()
