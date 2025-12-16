from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from .config import CIMConfig
from .http import BaseHttpClient, CIMApiError

if TYPE_CHECKING:  # 避免循环导入
    from .orders import OrdersAPI
    from .products import ProductsAPI
    from .transactions import TransactionsAPI


class CIMClient(BaseHttpClient):
    """
    根客户端：
    - 负责 token / config / session / 基础 request
    - 暴露领域子 API：orders / transactions / products（懒加载）
    """

    def __init__(self, *, token: Optional[str] = None, config: Optional[CIMConfig] = None):
        super().__init__(config=config)
        if token:
            self.set_token(token)

        self.expires_time: Optional[datetime] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.has_order: Optional[bool] = None

        # 子模块懒加载占位
        self._orders: Optional["OrdersAPI"] = None
        self._transactions: Optional["TransactionsAPI"] = None
        self._products: Optional["ProductsAPI"] = None

    def login(self, username: str, password: str, uuid: str = "") -> Dict[str, Any]:
        """
        调用 /auth/login 接口，并把 accessToken 写入 client.token。

        返回 data 字段的内容，形如：
        {
            "userId": "...",
            "accessToken": "...",
            "refreshToken": "...",
            "expiresTime": "2025-12-04 08:34:41",
            "hasOrder": true
        }
        """
        payload = {
            "username": username,
            "password": password,
            "uuid": uuid,
        }

        resp = self.request(
            "POST",
            "/auth/login",
            json=payload,
            headers={
                "content-type": "application/json",
                "origin": "https://cim.cameronsino.com",
            },
        )

        code = resp.get("code")
        if code != 0:
            msg = resp.get("msg") or "登录失败（未知错误）"
            raise CIMApiError(f"登录失败: code={code}, msg={msg}")

        data = resp.get("data") or {}
        access_token = data.get("accessToken")
        if not access_token:
            raise CIMApiError("登录响应中缺少 accessToken")

        self.set_token(access_token)

        self.user_id = data.get("userId")
        self.refresh_token = data.get("refreshToken")
        self.has_order = data.get("hasOrder")

        expires_str = data.get("expiresTime")
        if expires_str:
            try:
                self.expires_time = datetime.strptime(expires_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                self.expires_time = None

        return data

    @classmethod
    def from_credentials(
        cls,
        username: str,
        password: str,
        uuid: str = "",
        *,
        config: Optional[CIMConfig] = None,
    ) -> "CIMClient":
        """
        简化构造：提供账号信息直接完成登录。
        """
        client = cls(config=config)
        client.login(username, password, uuid=uuid)
        return client

    # ===== 懒加载子 API =====

    @property
    def orders(self) -> "OrdersAPI":
        if self._orders is None:
            from .orders import OrdersAPI

            self._orders = OrdersAPI(self)
        return self._orders

    @property
    def transactions(self) -> "TransactionsAPI":
        if self._transactions is None:
            from .transactions import TransactionsAPI

            self._transactions = TransactionsAPI(self)
        return self._transactions

    @property
    def products(self) -> "ProductsAPI":
        if self._products is None:
            from .products import ProductsAPI

            self._products = ProductsAPI(self)
        return self._products
