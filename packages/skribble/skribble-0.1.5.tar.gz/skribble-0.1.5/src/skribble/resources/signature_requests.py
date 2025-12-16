from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from skribble.exceptions import SkribbleError

if TYPE_CHECKING:
    from skribble.client import SkribbleClient


class SignatureRequestsClient:
    """
    Client for /v2/signature-requests endpoints.
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    # ---------- Create ----------

    def create(
            self,
            *,
            title: str,
            signatures: Optional[List[Dict[str, Any]]] = None,
            content: Optional[str] = None,
            file_url: Optional[str] = None,
            document_id: Optional[str] = None,
            message: Optional[str] = None,
            content_type: Optional[str] = None,
            observers: Optional[List[str]] = None,
            cc_email_addresses: Optional[List[str]] = None,
            callbacks: Optional[List[Dict[str, Any]]] = None,
            callback_success_url: Optional[str] = None,
            callback_update_url: Optional[str] = None,
            callback_error_url: Optional[str] = None,
            attach_on_success: Optional[List[str]] = None,
            quality: Optional[str] = None,
            signature_level: Optional[str] = None,
            legislation: Optional[str] = None,
            creator: Optional[str] = None,
            owner_account_email: Optional[str] = None,
            write_access: Optional[List[str]] = None,
            read_access: Optional[List[str]] = None,
            disable_notifications: Optional[bool] = None,
            **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Create a SignatureRequest using any of the documented variants.

        Covers:
        - Uploading a PDF (`content`), using an existing URL (`file_url`), or reusing an uploaded
          document (`document_id`).
        - Visual signatures (provided inside each item of `signatures`), quality/legislation,
          observers, callbacks, auto-attachments, specific owner (`creator`), and no-account signers.

        Exactly one of `content`, `file_url` or `document_id` must be provided.
        """
        source_fields = [name for name, val in
                         [("content", content), ("file_url", file_url), ("document_id", document_id)]
                         if val is not None]
        if len(source_fields) != 1:
            raise SkribbleError(
                "Exactly one of `content`, `file_url` or `document_id` must be set"
            )

        body: Dict[str, Any] = {
            "title": title,
            "signatures": signatures or [],
        }
        if content is not None:
            body["content"] = content
        if file_url is not None:
            body["file_url"] = file_url
        if document_id is not None:
            body["document_id"] = document_id
        if message is not None:
            body["message"] = message
        if content_type is not None:
            body["content_type"] = content_type

        ccs = cc_email_addresses or observers
        if ccs is not None:
            body["cc_email_addresses"] = ccs
        if callbacks is not None:
            body["callbacks"] = callbacks
        if callback_success_url is not None:
            body["callback_success_url"] = callback_success_url
        if callback_update_url is not None:
            body["callback_update_url"] = callback_update_url
        if callback_error_url is not None:
            body["callback_error_url"] = callback_error_url
        if attach_on_success is not None:
            body["attach_on_success"] = attach_on_success

        quality_value = quality or signature_level
        if quality_value is not None:
            body["quality"] = quality_value
        if legislation is not None:
            body["legislation"] = legislation

        creator_value = creator or owner_account_email
        if creator_value is not None:
            body["creator"] = creator_value
        if write_access is not None:
            body["write_access"] = write_access
        if read_access is not None:
            body["read_access"] = read_access
        if disable_notifications is not None:
            body["disable_notifications"] = disable_notifications

        # Any additional fields introduced by the API can be passed via extra_fields
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            "/signature-requests",
            json=body,
        )
        return resp.json()

    # ---------- Find / list ----------

    def list(
            self,
            *,
            account_email: Optional[str] = None,
            search: Optional[str] = None,
            signature_status: Optional[str] = None,
            status_overall: Optional[str] = None,
            page_number: Optional[int] = None,
            page_size: Optional[int] = None,
            **extra_params: Any,
    ) -> Dict[str, Any]:
        """
        List and filter SignatureRequests.

        Mirrors "List and find SignatureRequests" in the Postman collection.
        """
        params: Dict[str, Any] = {}
        if account_email is not None:
            params["account_email"] = account_email
        if search is not None:
            params["search"] = search
        if signature_status is not None:
            params["signature_status"] = signature_status
        if status_overall is not None:
            params["status_overall"] = status_overall
        if page_number is not None:
            params["page_number"] = page_number
        if page_size is not None:
            params["page_size"] = page_size
        params.update(extra_params)

        resp = self._client.request(
            "GET",
            "/signature-requests",
            params=params,
        )
        return resp.json()

    def get(self, signature_request_id: str) -> Dict[str, Any]:
        """
        Get a single SignatureRequest by ID.
        """
        resp = self._client.request(
            "GET",
            f"/signature-requests/{signature_request_id}",
        )
        return resp.json()

    def get_bulk(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        List SignatureRequests by bulk.

        Mirrors POST /v2/signature-requests/bulk which accepts an array of IDs.
        """
        resp = self._client.request(
            "POST",
            "/signature-requests/bulk",
            json=ids,
        )
        return resp.json()

    # ---------- Update (multiple signers or meta) ----------

    def update(
            self,
            signature_request_id: str,
            *,
            title: Optional[str] = None,
            message: Optional[str] = None,
            signatures: Optional[List[Dict[str, Any]]] = None,
            attach_on_success: Optional[List[str]] = None,
            callbacks: Optional[List[Dict[str, Any]]] = None,
            callback_success_url: Optional[str] = None,
            callback_update_url: Optional[str] = None,
            callback_error_url: Optional[str] = None,
            quality: Optional[str] = None,
            legislation: Optional[str] = None,
            creator: Optional[str] = None,
            read_access: Optional[List[str]] = None,
            write_access: Optional[List[str]] = None,
            **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Update a SignatureRequest, including adding/removing signers in bulk.

        Mirrors PUT /v2/signature-requests which expects the SignatureRequest payload (including id)
        and is used in the Postman collection as "Add or remove multiple signers simultaneously".
        """
        body: Dict[str, Any] = {
            "id": signature_request_id,
        }
        if title is not None:
            body["title"] = title
        if message is not None:
            body["message"] = message
        if signatures is not None:
            body["signatures"] = signatures
        if attach_on_success is not None:
            body["attach_on_success"] = attach_on_success
        if callbacks is not None:
            body["callbacks"] = callbacks
        if callback_success_url is not None:
            body["callback_success_url"] = callback_success_url
        if callback_update_url is not None:
            body["callback_update_url"] = callback_update_url
        if callback_error_url is not None:
            body["callback_error_url"] = callback_error_url
        if quality is not None:
            body["quality"] = quality
        if legislation is not None:
            body["legislation"] = legislation
        if creator is not None:
            body["creator"] = creator
        if read_access is not None:
            body["read_access"] = read_access
        if write_access is not None:
            body["write_access"] = write_access

        body.update(extra_fields)

        resp = self._client.request(
            "PUT",
            "/signature-requests",
            json=body,
        )
        return resp.json()

    # ---------- Signers ----------

    def add_signer(
            self,
            signature_request_id: str,
            *,
            account_email: Optional[str] = None,
            signer_identity_data: Optional[Dict[str, Any]] = None,
            **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Add an individual signer to an existing SignatureRequest.

        Mirrors POST /v2/signature-requests/{SR_ID}/signatures
        using the same parameters as when creating a SignatureRequest.
        """
        if not account_email and not signer_identity_data:
            raise SkribbleError("At least one of account_email or signer_identity_data must be provided.")

        body: Dict[str, Any] = {}
        if account_email is not None:
            body["account_email"] = account_email
        if signer_identity_data is not None:
            body["signer_identity_data"] = signer_identity_data
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/signatures",
            json=body,
        )
        return resp.json()

    def remove_signer(self, signature_request_id: str, signer_id: str) -> None:
        """
        Remove an individual signer by signature ID from a SignatureRequest.

        Mirrors DELETE /v2/signature-requests/{SR_ID}/signatures/{SID}
        """
        self._client.request(
            "DELETE",
            f"/signature-requests/{signature_request_id}/signatures/{signer_id}",
            expected_status=204,
        )

    # ---------- Attachments ----------

    def add_attachment(
            self,
            signature_request_id: str,
            *,
            filename: str,
            content_type: str,
            content: str,
            **extra_fields: Any,
    ) -> Dict[str, Any]:
        """
        Add an attachment to a SignatureRequest.

        Mirrors POST /v2/signature-requests/{SR_ID}/attachments with body containing
        filename, content_type, content (Base64).
        """
        body: Dict[str, Any] = {
            "filename": filename,
            "content_type": content_type,
            "content": content,
        }
        body.update(extra_fields)

        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/attachments",
            json=body,
        )
        return resp.json()

    def remove_attachment(self, signature_request_id: str, attachment_id: str) -> None:
        """
        Remove an attachment from a SignatureRequest.

        Mirrors DELETE /v2/signature-requests/{SR_ID}/attachments/{ATTACHMENT_ID}
        """
        self._client.request(
            "DELETE",
            f"/signature-requests/{signature_request_id}/attachments/{attachment_id}",
            expected_status=204,
        )

    def download_attachment(self, signature_request_id: str, attachment_id: str) -> bytes:
        """
        Download a specific attachment from a SignatureRequest.

        Mirrors GET /v2/signature-requests/{SR_ID}/attachments/{ATTACHMENT_ID}/content
        """
        resp = self._client.request(
            "GET",
            f"/signature-requests/{signature_request_id}/attachments/{attachment_id}/content",
            stream=True,
        )
        return resp.content

    # ---------- Delete / withdraw / remind ----------

    def delete(self, signature_request_id: str) -> None:
        """
        Delete a SignatureRequest and its associated document.

        Mirrors DELETE /v2/signature-requests/{SR_ID}
        """
        self._client.request(
            "DELETE",
            f"/signature-requests/{signature_request_id}",
            expected_status=204,
        )

    def withdraw(self, signature_request_id: str, message: Optional[str] = None) -> Dict[str, Any]:
        """
        Withdraw a SignatureRequest, optionally providing a message.

        Mirrors POST /v2/signature-requests/{SR_ID}/withdraw
        """
        body = {"message": message} if message is not None else {}
        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/withdraw",
            json=body if body else None,
        )
        return resp.json()

    def remind(self, signature_request_id: str) -> Dict[str, Any]:
        """
        Send reminder notifications to open signers.

        Mirrors POST /v2/signature-requests/{SR_ID}/remind
        """
        resp = self._client.request(
            "POST",
            f"/signature-requests/{signature_request_id}/remind",
        )
        return resp.json()

    # ---------- Callbacks (Monitoring/Callbacks) ----------

    def list_callbacks(self, signature_request_id: str) -> Dict[str, Any]:
        """
        Get the list of callbacks configured for a SignatureRequest.

        Mirrors GET /v2/signature-requests/{SR_ID}/callbacks
        """
        resp = self._client.request(
            "GET",
            f"/signature-requests/{signature_request_id}/callbacks",
        )
        return resp.json()

    # ---------- Signing view (web app) ----------

    def view(
            self,
            signature_request_id: str,
            *,
            exit_url: Optional[str] = None,
            redirect_timeout: Optional[int] = None,
            hide_download: Optional[bool] = None,
    ) -> str:
        """
        Build and call the signing view endpoint (used to redirect a user to sign).

        Mirrors GET /view/{SR_ID} from the Postman quickstart. Returns the resolved URL
        (after applying query params). Uses app_base_url from config if provided, otherwise
        falls back to the API host without /v2.
        """
        base_app = getattr(self._client.config, "app_base_url", None) or self._client.config.api_base_url.rstrip("/")
        if base_app.endswith("/v2"):
            base_app = base_app[:-3]

        url = f"{base_app}/view/{signature_request_id}"
        params: Dict[str, Any] = {}
        if exit_url is not None:
            params["exitURL"] = exit_url
        if redirect_timeout is not None:
            params["redirectTimeout"] = redirect_timeout
        if hide_download is not None:
            params["hidedownload"] = str(hide_download).lower()

        # Do not force auth; view endpoint is meant for end-user redirect context.
        resp = self._client.request(
            "GET",
            url,
            auth=False,
            params=params or None,
        )
        return resp.url
