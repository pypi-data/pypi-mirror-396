import datetime

from cim_sdk.token_manager import get_cim_client_for_username


class _FakeCursor:
    def __init__(self, future_seconds: int = 3600):
        self.executed_sql = None
        self.executed_params = None
        self.future = future_seconds

    def execute(self, sql, params):
        self.executed_sql = sql
        self.executed_params = params

    def fetchone(self):
        # 返回 dict，避免依赖 description
        exp_time = (datetime.datetime.now() + datetime.timedelta(seconds=self.future)).strftime("%Y-%m-%d %H:%M:%S")
        return {
            "username": "user-1",
            "cs_password": "pwd",
            "Rcustomerno": "CUST-9",
            "token": "token-abc",
            "exp_time": exp_time,
            "exp_times_tamp": str(int(datetime.datetime.now().timestamp()) + self.future),
            "refreshToken": "r1",
            "userId": "U100",
            "hasOrder": 1,
        }

    def close(self):
        pass


class _FakeDB:
    def __init__(self, future_seconds: int = 3600):
        self.cursor_obj = _FakeCursor(future_seconds)

    def cursor(self):
        return self.cursor_obj

    def commit(self):
        pass


def _assert_query(column_name: str, value: str):
    db = _FakeDB()
    client = get_cim_client_for_username(
        db,
        username=None,
        rcustomerno=value if column_name == "Rcustomerno" else None,
        user_id=value if column_name == "userId" else None,
    )
    sql = db.cursor_obj.executed_sql.lower()
    assert column_name.lower() in sql
    assert db.cursor_obj.executed_params == (value,)
    assert client.token == "token-abc"


def test_query_by_rcustomerno():
    _assert_query("Rcustomerno", "CUST-9")


def test_query_by_user_id():
    _assert_query("userId", "U100")
