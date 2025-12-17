from typing import Any, Dict, Optional

from .http import BaseHttpClient


class CimSubAPI:
    """
    所有领域子 API 的基类，内部持有一个 CIMClient / BaseHttpClient，
    提供 _request() 便于复用底层 HTTP 能力。
    """

    def __init__(self, client: BaseHttpClient):
        self.client = client

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        return self.client.request(method, path, params=params, json=json, headers=headers)
