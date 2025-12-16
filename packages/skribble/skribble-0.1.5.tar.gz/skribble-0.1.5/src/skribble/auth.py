from __future__ import annotations

import json
from typing import Optional

import redis
import requests
from skribble.config import SkribbleConfig
from skribble.exceptions import SkribbleAuthError
from skribble.exceptions import SkribbleHTTPError


class TokenManager:
    """
    Handles obtaining and caching Skribble access tokens (JWTs) in Redis.

    - Logs in via POST /access/login with username + api-key
    - Caches access token in Redis with TTL from config (default 20 minutes)
    """

    def __init__(
            self,
            *,
            username: str,
            api_key: str,
            http_session: requests.Session,
            config: SkribbleConfig,
            redis_client: redis.Redis,
            tenant_id: Optional[str] = None,
    ) -> None:
        self._username = username
        self._api_key = api_key
        self._session = http_session
        self._cfg = config
        self._redis = redis_client
        self._tenant_id = tenant_id

    @property
    def _redis_key(self) -> str:
        base = f"{self._cfg.redis_key_prefix}:token:{self._username}"
        if self._tenant_id:
            return f"{base}:{self._tenant_id}"
        return base

    def get_access_token(self, *, force_refresh: bool = False) -> str:
        """
        Returns a valid access token, refreshing it via /access/login if needed.
        """
        if not force_refresh:
            cached = self._redis.get(self._redis_key)
            if cached:
                return cached.decode("utf-8")

        token = self._login()
        # Store token with configured TTL (docs: ~20 minutes)
        self._redis.setex(
            self._redis_key,
            self._cfg.access_token_ttl_seconds,
            token,
        )
        return token

    def _login(self) -> str:
        """
        Performs POST /access/login and returns the JWT access token.
        """
        url = f"{self._cfg.api_base_url}/access/login"
        payload = {
            "username": self._username,
            "api-key": self._api_key,
        }

        try:
            resp = self._session.post(
                url,
                json=payload,
                timeout=self._cfg.timeout,
                verify=self._cfg.verify_ssl,
            )
        except requests.RequestException as exc:
            raise SkribbleAuthError(f"Failed to call Skribble login endpoint: {exc}") from exc

        if resp.status_code != 200:
            text = resp.text
            try:
                data = resp.json()
                msg = data.get("message") or data.get("error") or text
            except json.JSONDecodeError:
                data = None
                msg = text
            raise SkribbleHTTPError(
                resp.status_code,
                f"Login failed: {msg}",
                response_json=data,
                response_text=text,
            )

        # The Postman collection stores the JWT in AUTH_ACCESS_TOKEN environment var.
        # Here, we assume the API returns the JWT directly as a string or in a JSON field.
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" in content_type:
            data = resp.json()
            # Common patterns: {"token": "..."} or {"access_token": "..."} or string
            token = (
                    data.get("access_token")
                    or data.get("token")
                    or data.get("jwt")
                    or data.get("AUTH_ACCESS_TOKEN")
            )
            if not token:
                # Try plain JSON string
                if isinstance(data, str):
                    token = data
            if not token:
                raise SkribbleAuthError("Login succeeded but no access token found in response JSON.")
        else:
            # Some implementations may return raw token text
            token = resp.text.strip()

        if not token:
            raise SkribbleAuthError("Login succeeded but access token is empty.")

        return token
