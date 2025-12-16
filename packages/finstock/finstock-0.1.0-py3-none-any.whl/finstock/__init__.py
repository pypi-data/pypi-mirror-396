"""
FinStock - 中国期货股票数据获取库

通过API获取期货和股票的K线数据，并转换为pandas DataFrame格式。
"""

from .client import FinStockClient
from .models import KLineData, UnifiedKlineResponse

__version__ = "0.1.0"
__author__ = "FinStock Team"
__email__ = "contact@finstock.com"

__all__ = [
    "FinStockClient",
    "KLineData",
    "UnifiedKlineResponse",
]