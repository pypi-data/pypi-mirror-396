"""
FinStock客户端测试

测试API客户端的核心功能。
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from finstock import FinStockClient
from finstock.models import UnifiedKline, UnifiedKlineResponse


class TestFinStockClient:
    """FinStock客户端测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.client = FinStockClient(base_url="http://test.example.com")

    def teardown_method(self):
        """测试后的清理"""
        self.client.close()

    def test_client_initialization(self):
        """测试客户端初始化"""
        assert self.client.base_url == "http://test.example.com"
        assert self.client.timeout == 30
        assert self.client.session is not None

    def test_client_initialization_with_options(self):
        """测试带选项的客户端初始化"""
        custom_headers = {"Custom-Header": "test"}
        client = FinStockClient(
            base_url="https://api.example.com",
            timeout=60,
            headers=custom_headers,
        )
        try:
            assert client.base_url == "https://api.example.com"
            assert client.timeout == 60
            assert "Custom-Header" in client.session.headers
        finally:
            client.close()

    def test_validate_symbol_format(self):
        """测试合约代码格式验证"""
        from finstock.utils import validate_symbol

        # 有效的合约代码
        assert validate_symbol("CU2401.SHFE") is True
        assert validate_symbol("AU2402.SHFE") is True
        assert validate_symbol("SR2405.CZCE") is True
        assert validate_symbol("I2403.DCE") is True

        # 无效的合约代码
        assert validate_symbol("INVALID") is False
        assert validate_symbol("") is False
        assert validate_symbol(None) is False

    def test_validate_interval_format(self):
        """测试时间间隔格式验证"""
        from finstock.utils import validate_interval

        # 有效的时间间隔
        assert validate_interval("1m") is True
        assert validate_interval("5m") is True
        assert validate_interval("15m") is True
        assert validate_interval("1h") is True
        assert validate_interval("1d") is True
        assert validate_interval("1w") is True
        assert validate_interval("1M") is True

        # 无效的时间间隔
        assert validate_interval("30m") is False
        assert validate_interval("2h") is False
        assert validate_interval("") is False
        assert validate_interval("invalid") is False

    @patch('finstock.client.requests.Session.request')
    def test_health_check_success(self, mock_request):
        """测试健康检查成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.json.return_value = {"code": 0, "msg": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        result = self.client.health_check()
        assert result is True

    @patch('finstock.client.requests.Session.request')
    def test_health_check_failure(self, mock_request):
        """测试健康检查失败"""
        # 模拟请求异常
        import requests
        mock_request.side_effect = requests.RequestException("Network error")

        result = self.client.health_check()
        assert result is False

    @patch('finstock.client.requests.Session.request')
    def test_get_kline_success(self, mock_request):
        """测试获取K线数据成功"""
        # 模拟API响应数据
        mock_response_data = {
            "code": 0,
            "msg": "success",
            "timestamp": "2024-01-15T10:30:00",
            "data": {
                "symbol": "CU2401.SHFE",
                "interval": "1d",
                "date_time": ["2024-01-15T00:00:00", "2024-01-16T00:00:00"],
                "open": [68500.0, 68650.0],
                "close": [68650.0, 68800.0],
                "high": [68800.0, 68950.0],
                "low": [68200.0, 68400.0],
                "volume": [125680.0, 132450.0],
                "total_turnover": [8628456000.0, 9123456000.0],
                "open_interest": [185420.0, 186850.0],
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # 调用API
        kline_data = self.client.get_kline(
            symbol="CU2401.SHFE",
            interval="1d",
            start_datetime="2024-01-15",
            end_datetime="2024-01-16",
        )

        # 验证结果
        assert kline_data.data.symbol == "CU2401.SHFE"
        assert kline_data.data.interval == "1d"
        assert len(kline_data) == 2
        assert kline_data.data.open[0] == 68500.0

    @patch('finstock.client.requests.Session.request')
    def test_get_kline_api_error(self, mock_request):
        """测试获取K线数据API错误"""
        # 模拟API错误响应
        mock_response_data = {
            "code": 1001,
            "msg": "合约不存在",
            "timestamp": "2024-01-15T10:30:00",
            "data": None
        }

        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        # 验证抛出异常
        with pytest.raises(ValueError, match="API返回错误"):
            self.client.get_kline(symbol="INVALID", interval="1d")

    def test_get_kline_invalid_params(self):
        """测试无效参数"""
        # 测试空symbol
        with pytest.raises(ValueError, match="symbol参数不能为空"):
            self.client.get_kline(symbol="", interval="1d")

        # 测试无效interval
        with pytest.raises(ValueError, match="interval参数无效"):
            self.client.get_kline(symbol="CU2401.SHFE", interval="invalid")

    def test_context_manager(self):
        """测试上下文管理器"""
        with FinStockClient() as client:
            assert client.session is not None
        # 上下文管理器应该自动关闭会话

    def test_dataframe_conversion(self):
        """测试DataFrame转换"""
        # 创建测试数据
        unified_kline = UnifiedKline(
            symbol="CU2401.SHFE",
            interval="1d",
            date_time=[datetime(2024, 1, 15), datetime(2024, 1, 16)],
            open=[68500.0, 68650.0],
            close=[68650.0, 68800.0],
            high=[68800.0, 68950.0],
            low=[68200.0, 68400.0],
            volume=[125680.0, 132450.0],
            total_turnover=[8628456000.0, 9123456000.0],
            open_interest=[185420.0, 186850.0],
        )

        from finstock.models import KLineData
        kline_data = KLineData(unified_kline)
        df = kline_data.to_dataframe()

        # 验证DataFrame
        assert len(df) == 2
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume', 'turnover', 'open_interest']
        assert df.attrs['symbol'] == "CU2401.SHFE"
        assert df.attrs['interval'] == "1d"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])