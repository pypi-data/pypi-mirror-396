#!/usr/bin/env python3
"""
FinStock高级使用示例

演示更高级的功能，包括批量获取、数据分析等。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from finstock import FinStockClient
from finstock.utils import validate_symbol, get_exchange_info, is_trading_time


def advanced_analysis_example():
    """高级数据分析示例"""
    print("=== FinStock高级数据分析示例 ===\n")

    with FinStockClient() as client:
        # 检查API状态
        if not client.health_check():
            print("✗ API服务不可用")
            return

        print("✓ API服务正常")

        # 定义要分析的合约列表
        symbols = [
            "CU2401.SHFE",  # 铜
            "AL2401.SHFE",  # 铝
            "ZN2401.SHFE",  # 锌
        ]

        all_data = {}

        # 批量获取数据
        for symbol in symbols:
            print(f"\n正在获取 {symbol} 数据...")

            try:
                # 验证合约代码
                if not validate_symbol(symbol):
                    print(f"✗ 无效的合约代码: {symbol}")
                    continue

                # 获取交易所信息
                exchange_info = get_exchange_info(symbol)
                print(f"交易所: {exchange_info.get('name', '未知')}")

                # 获取K线数据
                df = client.get_kline_dataframe(
                    symbol=symbol,
                    interval="1d",
                    start_datetime="2024-01-01",
                    end_datetime="2024-01-31"
                )

                if len(df) > 0:
                    all_data[symbol] = df
                    print(f"✓ 成功获取 {len(df)} 条数据")
                else:
                    print(f"✗ {symbol} 暂无数据")

            except Exception as e:
                print(f"✗ 获取 {symbol} 数据失败: {e}")

        # 数据分析
        if all_data:
            print(f"\n=== 数据分析结果 ===")

            # 创建汇总表
            summary_data = []
            for symbol, df in all_data.items():
                if len(df) > 0:
                    latest_close = df['close'].iloc[-1]
                    period_high = df['high'].max()
                    period_low = df['low'].min()
                    total_volume = df['volume'].sum()
                    price_change = (latest_close - df['close'].iloc[0]) / df['close'].iloc[0] * 100

                    summary_data.append({
                        '合约': symbol,
                        '最新价': latest_close,
                        '期间最高': period_high,
                        '期间最低': period_low,
                        '涨跌幅(%)': round(price_change, 2),
                        '总成交量': total_volume,
                        '数据天数': len(df)
                    })

            summary_df = pd.DataFrame(summary_data)
            print("\n合约汇总:")
            print(summary_df.to_string(index=False))

            # 计算相关性
            if len(all_data) > 1:
                print(f"\n=== 价格相关性分析 ===")

                # 构建价格DataFrame
                price_df = pd.DataFrame()
                for symbol, df in all_data.items():
                    price_df[symbol] = df['close']

                # 计算相关系数
                correlation_matrix = price_df.corr()
                print("\n收盘价相关系数矩阵:")
                print(correlation_matrix.round(3))


def technical_indicators_example():
    """技术指标计算示例"""
    print("\n=== 技术指标计算示例 ===\n")

    try:
        with FinStockClient() as client:
            # 获取分钟线数据用于技术指标计算
            df = client.get_kline_dataframe(
                symbol="CU2401.SHFE",
                interval="1h",
                start_datetime=datetime.now() - timedelta(days=7),
                end_datetime=datetime.now()
            )

            if len(df) < 20:
                print("✗ 数据不足，无法计算技术指标")
                return

            print(f"✓ 获取到 {len(df)} 条小时线数据")

            # 计算移动平均线
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()

            # 计算RSI
            def calculate_rsi(prices, period=14):
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi

            df['RSI'] = calculate_rsi(df['close'])

            # 计算MACD
            def calculate_macd(prices, fast=12, slow=26, signal=9):
                exp1 = prices.ewm(span=fast).mean()
                exp2 = prices.ewm(span=slow).mean()
                macd = exp1 - exp2
                signal_line = macd.ewm(span=signal).mean()
                histogram = macd - signal_line
                return macd, signal_line, histogram

            df['MACD'], df['MACD_Signal'], df['MACD_Histogram'] = calculate_macd(df['close'])

            # 计算布林带
            df['BB_Middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

            # 显示最新数据
            print(f"\n最新技术指标数据 ({df.index[-1].strftime('%Y-%m-%d %H:%M')}):")
            latest_data = df[['close', 'MA5', 'MA10', 'MA20', 'RSI']].iloc[-1]
            for indicator, value in latest_data.items():
                if pd.notna(value):
                    print(f"{indicator}: {value:.2f}")

            # RSI信号分析
            latest_rsi = df['RSI'].iloc[-1]
            if latest_rsi > 70:
                print(f"\nRSI ({latest_rsi:.1f}) 显示超买信号")
            elif latest_rsi < 30:
                print(f"\nRSI ({latest_rsi:.1f}) 显示超卖信号")
            else:
                print(f"\nRSI ({latest_rsi:.1f}) 处于正常区间")

    except Exception as e:
        print(f"✗ 技术指标计算失败: {e}")


def trading_time_check_example():
    """交易时间检查示例"""
    print("\n=== 交易时间检查示例 ===\n")

    symbols = ["CU2401.SHFE", "I2401.DCE", "TA2401.CZCE", "IF2401.CFFEX"]
    current_time = datetime.now()

    print(f"当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    for symbol in symbols:
        exchange = symbol.split('.')[-1]
        is_trading = is_trading_time(symbol, current_time)

        exchange_info = get_exchange_info(symbol)
        exchange_name = exchange_info.get('name', exchange)

        status = "交易中" if is_trading else "休市"
        print(f"{symbol} ({exchange_name}): {status}")


if __name__ == "__main__":
    # 运行所有示例
    try:
        advanced_analysis_example()
        technical_indicators_example()
        trading_time_check_example()
    except KeyboardInterrupt:
        print("\n\n示例执行被用户中断")
    except Exception as e:
        print(f"\n\n示例执行出错: {e}")