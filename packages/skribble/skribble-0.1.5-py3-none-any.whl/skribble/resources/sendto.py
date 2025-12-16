from __future__ import annotations

from typing import Any
from typing import Dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skribble.client import SkribbleClient


class SendToClient:
    """
    Client for /v2/sendto and /sendto endpoints.
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    def create(self, *, title: str, content: str) -> Dict[str, Any]:
        """
        Create a Send-To object.

        Mirrors POST /v2/sendto with body:
        {
            "title": "...",
            "content": "<BASE64_PDF>"
        }

        Response contains `id`, `url`, `access_code`, etc.
        """
        body = {
            "title": title,
            "content": content,
        }
        resp = self._client.request(
            "POST",
            "/sendto",
            auth=False,  # Send-To is authenticated via access code only
            json=body,
        )
        return resp.json()

    def track(self, send_to_id: str, access_code: str) -> Dict[str, Any]:
        """
        Track the status of a Send-To object.

        Mirrors GET /v2/sendto/{SEND_TO_ID}/track with header X-Accesscode.
        """
        resp = self._client.request(
            "GET",
            f"/sendto/{send_to_id}/track",
            auth=False,
            headers={"X-Accesscode": access_code},
        )
        return resp.json()

    def download(self, send_to_id: str, access_code: str) -> bytes:
        """
        Download the Send-To based document (PDF).

        Mirrors GET /sendto/{SEND_TO_ID}/download with header X-Accesscode.
        """
        api_root = self._client.config.api_base_url.rstrip("/")
        if api_root.endswith("/v2"):
            api_root = api_root[:-3]
        url_path = f"{api_root}/sendto/{send_to_id}/download"
        resp = self._client.request(
            "GET",
            url_path,
            auth=False,
            headers={"X-Accesscode": access_code},
            stream=True,
        )
        return resp.content

    def delete(self, send_to_id: str, access_code: str) -> None:
        """
        Delete a Send-To object and its associated Document and SignatureRequest.

        Mirrors DELETE /v2/sendto/{SEND_TO_ID} with header X-Accesscode.
        """
        self._client.request(
            "DELETE",
            f"/sendto/{send_to_id}",
            auth=False,
            headers={"X-Accesscode": access_code},
        )
