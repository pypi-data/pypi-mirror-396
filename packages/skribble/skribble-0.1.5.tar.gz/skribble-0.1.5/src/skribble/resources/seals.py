from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional
from typing import TYPE_CHECKING

from skribble.exceptions import SkribbleError

if TYPE_CHECKING:
    from skribble.client import SkribbleClient


class SealsClient:
    """
    Client for /v2/seal endpoints.
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    def seal_document(
            self,
            *,
            content: Optional[str] = None,
            document_id: Optional[str] = None,
            account_name: Optional[str] = None,
            visual_signature: Optional[Dict[str, Any]] = None,
            **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Seal a document using Skribble seals.

        Unifies the variants:
        - Seal a document (with content)
        - Seal a document with a specific seal (account_name)
        - Seal an existing document via document_id

        Exactly one of `content` or `document_id` must be provided.
        """
        if (content is None) == (document_id is None):
            raise SkribbleError("Exactly one of `content` or `document_id` must be provided.")

        body: Dict[str, Any] = {}
        if content is not None:
            body["content"] = content
        if document_id is not None:
            body["document_id"] = document_id
        if account_name is not None:
            body["account_name"] = account_name
        if visual_signature is not None:
            body["visual_signature"] = visual_signature
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            "/seal",
            json=body,
        )
        return resp.json()
