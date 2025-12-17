from decimal import Decimal
from typing import Any, Dict, List, Optional

from .subapi import CimSubAPI


class OrdersAPI(CimSubAPI):
    """
    订单相关接口：dropship 报价、创建、分页、详情、取消
    """

    # ---- 报价 ----

    def get_total_price(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        /dropship/order/total/price
        payload 结构参考你之前抓到的 curl
        """
        return self._request(
            "POST",
            "/dropship/order/total/price",
            json=payload,
            headers={"content-type": "application/json", "origin": "https://cim.cameronsino.com"},
        )

    @staticmethod
    def pick_cheapest_express(express_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        根据 price + dgFee 选出最便宜的一条：
        [
          {"expressName": "USPS","price": "6.28","dgFee": "0.00","currency": "USD"},
          ...
        ]
        """
        if not express_list:
            raise ValueError("express_list 不能为空")

        def total_cost(x: Dict[str, Any]) -> Decimal:
            return Decimal(str(x.get("price") or 0)) + Decimal(str(x.get("dgFee") or 0))

        return min(express_list, key=total_cost)

    # ---- 创建 Dropship 订单 ----

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        /dropship/create
        """
        return self._request(
            "POST",
            "/dropship/create",
            json=payload,
            headers={"content-type": "application/json", "origin": "https://cim.cameronsino.com"},
        )

    # ---- 分页查询 ----

    def list_page(
            self,
            page_no: int = 1,
            page_size: int = 20,
            *,
            date: str = "",
            start_date: str = "",
            end_date: str = "",
            item_no: str = "",
            order_status: str = "",
            search: str = "",
            shipment_region: str = "",
            type_: str = "",
    ) -> Dict[str, Any]:
        """
        /dropship/page
        """
        params = {
            "pageNo": str(page_no),
            "pageSize": str(page_size),
            "date": date,
            "startDate": start_date,
            "endDate": end_date,
            "itemNo": item_no,
            "orderStatus": order_status,
            "search": search,
            "shipmentRegion": shipment_region,
            "type": type_,
        }
        return self._request("GET", "/dropship/page", params=params)

    # ---- 详情 ----

    def get_detail(self, dropship_id: str) -> Dict[str, Any]:
        """
        /dropship/detail?dropShipId=US-xxxx
        """
        params = {"dropShipId": dropship_id}
        return self._request("GET", "/dropship/detail", params=params)

    # ---- 取消 ----

    def cancel(self, dropship_id: str) -> Dict[str, Any]:
        """
        对于 pending状态的订单取消
        /dropship/cancel?dropshipId=US-xxxx  （PUT）
        """
        params = {"dropshipId": dropship_id}
        return self._request(
            "PUT",
            "/dropship/cancel",
            params=params,
            headers={"origin": "https://cim.cameronsino.com"},
        )

    def approve_cancel(
            self,
            order_id: str,
            reason: str = 'Incompleted address',
            description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        对取消中的订单进行审批。

        :param order_id: 订单号，例如 "US-3734389"
        :param reason: 取消原因，例如 "Out of stock"
        :param description: 备注说明，可为 None
        :return: 后端返回的 JSON 数据
        """
        payload: Dict[str, Any] = {
            "orderId": order_id,
            "reason": reason,
            "description": description,
        }
        return self._request(
            method="PUT",
            path="/dropship/cancel/approval",
            json=payload,
        )
