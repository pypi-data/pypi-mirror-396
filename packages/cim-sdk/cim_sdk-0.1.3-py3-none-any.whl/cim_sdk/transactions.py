import datetime
from typing import Any, Dict

from .subapi import CimSubAPI


class TransactionsAPI(CimSubAPI):
    """
    财务流水 / 交易记录相关接口
    """

    def get_records(
        self,
        start_date: str,
        end_date: str,
        *,
        page_no: int = 1,
        page_size: int = 500,
        type_: str = "ALL",
        keyword: str = "",
    ) -> Dict[str, Any]:
        """
        /transaction-record
        """
        params = {
            "startDate": start_date,
            "endDate": end_date,
            "pageNo": str(page_no),
            "pageSize": str(page_size),
            "type": type_,
            "keyWord": keyword,
        }
        return self._request("GET", "/transaction-record", params=params)

    def get_recent_records(self, past_days: int = 3, **kwargs: Any) -> Dict[str, Any]:
        """
        获取最近 N 天的流水（简单封装）
        """
        today = datetime.date.today()
        start = today - datetime.timedelta(days=past_days)
        return self.get_records(
            start_date=start.strftime("%Y-%m-%d"),
            end_date=today.strftime("%Y-%m-%d"),
            **kwargs,
        )
