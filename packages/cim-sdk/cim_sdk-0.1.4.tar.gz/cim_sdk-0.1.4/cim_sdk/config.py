from dataclasses import dataclass


@dataclass
class CIMConfig:
    """
    CIM 客户端配置：
    - base_url: API 前缀
    - tenant_id: 现在你这边都是 1
    - timeout: 请求超时时间
    - user_agent: SDK 自定义 UA
    """

    base_url: str = "https://cim.cameronsino.com/admin-api/cim"
    tenant_id: str = "1"
    user_agent: str = "Mozilla/5.0 (CIM-SDK-Python)"
    timeout: int = 20
