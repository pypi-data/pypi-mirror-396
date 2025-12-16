import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .subapi import CimSubAPI
from .http import CIMApiError


class ProductsAPI(CimSubAPI):
    """
    产品相关接口（预留，将来你有 /product/... 之类的接口再慢慢加）
    """

    def _export_product_payload(
        self,
        *,
        category_ids: Optional[List[Any]],
        item_no: str,
        keyword: str,
        brands: Optional[List[str]],
        export_type: int,
    ) -> Dict[str, Any]:
        return {
            "categoryIds": category_ids or [],
            "itemNo": item_no,
            "keyword": keyword,
            "brands": brands or [],
            "exportType": export_type,
        }

    def _resolve_filename(self, resp: requests.Response) -> Optional[str]:
        content_disp = resp.headers.get("content-disposition") or resp.headers.get("Content-Disposition")
        if not content_disp:
            return None
        match = re.search(r'filename="?([^";]+)"?', content_disp)
        return match.group(1) if match else None

    def _export_product_request(self, payload: Dict[str, Any]) -> requests.Response:
        url = f"{self.client.config.base_url.rstrip('/')}/product/exportProductList"
        headers = self.client._headers(
            {"content-type": "application/json", "origin": "https://cim.cameronsino.com"}
        )
        try:
            resp = self.client.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.client.config.timeout,
                stream=True,
            )
        except requests.RequestException as exc:
            raise CIMApiError(f"网络请求异常: {exc}") from exc

        if not resp.ok:
            raise CIMApiError(f"CIM API 调用失败: HTTP {resp.status_code}", status_code=resp.status_code, response=resp)
        return resp

    def export_product_list_bytes(
        self,
        *,
        category_ids: Optional[List[Any]] = None,
        item_no: str = "",
        keyword: str = "",
        brands: Optional[List[str]] = None,
        export_type: int = 2,
    ) -> bytes:
        """
        /product/exportProductList
        返回 Excel 二进制内容，适合上层自行存储或直接返回给浏览器。
        """
        payload = self._export_product_payload(
            category_ids=category_ids,
            item_no=item_no,
            keyword=keyword,
            brands=brands,
            export_type=export_type,
        )
        resp = self._export_product_request(payload)
        return resp.content

    def export_product_list_to_file(
        self,
        *,
        save_to: Optional[str] = None,
        category_ids: Optional[List[Any]] = None,
        item_no: str = "",
        keyword: str = "",
        brands: Optional[List[str]] = None,
        export_type: int = 2,
        chunk_size: int = 8192,
    ) -> Path:
        """
        /product/exportProductList
        流式写入 Excel 文件，默认使用响应文件名（若响应未提供则使用 export_product_list.xlsx）。
        """
        payload = self._export_product_payload(
            category_ids=category_ids,
            item_no=item_no,
            keyword=keyword,
            brands=brands,
            export_type=export_type,
        )
        resp = self._export_product_request(payload)
        filename = save_to or self._resolve_filename(resp) or "export_product_list.xlsx"
        target_path = Path(filename)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with target_path.open("wb") as fp:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    fp.write(chunk)

        return target_path

    def get_product_record_list(
        self,
        *,
        type_: str = "",
        item_no: str = "",
        keyword: str = "",
        page_no: int = 1,
        page_size: int = 30,
        date_query_start: str = "",
        date_query_end: str = "",
    ) -> Dict[str, Any]:
        """
        /product/getProductRecordList
        对应你提供的 curl，查询产品操作记录或变更记录。
        """
        payload: Dict[str, Any] = {
            "type": type_,
            "itemNo": item_no,
            "keyword": keyword,
            "pageNo": page_no,
            "pageSize": page_size,
            "dateQueryStart": date_query_start,
            "dateQueryEnd": date_query_end,
        }
        return self._request(
            "POST",
            "/product/getProductRecordList",
            json=payload,
            headers={"content-type": "application/json", "origin": "https://cim.cameronsino.com"},
        )

    def get_product_price_list(
        self,
        *,
        type_: str = "",
        item_no: str = "",
        keyword: str = "",
        ref: str = "",
        shipment_region: str = "",
        date_query_start: Optional[str] = None,
        date_query_end: Optional[str] = None,
        page_no: int = 1,
        page_size: int = 30,
    ) -> Dict[str, Any]:
        """
        /product/getProductPriceList
        对应你提供的 curl，用于查询产品价格列表。
        """
        payload: Dict[str, Any] = {
            "type": type_,
            "itemNo": item_no,
            "keyword": keyword,
            "ref": ref,
            "shipmentRegion": shipment_region,
            "dateQueryStart": date_query_start,
            "dateQueryEnd": date_query_end,
            "pageNo": page_no,
            "pageSize": page_size,
        }
        return self._request(
            "POST",
            "/product/getProductPriceList",
            json=payload,
            headers={"content-type": "application/json", "origin": "https://cim.cameronsino.com"},
        )

    def get_product_list(
        self,
        *,
        category_ids: Optional[List[Any]] = None,
        item_no: str = "",
        keyword: str = "",
        brands: Optional[List[str]] = None,
        page_no: int = 1,
        page_size: int = 30,
    ) -> Dict[str, Any]:
        """
        /product/getProductList
        对应你提供的 curl，用于查询产品列表。
        """
        payload: Dict[str, Any] = {
            "categoryIds": category_ids or [],
            "itemNo": item_no,
            "keyword": keyword,
            "brands": brands or [],
            "pageNo": page_no,
            "pageSize": page_size,
        }
        return self._request(
            "POST",
            "/product/getProductList",
            json=payload,
            headers={"content-type": "application/json", "origin": "https://cim.cameronsino.com"},
        )

    def get_product_info(self, item_no: str) -> Dict[str, Any]:
        """
        /product/getProductInfo?itemNo=CS-TRX500SL （POST，无 body）
        根据 itemNo 获取单个产品详情。
        """
        params = {"itemNo": item_no}
        return self._request(
            "POST",
            "/product/getProductInfo",
            params=params,
            headers={"origin": "https://cim.cameronsino.com"},
        )
