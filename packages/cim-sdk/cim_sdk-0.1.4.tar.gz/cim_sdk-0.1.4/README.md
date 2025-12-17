# cim-sdk

非官方的 CameronSino CIM Admin API Python SDK。支持通过 `pip install .` 安装，提供订单与交易记录的便捷访问，并附带基于 `cs_user_info` 的 token 复用工厂。

## 安装

在项目根目录执行：

```bash
python -m pip install .
```

## 快速开始

```python
from cim_sdk import CIMClient

# 方式 1：提供账号直接登录
client = CIMClient.from_credentials("username", "password")

# 方式 2：已有 token 直接复用
another = CIMClient(token="EXISTING_ACCESS_TOKEN")

# Dropship 订单详情
detail = client.orders.get_detail("US-3729797")
print(detail)

# 最近三天的交易记录
records = client.transactions.get_recent_records(page_size=100)
print(records)
```

## Token 持久化与自动登录（业务侧）

SDK 内置了工厂 `cim_sdk.token_manager.get_cim_client_for_username`，按照 `cs_user_info` 表结构（见 `AGENTS.md`）工作：

```python
from cim_sdk.token_manager import get_cim_client_for_username

# db_conn 需实现标准 DB-API（cursor/execute/commit），如 PyMySQL 的连接对象
client = get_cim_client_for_username(db_conn, "andy")

# 如果数据库里 token 未过期，将直接 set_token；否则自动调用 /auth/login 并写回新 token。
orders = client.orders.list_page(page_no=1, page_size=20)
```

## 开发与测试

- 运行基础单测（需安装 pytest）：`python -m pytest`
- 本地打包验证安装：`python -m pip install .`

## 目录结构

- `cim_sdk/`：SDK 代码与 token 工厂
- `tests/`：简单的导入测试与使用示例
- `pyproject.toml`：打包配置

# 1. 修改 version（pyproject.toml / setup.py）→ 比如 0.1.2

# 2. 清理 + 打包
rm -rf dist build *.egg-info
python -m build

# 3. 上传到 TestPyPI
python -m twine upload --repository testpypi dist/*

# 4. 本地用 TestPyPI 测试安装
pip install --no-cache-dir --upgrade \
  --index-url https://test.pypi.org/simple \
  --extra-index-url https://pypi.org/simple \
  cim-sdk==0.1.2

# 5. 没问题后，上传到正式 PyPI
python -m twine upload dist/*
