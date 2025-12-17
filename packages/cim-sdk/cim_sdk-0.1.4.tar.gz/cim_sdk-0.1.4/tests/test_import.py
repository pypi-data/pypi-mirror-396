from cim_sdk import CIMClient


def test_client_has_subapis():
    client = CIMClient()
    assert hasattr(client, "orders")
    assert hasattr(client, "transactions")
    assert hasattr(client, "products")
