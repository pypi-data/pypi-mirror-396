"""
数据模型定义

定义API返回的数据结构和pandas DataFrame的转换逻辑。
"""

from datetime import datetime
from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, validator


class BaseResponse(BaseModel):
    """API响应基类"""
    code: int = Field(default=0, description="状态码，0表示成功，非0表示失败")
    msg: str = Field(default="success", description="响应消息")
    timestamp: datetime = Field(description="响应时间戳")


class BaseResponseData(BaseResponse):
    """带数据的API响应基类"""
    data: Optional[Any] = Field(default=None, description="响应数据")


class UnifiedKline(BaseModel):
    """统一K线数据模型"""
    symbol: str = Field(description="期货合约代码，格式: CU2401.SHFE")
    interval: str = Field(description="时间间隔: 1m, 5m, 15m, 1h, 1d, 1w, 1M")
    date_time: List[datetime] = Field(description="K线时间列表")
    open: List[float] = Field(description="开盘价列表")
    close: List[float] = Field(description="收盘价列表")
    high: List[float] = Field(description="最高价列表")
    low: List[float] = Field(description="最低价列表")
    total_turnover: List[float] = Field(description="成交额列表")
    volume: List[float] = Field(description="成交量列表")

    # 可选字段
    prev_close: Optional[List[float]] = Field(default=None, description="昨日收盘价")
    limit_up: Optional[List[float]] = Field(default=None, description="涨停价（仅限日线数据）")
    limit_down: Optional[List[float]] = Field(default=None, description="跌停价（仅限日线数据）")
    num_trades: Optional[List[int]] = Field(default=None, description="成交笔数")
    settlement: Optional[List[float]] = Field(default=None, description="结算价（仅限期货期权日线数据）")
    prev_settlement: Optional[List[float]] = Field(default=None, description="昨日结算价（仅限期货期权日线数据）")
    open_interest: Optional[List[float]] = Field(default=None, description="累计持仓量（期货期权专用）")
    trading_date: Optional[List[str]] = Field(default=None, description="交易日期（仅限期货分钟线数据），格式：yyyymmdd")
    day_session_open: Optional[List[float]] = Field(default=None, description="日盘开盘价（仅限期货期权日线数据）")
    strike_price: Optional[List[float]] = Field(default=None, description="行权价，仅限期权日线数据")
    contract_multiplier: Optional[List[float]] = Field(default=None, description="合约乘数，仅限期权日线数据")
    iopv: Optional[List[float]] = Field(default=None, description="场内基金实时估算净值")
    dominant_id: Optional[List[str]] = Field(default=None, description="实际合约的order_book_id，对应期货888系主力连续合约")


class UnifiedKlineResponse(BaseResponseData):
    """统一K线数据响应"""
    data: Optional[UnifiedKline] = Field(default=None, description="K线数据")


class KLineData:
    """K线数据封装类，提供转换为DataFrame的功能"""

    def __init__(self, unified_kline: UnifiedKline):
        self.data = unified_kline

    def to_dataframe(self) -> "pandas.DataFrame":
        """转换为pandas DataFrame"""
        import pandas as pd

        # 构建基础数据
        df_data = {
            'datetime': self.data.date_time,
            'open': self.data.open,
            'high': self.data.high,
            'low': self.data.low,
            'close': self.data.close,
            'volume': self.data.volume,
            'turnover': self.data.total_turnover,
        }

        # 添加可选字段
        if self.data.prev_close:
            df_data['prev_close'] = self.data.prev_close
        if self.data.limit_up:
            df_data['limit_up'] = self.data.limit_up
        if self.data.limit_down:
            df_data['limit_down'] = self.data.limit_down
        if self.data.num_trades:
            df_data['num_trades'] = self.data.num_trades
        if self.data.settlement:
            df_data['settlement'] = self.data.settlement
        if self.data.prev_settlement:
            df_data['prev_settlement'] = self.data.prev_settlement
        if self.data.open_interest:
            df_data['open_interest'] = self.data.open_interest
        if self.data.trading_date:
            df_data['trading_date'] = self.data.trading_date
        if self.data.day_session_open:
            df_data['day_session_open'] = self.data.day_session_open
        if self.data.strike_price:
            df_data['strike_price'] = self.data.strike_price
        if self.data.contract_multiplier:
            df_data['contract_multiplier'] = self.data.contract_multiplier
        if self.data.iopv:
            df_data['iopv'] = self.data.iopv
        if self.data.dominant_id:
            df_data['dominant_id'] = self.data.dominant_id

        df = pd.DataFrame(df_data)

        # 设置datetime为索引
        df.set_index('datetime', inplace=True)
        df.index = pd.to_datetime(df.index)

        # 添加元数据
        df.attrs['symbol'] = self.data.symbol
        df.attrs['interval'] = self.data.interval

        return df

    def __len__(self) -> int:
        """返回数据条数"""
        return len(self.data.date_time)

    def __repr__(self) -> str:
        return f"KLineData(symbol='{self.data.symbol}', interval='{self.data.interval}', count={len(self)})"