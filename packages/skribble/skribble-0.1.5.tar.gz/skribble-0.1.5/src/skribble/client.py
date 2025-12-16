from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

import redis
import requests
from skribble.auth import TokenManager
from skribble.config import SkribbleConfig
from skribble.config import SkribbleEUConfig
from skribble.exceptions import SkribbleHTTPError
from skribble.resources.documents import DocumentsClient
from skribble.resources.monitoring import MonitoringClient
from skribble.resources.report import ReportClient
from skribble.resources.seals import SealsClient
from skribble.resources.sendto import SendToClient
from skribble.resources.signature_requests import SignatureRequestsClient
from skribble.resources.user import UserClient

JsonType = Union[Dict[str, Any], list, None]


class SkribbleClient:
    """
    High-level Skribble API v2 client.

    Usage (single-tenant):

        import redis
        from skribble import SkribbleClient

        r = redis.Redis(host="localhost", port=6379, db=0)
        client = SkribbleClient(
            username="api_demo_your_name",
            api_key="your_api_key",
            redis_client=r
        )

        docs = client.documents.list()

    For multi-tenant:
    - Create one SkribbleClient per tenant, with separate credentials and/or tenant_id.

    `region` should be DE_EU for Europe or CH_ROW for Switzerland and rest of world.
    """

    def __init__(
            self,
            *,
            username: str,
            api_key: str,
            redis_client: redis.Redis,
            region: str = "CH_ROW",
            tenant_id: Optional[str] = None,
            config: Optional[SkribbleConfig] = None,
            session: Optional[requests.Session] = None,
    ) -> None:
        self.session = session or requests.Session()
        self.config = config or (SkribbleEUConfig() if region == 'DE_EU' else SkribbleConfig())
        self.session.headers.update({"User-Agent": self.config.user_agent})

        self._token_manager = TokenManager(
            username=username,
            api_key=api_key,
            http_session=self.session,
            config=self.config,
            redis_client=redis_client,
            tenant_id=tenant_id,
        )

        # Resource clients
        self.signature_requests = SignatureRequestsClient(self)
        self.documents = DocumentsClient(self)
        self.seals = SealsClient(self)
        self.sendto = SendToClient(self)
        self.user = UserClient(self)
        self.report = ReportClient(self)
        self.monitoring = MonitoringClient(self)

    # ---------- Core HTTP helpers ----------

    def _get_access_token(self, *, force_refresh: bool = False) -> str:
        return self._token_manager.get_access_token(force_refresh=force_refresh)

    def _build_url(self, path: str, *, management: bool = False) -> str:
        # Allow passing full URLs to bypass base composition (needed for non-/v2 endpoints).
        if path.startswith("http://") or path.startswith("https://"):
            return path

        base = self.config.management_base_url if management else self.config.api_base_url
        return f"{base}{path}"

    def request(
            self,
            method: str,
            path: str,
            *,
            management: bool = False,
            auth: bool = True,
            params: Optional[Dict[str, Any]] = None,
            json: JsonType = None,
            headers: Optional[Dict[str, str]] = None,
            stream: bool = False,
            expected_status: Optional[int] = None,
    ) -> requests.Response:
        """
        Low-level request wrapper. Most users should use resource methods.
        """
        url = self._build_url(path, management=management)
        hdrs: Dict[str, str] = {}
        if headers:
            hdrs.update(headers)

        if auth:
            token = self._get_access_token()
            hdrs.setdefault("Authorization", f"Bearer {token}")

        try:
            resp = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                headers=hdrs,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
                stream=stream,
            )
        except requests.RequestException as exc:
            raise SkribbleHTTPError(-1, f"Request to Skribble failed: {exc}") from exc

        if expected_status is not None and resp.status_code != expected_status:
            self._raise_for_status(resp)
        elif expected_status is None and not (200 <= resp.status_code < 300):
            self._raise_for_status(resp)

        return resp

    def _raise_for_status(self, resp: requests.Response) -> None:
        text = resp.text
        try:
            data = resp.json()
            msg = data.get("message") or data.get("error") or text
        except Exception:
            data = None
            msg = text
        raise SkribbleHTTPError(
            resp.status_code,
            msg,
            response_json=data,
            response_text=text,
        )
