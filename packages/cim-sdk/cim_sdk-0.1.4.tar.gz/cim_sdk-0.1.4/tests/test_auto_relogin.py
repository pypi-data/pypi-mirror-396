from __future__ import annotations

from typing import Any, Dict, List, Optional

from cim_sdk import CIMClient


class _FakeResponse:
    def __init__(self, payload: Dict[str, Any], *, ok: bool = True, status_code: int = 200):
        self._payload = payload
        self.ok = ok
        self.status_code = status_code

    def json(self) -> Dict[str, Any]:
        return self._payload


class _FakeSession:
    def __init__(self, responses: List[_FakeResponse]):
        self._responses = responses
        self.calls: List[Dict[str, Any]] = []

    def request(
        self,
        *,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> _FakeResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": params,
                "json": json,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return self._responses.pop(0)


def test_request_auto_relogin_on_code_401_payload():
    session = _FakeSession(
        [
            _FakeResponse({"code": 401, "data": None, "msg": "账号未登录"}),
            _FakeResponse({"code": 0, "data": {"ok": True}, "msg": "success"}),
        ]
    )

    client = CIMClient()
    client.session = session

    called = {"n": 0}

    def handler() -> None:
        called["n"] += 1
        client.set_token("new-token")

    client.set_auto_relogin_handler(handler)

    resp = client.request("GET", "/dropship/page", params={"pageNo": "1"})
    assert resp["code"] == 0
    assert called["n"] == 1
    assert len(session.calls) == 2

