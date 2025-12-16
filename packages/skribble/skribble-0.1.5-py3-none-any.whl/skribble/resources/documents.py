from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skribble.client import SkribbleClient


class DocumentsClient:
    """
    Client for /v2/documents endpoints.
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    def upload(
            self,
            *,
            title: str,
            content: str,
            content_type: str = "application/pdf",
            **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Simple PDF document upload.

        Mirrors POST /v2/documents with body:
        {
            "title": "Example contract PDF",
            "content": "<BASE64_PDF>"
        }
        """
        body: Dict[str, Any] = {
            "title": title,
            "content": content,
            "content_type": content_type,
        }
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            "/documents",
            json=body,
        )
        return resp.json()

    def list(self) -> List[Dict[str, Any]]:
        """
        List all accessible documents.

        Mirrors GET /v2/documents
        """
        resp = self._client.request(
            "GET",
            "/documents",
        )
        return resp.json()

    def get_metadata(self, document_id: str) -> Dict[str, Any]:
        """
        Get the document metadata.

        Mirrors GET /v2/documents/{DOC_ID}
        """
        resp = self._client.request(
            "GET",
            f"/documents/{document_id}",
        )
        return resp.json()

    def download_content(self, document_id: str) -> bytes:
        """
        Download the full document content (PDF bytes).

        Mirrors GET /v2/documents/{DOC_ID}/content
        """
        resp = self._client.request(
            "GET",
            f"/documents/{document_id}/content",
            headers={"Accept": "application/pdf"},
            stream=True,
        )
        return resp.content

    def get_page_preview(self, document_id: str, page_id: int) -> bytes:
        """
        Download a page preview image for a document.

        Mirrors GET /v2/documents/{DOC_ID}/pages/{PAGE_ID}
        """
        resp = self._client.request(
            "GET",
            f"/documents/{document_id}/pages/{page_id}",
            stream=True,
        )
        return resp.content

    def delete(self, document_id: str) -> None:
        """
        Delete a document.

        Mirrors DELETE /v2/documents/{DOC_ID}
        """
        self._client.request(
            "DELETE",
            f"/documents/{document_id}",
            expected_status=204,
        )
