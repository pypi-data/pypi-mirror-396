"""
工具函数模块

提供常用的辅助函数和数据验证功能。
"""

from datetime import datetime
from typing import List, Optional, Union


def validate_symbol(symbol: str) -> bool:
    """
    验期货合约代码格式

    Args:
        symbol: 期货合约代码，如 CU2401.SHFE

    Returns:
        是否为有效的合约代码

    Example:
        >>> validate_symbol("CU2401.SHFE")
        True
        >>> validate_symbol("INVALID")
        False
    """
    if not symbol or len(symbol) < 9:
        return False

    # 检查交易所后缀
    valid_exchanges = ["SHFE", "DCE", "CZCE", "CFFEX", "INE"]

    # 尝试分割交易所后缀
    for exchange in valid_exchanges:
        if symbol.endswith(f".{exchange}"):
            contract_part = symbol[:-len(f".{exchange}")]
            # 检查合约部分格式 (品种代码 + 月份 + 年份)
            if len(contract_part) >= 4 and contract_part[-4:].isdigit():
                return True

    return False


def validate_interval(interval: str) -> bool:
    """
    验证时间间隔格式

    Args:
        interval: 时间间隔，如 1m, 5m, 15m, 1h, 1d, 1w, 1M

    Returns:
        是否为有效的时间间隔
    """
    valid_intervals = ["1m", "5m", "15m", "1h", "1d", "1w", "1M"]
    return interval in valid_intervals


def parse_datetime(datetime_str: Optional[Union[str, datetime]]) -> Optional[datetime]:
    """
    解析日期时间字符串

    Args:
        datetime_str: 日期时间字符串或datetime对象

    Returns:
        解析后的datetime对象，如果输入为None则返回None

    Example:
        >>> dt = parse_datetime("2024-01-15T10:30:00")
        >>> isinstance(dt, datetime)
        True
    """
    if datetime_str is None:
        return None

    if isinstance(datetime_str, datetime):
        return datetime_str

    # 尝试解析不同格式的日期时间字符串
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y/%m/%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"无法解析日期时间格式: {datetime_str}")


def get_trading_sessions() -> dict:
    """
    获取中国期货市场交易时段

    Returns:
        交易时段字典，包含不同交易所的交易时间

    Example:
        >>> sessions = get_trading_sessions()
        >>> print(sessions["SHFE"]["day_session"])
        ['09:00-10:15', '10:30-11:30', '13:30-15:00']
    """
    return {
        "SHFE": {  # 上海期货交易所
            "day_session": ["09:00-10:15", "10:30-11:30", "13:30-15:00"],
            "night_session": ["21:00-02:30"],  # 部分品种有夜盘
        },
        "DCE": {   # 大连商品交易所
            "day_session": ["09:00-10:15", "10:30-11:30", "13:30-15:00"],
            "night_session": ["21:00-23:00"],  # 部分品种有夜盘
        },
        "CZCE": {  # 郑州商品交易所
            "day_session": ["09:00-10:15", "10:30-11:30", "13:30-15:00"],
            "night_session": ["21:00-23:30"],  # 部分品种有夜盘
        },
        "CFFEX": {  # 中国金融期货交易所
            "day_session": ["09:30-11:30", "13:00-15:00"],
            "night_session": [],  # 无夜盘
        },
        "INE": {   # 上海国际能源交易中心
            "day_session": ["09:00-10:15", "10:30-11:30", "13:30-15:00"],
            "night_session": ["21:00-02:30"],  # 有夜盘
        },
    }


def is_trading_time(symbol: str, current_time: Optional[datetime] = None) -> bool:
    """
    判断指定时间是否为交易时间

    Args:
        symbol: 期货合约代码
        current_time: 当前时间，默认为系统当前时间

    Returns:
        是否为交易时间

    Example:
        >>> is_trading_time("CU2401.SHFE")
        True
    """
    if current_time is None:
        current_time = datetime.now()

    # 提取交易所代码
    if "." not in symbol:
        return False

    exchange = symbol.split(".")[-1].upper()
    if exchange not in get_trading_sessions():
        return False

    # 获取交易时段
    sessions = get_trading_sessions()[exchange]
    current_str = current_time.strftime("%H:%M")

    # 检查日盘
    for session in sessions["day_session"]:
        start_time, end_time = session.split("-")
        if start_time <= current_str <= end_time:
            return True

    # 检查夜盘
    for session in sessions["night_session"]:
        start_time, end_time = session.split("-")
        # 处理跨日的情况
        if start_time <= current_str or current_str <= end_time:
            return True

    return False


def get_exchange_info(symbol: str) -> dict:
    """
    获取期货交易所信息

    Args:
        symbol: 期货合约代码

    Returns:
        交易所信息字典

    Example:
        >>> info = get_exchange_info("CU2401.SHFE")
        >>> print(info["name"])
        上海期货交易所
    """
    exchange_mapping = {
        "SHFE": {
            "name": "上海期货交易所",
            "name_en": "Shanghai Futures Exchange",
            "products": ["铜", "铝", "锌", "铅", "镍", "锡", "黄金", "白银", "螺纹钢", "热轧卷板", "原油", "燃料油", "石油沥青", "天然橡胶", "纸浆"],
        },
        "DCE": {
            "name": "大连商品交易所",
            "name_en": "Dalian Commodity Exchange",
            "products": ["玉米", "玉米淀粉", "黄大豆1号", "黄大豆2号", "豆粕", "豆油", "棕榈油", "聚丙烯", "聚氯乙烯", "线型低密度聚乙烯", "焦炭", "焦煤", "铁矿石", "鸡蛋", "胶合板", "纤维板", "聚丙烯", "乙二醇", "苯乙烯", "液化石油气"],
        },
        "CZCE": {
            "name": "郑州商品交易所",
            "name_en": "Zhengzhou Commodity Exchange",
            "products": ["强麦", "普麦", "棉花", "棉纱", "菜籽油", "菜籽粕", "花生仁", "白砂糖", "苹果", "红枣", "动力煤", "甲醇", "精对苯二甲酸", "短纤", "玻璃", "纯碱", "尿素", "锰硅", "硅铁", "普麦", "强麦"],
        },
        "CFFEX": {
            "name": "中国金融期货交易所",
            "name_en": "China Financial Futures Exchange",
            "products": ["沪深300股指期货", "上证50股指期货", "中证500股指期货", "2年期国债期货", "5年期国债期货", "10年期国债期货"],
        },
        "INE": {
            "name": "上海国际能源交易中心",
            "name_en": "Shanghai International Energy Exchange",
            "products": ["原油", "低硫燃料油", "20号胶"],
        },
    }

    if "." not in symbol:
        return {}

    exchange = symbol.split(".")[-1].upper()
    return exchange_mapping.get(exchange, {})