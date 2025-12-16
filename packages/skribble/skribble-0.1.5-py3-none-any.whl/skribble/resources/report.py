from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skribble.client import SkribbleClient


class ReportClient:
    """
    Client for reporting endpoints such as /v2/activities/signatures.
    """

    def __init__(self, client: SkribbleClient) -> None:
        self._client = client

    def get_signature_activities(
            self,
            *,
            start_date: str,
            end_date: str,
            page: Optional[int] = None,
            size: Optional[int] = None,
            **extra_params: Any,
    ) -> Dict[str, Any]:
        """
        Get signature activities by business.

        Mirrors:
        GET /v2/activities/signatures?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&page=&size=

        Dates must be in `yyyy-MM-dd` format.
        """
        params: Dict[str, Any] = {
            "start_date": start_date,
            "end_date": end_date,
        }
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        params.update(extra_params)

        resp = self._client.request(
            "GET",
            "/activities/signatures",
            params=params,
        )
        return resp.json()
