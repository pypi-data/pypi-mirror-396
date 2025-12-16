#!/usr/bin/env python3
"""
FinStock基础使用示例

演示如何使用FinStock客户端获取期货K线数据。
"""

import pandas as pd
from datetime import datetime, timedelta
from finstock import FinStockClient


def basic_usage_example():
    """基础使用示例"""
    print("=== FinStock基础使用示例 ===\n")

    # 1. 创建客户端
    print("1. 创建FinStock客户端...")
    client = FinStockClient(base_url="http://localhost:8000")

    # 2. 检查API服务状态
    print("2. 检查API服务状态...")
    if client.health_check():
        print("✓ API服务正常")
    else:
        print("✗ API服务异常，请检查服务是否启动")
        return

    # 3. 获取K线数据
    print("\n3. 获取CU2401.SHFE日线数据...")
    try:
        # 获取最近10天的日线数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=10)

        kline_data = client.get_kline(
            symbol="CU2401.SHFE",
            interval="1d",
            start_datetime=start_time,
            end_datetime=end_time,
        )

        print(f"✓ 成功获取 {len(kline_data)} 条K线数据")
        print(f"合约代码: {kline_data.data.symbol}")
        print(f"时间间隔: {kline_data.data.interval}")

    except Exception as e:
        print(f"✗ 获取K线数据失败: {e}")
        return

    # 4. 转换为DataFrame
    print("\n4. 转换为DataFrame...")
    df = kline_data.to_dataframe()
    print(f"DataFrame形状: {df.shape}")
    print("\n前5行数据:")
    print(df.head())

    # 5. 显示DataFrame信息
    print("\n5. DataFrame信息:")
    print(f"数据列: {list(df.columns)}")
    print(f"索引类型: {type(df.index)}")
    print(f"数据范围: {df.index.min()} 到 {df.index.max()}")

    # 6. 基础分析
    print("\n6. 基础分析:")
    if 'close' in df.columns:
        print(f"最新收盘价: {df['close'].iloc[-1]:.2f}")
        print(f"期间最高价: {df['high'].max():.2f}")
        print(f"期间最低价: {df['low'].min():.2f}")
        print(f"期间平均成交量: {df['volume'].mean():.0f}")

    # 7. 关闭客户端
    print("\n7. 关闭客户端...")
    client.close()
    print("✓ 客户端已关闭")


def direct_dataframe_example():
    """直接获取DataFrame示例"""
    print("\n=== 直接获取DataFrame示例 ===\n")

    # 使用上下文管理器
    try:
        with FinStockClient() as client:
            print("使用上下文管理器创建客户端...")

            # 直接获取DataFrame
            df = client.get_kline_dataframe(
                symbol="CU2401.SHFE",
                interval="1d",
                start_datetime="2024-01-01",
                end_datetime="2024-01-10",
            )

            print(f"✓ 直接获取DataFrame，形状: {df.shape}")
            print(f"DataFrame属性 - 合约代码: {df.attrs.get('symbol')}")
            print(f"DataFrame属性 - 时间间隔: {df.attrs.get('interval')}")

            # 计算简单技术指标
            if len(df) >= 5:
                df['ma5'] = df['close'].rolling(window=5).mean()
                print("\n5日移动平均线:")
                print(df[['close', 'ma5']].tail())

    except Exception as e:
        print(f"✗ 示例执行失败: {e}")


if __name__ == "__main__":
    # 运行示例
    basic_usage_example()
    direct_dataframe_example()