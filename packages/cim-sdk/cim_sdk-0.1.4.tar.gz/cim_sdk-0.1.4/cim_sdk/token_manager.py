"""
基于业务表 `cs_user_info` 的 Token 复用工厂，随 SDK 一起分发（pip 安装可直接导入）。

表结构（核心字段）：
    username (PK), cs_password, Rcustomerno, token, exp_time, exp_times_tamp,
    refreshToken, userId, hasOrder
"""

from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Any, Dict, Optional

from cim_sdk import CIMClient

if TYPE_CHECKING:
    from cim_sdk import CIMConfig

TABLE_NAME = "cs_user_info"
DEFAULT_SAFETY_MARGIN_SECONDS = 60


def _parse_exp_time(raw: Any) -> Optional[_dt.datetime]:
    """将 exp_time / expiresTime 字段解析为 datetime。"""
    if raw is None:
        return None
    if isinstance(raw, _dt.datetime):
        return raw
    if isinstance(raw, _dt.date):
        return _dt.datetime.combine(raw, _dt.time())
    if isinstance(raw, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return _dt.datetime.strptime(raw, fmt)
            except ValueError:
                continue
        try:
            return _dt.datetime.fromisoformat(raw)
        except ValueError:
            return None
    return None


def _fetch_user_record(db_conn: Any, value: str, *, column: str = "username") -> Optional[Dict[str, Any]]:
    """
    从 cs_user_info 查询用户记录，column 支持 username / Rcustomerno / userId。
    期望 db_conn 遵循 DB-API：支持 cursor() / execute() / fetchone()。
    """
    sql = f"SELECT * FROM {TABLE_NAME} WHERE {column}=%s"
    cursor = db_conn.cursor()
    try:
        cursor.execute(sql, (value,))
        row = cursor.fetchone()
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))
    finally:
        cursor.close()


def _is_token_valid(record: Dict[str, Any], safety_margin_seconds: int) -> bool:
    """检查记录中的 token 是否仍然有效。"""
    token = record.get("token")
    exp_time = _parse_exp_time(record.get("exp_time"))
    if not token or not exp_time:
        return False
    now = _dt.datetime.now()
    return exp_time - _dt.timedelta(seconds=safety_margin_seconds) > now


def _update_tokens(
    db_conn: Any,
    username: str,
    *,
    access_token: str,
    refresh_token: Optional[str],
    expires_at: Optional[_dt.datetime],
    user_id: Optional[str],
    has_order: Optional[bool],
) -> None:
    """将登录结果写回 cs_user_info。"""
    exp_time_str = expires_at.strftime("%Y-%m-%d %H:%M:%S") if expires_at else None
    exp_timestamp = str(int(expires_at.timestamp())) if expires_at else None
    sql = f"""
        UPDATE {TABLE_NAME}
        SET token=%s,
            exp_time=%s,
            exp_times_tamp=%s,
            refreshToken=%s,
            userId=%s,
            hasOrder=%s
        WHERE cs_name=%s
    """
    params = (
        access_token,
        exp_time_str,
        exp_timestamp,
        refresh_token,
        user_id,
        int(has_order) if has_order is not None else None,
        username,
    )
    cursor = db_conn.cursor()
    try:
        cursor.execute(sql, params)
        db_conn.commit()
    finally:
        cursor.close()


def _relogin_and_persist(
    client: CIMClient,
    db_conn: Any,
    *,
    username: str,
    password: str,
    uuid: str,
) -> None:
    """
    执行重新登录，并把 token/过期时间等信息写回 cs_user_info。
    用于：
    - 初始化时 token 缺失/过期
    - 调用接口过程中返回 {"code":401,"msg":"账号未登录"} 的兜底刷新
    """
    print('token过期需要重新登陆')
    login_data = client.login(username, password, uuid=uuid)
    expires_at = _parse_exp_time(login_data.get("expiresTime"))
    _update_tokens(
        db_conn,
        username,
        access_token=login_data.get("accessToken"),
        refresh_token=login_data.get("refreshToken"),
        expires_at=expires_at,
        user_id=login_data.get("userId"),
        has_order=login_data.get("hasOrder"),
    )


def get_cim_client_for_username(
    db_conn: Any,
    username: Optional[str] = None,
    *,
    safety_margin_seconds: int = DEFAULT_SAFETY_MARGIN_SECONDS,
    config: Optional["CIMConfig"] = None,
    uuid: str = "",
    rcustomerno: Optional[str] = None,
    user_id: Optional[str] = None,
) -> CIMClient:
    """
    工厂方法：基于 cs_user_info 的 token 复用逻辑，返回已配置好的 CIMClient。

    步骤：
    1. 按 username 读取 cs_user_info 记录；
    2. 若 token 未过期，直接 set_token；
    3. 若 token 缺失或过期，用存储的 cs_password 自动登录并更新 token 信息。
    """
    # 兼容：优先按传入的 rcustomerno / user_id 查询，否则按 username。
    query_column = "username"
    query_value = username
    if rcustomerno:
        query_column = "Rcustomerno"
        query_value = rcustomerno
    if user_id:
        query_column = "userId"
        query_value = user_id

    if not query_value:
        raise ValueError("必须提供 username、rcustomerno 或 user_id 之一用于查询。")

    record = _fetch_user_record(db_conn, query_value, column=query_column)
    if not record:
        raise ValueError(f"未找到对应记录，查询字段 {query_column} 值 {query_value}")

    stored_username = record.get("cs_name") or username or query_value
    stored_password = record.get("cs_password")
    if not stored_password:
        raise ValueError(f"用户 {stored_username} 缺少 cs_password，无法自动登录")

    client = CIMClient(config=config)

    # 注入：调用过程中 token 失效（返回 {"code":401,"msg":"账号未登录"}）时，自动重登并写回数据库
    client.set_auto_relogin_handler(
        lambda: _relogin_and_persist(
            client,
            db_conn,
            username=stored_username,
            password=stored_password,
            uuid=uuid,
        )
    )

    if _is_token_valid(record, safety_margin_seconds):
        client.set_token(record["token"])
        expires_at = _parse_exp_time(record.get("exp_time"))
        client.expires_time = expires_at
        client.refresh_token = record.get("refreshToken")
        client.user_id = record.get("userId")
        client.has_order = record.get("hasOrder")
        return client
    _relogin_and_persist(client, db_conn, username=stored_username, password=stored_password, uuid=uuid)
    return client
