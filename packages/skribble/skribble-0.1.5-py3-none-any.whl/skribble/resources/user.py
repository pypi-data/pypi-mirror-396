from __future__ import annotations

from typing import Any
from typing import Dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skribble.client import SkribbleClient


class UserClient:
    """
    Client for /v2/user endpoints.
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    def get_signature_qualities(self, username: str) -> Dict[str, Any]:
        """
        Get a user's signature qualities (simple).

        Mirrors GET /v2/user/signature-qualities?username=<email>
        """
        resp = self._client.request(
            "GET",
            "/user/signature-qualities",
            params={"username": username},
        )
        return resp.json()

    def get_signature_qualities_detail(self, username: str) -> Dict[str, Any]:
        """
        Get signature qualities details for a user.

        Mirrors GET /v2/user/signature-qualities-detail?username=<email>
        """
        resp = self._client.request(
            "GET",
            "/user/signature-qualities-detail",
            params={"username": username},
        )
        return resp.json()
