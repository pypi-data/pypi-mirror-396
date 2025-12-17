import datetime

from cim_sdk.orders import OrdersAPI
from cim_sdk.transactions import TransactionsAPI


def test_pick_cheapest_express_selects_min_total_cost():
    express_list = [
        {"expressName": "A", "price": "10.00", "dgFee": "1.00"},
        {"expressName": "B", "price": "6.00", "dgFee": "0.50"},
        {"expressName": "C", "price": "5.50", "dgFee": "2.00"},
    ]

    result = OrdersAPI.pick_cheapest_express(express_list)

    assert result["expressName"] == "B"


def test_get_recent_records_builds_expected_params():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=2)

    class DummyClient:
        def __init__(self):
            self.last_request = None

        def request(self, method, path, params=None, json=None, headers=None):
            self.last_request = {
                "method": method,
                "path": path,
                "params": params,
            }
            return {"ok": True}

    dummy_client = DummyClient()
    api = TransactionsAPI(dummy_client)
    api.get_recent_records(past_days=2, page_size=50, keyword="foo")

    params = dummy_client.last_request["params"]
    assert dummy_client.last_request["path"] == "/transaction-record"
    assert params["startDate"] == start.strftime("%Y-%m-%d")
    assert params["endDate"] == today.strftime("%Y-%m-%d")
    assert params["pageSize"] == "50"
    assert params["keyWord"] == "foo"
