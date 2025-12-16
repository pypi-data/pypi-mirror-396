"""
FinStock API客户端

提供期货和股票K线数据获取功能的主要客户端类。
"""

import requests
from datetime import datetime
from typing import Optional, Union, Dict, Any
from urllib.parse import urljoin

from .models import UnifiedKlineResponse, KLineData


class FinStockClient:
    """FinStock API客户端"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        初始化API客户端

        Args:
            base_url: API基础URL，默认为 http://localhost:8000
            timeout: 请求超时时间（秒）
            headers: 额外的请求头
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        # 默认请求头
        self.default_headers = {
            "User-Agent": "FinStock-Python-Client/0.1.0",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # 合并额外请求头
        if headers:
            self.default_headers.update(headers)

        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        发送HTTP请求

        Args:
            method: HTTP方法
            endpoint: API端点
            params: URL参数
            json_data: JSON请求体数据

        Returns:
            requests.Response对象

        Raises:
            requests.RequestException: 请求失败时抛出
        """
        url = urljoin(self.base_url + "/", endpoint.lstrip('/'))

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"API请求失败: {e}")

    def get_kline(
        self,
        symbol: str,
        interval: str,
        start_datetime: Optional[Union[datetime, str]] = None,
        end_datetime: Optional[Union[datetime, str]] = None,
    ) -> KLineData:
        """
        获取K线数据

        Args:
            symbol: 期货合约代码，如 CU2401.SHFE
            interval: 时间间隔，支持 1m, 5m, 15m, 1h, 1d, 1w, 1M
            start_datetime: 开始时间（包含）
            end_datetime: 结束时间（包含），默认为现在

        Returns:
            KLineData对象，包含K线数据并可转换为DataFrame

        Raises:
            ValueError: 参数错误时抛出
            requests.RequestException: API请求失败时抛出

        Example:
            >>> client = FinStockClient()
            >>> kline_data = client.get_kline("CU2401.SHFE", "1d")
            >>> df = kline_data.to_dataframe()
            >>> print(df.head())
        """
        # 参数验证
        if not symbol:
            raise ValueError("symbol参数不能为空")

        valid_intervals = ["1m", "5m", "15m", "1h", "1d", "1w", "1M"]
        if interval not in valid_intervals:
            raise ValueError(f"interval参数无效，支持: {', '.join(valid_intervals)}")

        # 构建请求参数
        params = {
            "symbol": symbol,
            "interval": interval,
        }

        if start_datetime:
            if isinstance(start_datetime, datetime):
                params["start_datetime"] = start_datetime.isoformat()
            else:
                params["start_datetime"] = start_datetime

        if end_datetime:
            if isinstance(end_datetime, datetime):
                params["end_datetime"] = end_datetime.isoformat()
            else:
                params["end_datetime"] = end_datetime

        # 发送请求
        response = self._make_request("GET", "/user/v1/kline", params=params)

        # 解析响应
        response_data = response.json()
        kline_response = UnifiedKlineResponse(**response_data)

        # 检查响应状态
        if kline_response.code != 0:
            raise ValueError(f"API返回错误: {kline_response.msg}")

        if not kline_response.data:
            raise ValueError("API返回的数据为空")

        return KLineData(kline_response.data)

    def get_kline_dataframe(
        self,
        symbol: str,
        interval: str,
        start_datetime: Optional[Union[datetime, str]] = None,
        end_datetime: Optional[Union[datetime, str]] = None,
    ) -> "pandas.DataFrame":
        """
        直接获取K线数据的DataFrame格式

        Args:
            symbol: 期货合约代码，如 CU2401.SHFE
            interval: 时间间隔，支持 1m, 5m, 15m, 1h, 1d, 1w, 1M
            start_datetime: 开始时间（包含）
            end_datetime: 结束时间（包含），默认为现在

        Returns:
            pandas.DataFrame对象

        Example:
            >>> client = FinStockClient()
            >>> df = client.get_kline_dataframe("CU2401.SHFE", "1d")
            >>> print(df.head())
        """
        kline_data = self.get_kline(symbol, interval, start_datetime, end_datetime)
        return kline_data.to_dataframe()

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            API服务是否正常

        Example:
            >>> client = FinStockClient()
            >>> if client.health_check():
            ...     print("API服务正常")
        """
        try:
            response = self._make_request("GET", "/common/v1/health")
            response_data = response.json()
            return response_data.get("code", -1) == 0
        except requests.RequestException:
            return False

    def get_openapi_spec(self) -> dict:
        """
        获取OpenAPI规范

        Returns:
            OpenAPI规范字典

        Example:
            >>> client = FinStockClient()
            >>> spec = client.get_openapi_spec()
            >>> print(spec["info"]["title"])
        """
        try:
            response = self._make_request("GET", "/openapi.json")
            return response.json()
        except requests.RequestException as e:
            raise requests.RequestException(f"获取OpenAPI规范失败: {e}")

    def close(self):
        """关闭客户端会话"""
        self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()