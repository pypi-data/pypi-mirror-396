from typing import Any, Dict, Optional

import requests

from .config import CIMConfig


class CIMApiError(Exception):
    """调用 CIM 接口失败时抛出的异常"""

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[requests.Response] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class BaseHttpClient:
    """
    负责：
    - 保存 config / session / token
    - 统一封装 HTTP 请求（带好 headers）
    """

    def __init__(self, config: Optional[CIMConfig] = None, session: Optional[requests.Session] = None):
        self.config = config or CIMConfig()
        self.session = session or requests.Session()
        self.token: Optional[str] = None

    # ========== token 相关 ==========

    def set_token(self, token: str) -> None:
        self.token = token

    # ========== headers & request ==========

    def _headers(self, extra_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "tenant-id": self.config.tenant_id,
            "user-agent": self.config.user_agent,
        }
        if self.token:
            headers["authorization"] = f"Bearer {self.token}"
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        统一的请求入口，返回 JSON dict，失败抛 CIMApiError
        """
        url = f"{self.config.base_url.rstrip('/')}/{path.lstrip('/')}"
        merged_headers = self._headers(headers)

        try:
            resp = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                headers=merged_headers,
                timeout=self.config.timeout,
            )
        except requests.RequestException as exc:
            raise CIMApiError(f"网络请求异常: {exc}") from exc

        if not resp.ok:
            try:
                err_json = resp.json()
            except Exception:
                err_json = None

            msg = f"CIM API 调用失败: HTTP {resp.status_code}"
            if isinstance(err_json, dict):
                msg_detail = err_json.get("msg") or err_json.get("message")
                if msg_detail:
                    msg += f" - {msg_detail}"
            raise CIMApiError(msg, status_code=resp.status_code, response=resp)

        try:
            return resp.json()
        except ValueError as exc:
            raise CIMApiError("响应不是合法 JSON", status_code=resp.status_code, response=resp) from exc
