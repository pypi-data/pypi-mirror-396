#!/usr/bin/env python3
"""
FinStock演示脚本

这是一个简单的演示脚本，展示如何使用FinStock库获取期货K线数据。
"""

import sys
from datetime import datetime, timedelta
from finstock import FinStockClient


def main():
    """主演示函数"""
    print("FinStock - 中国期货数据获取库演示")
    print("=" * 50)

    # 创建客户端
    print("\n正在连接到API服务器...")
    client = FinStockClient(base_url="http://localhost:8000")

    try:
        # 健康检查
        if client.health_check():
            print("[成功] API服务连接成功")
        else:
            print("[失败] API服务不可用，请检查服务器是否启动")
            return

        # 获取OpenAPI规范
        print("\n获取API规范信息...")
        try:
            spec = client.get_openapi_spec()
            print(f"API标题: {spec['info']['title']}")
            print(f"API版本: {spec['info']['version']}")

            # 显示可用的接口
            paths = list(spec['paths'].keys())
            kline_paths = [p for p in paths if 'kline' in p]
            print(f"K线接口: {kline_paths}")
        except Exception as e:
            print(f"[警告] 获取API规范失败: {e}")

        # 演示获取K线数据
        print("\n尝试获取K线数据...")
        print("合约: CU2401.SHFE (沪铜2401)")
        print("周期: 1d (日线)")

        try:
            # 尝试获取最近10天的数据
            end_time = datetime.now()
            start_time = end_time - timedelta(days=10)

            df = client.get_kline_dataframe(
                symbol="CU2401.SHFE",
                interval="1d",
                start_datetime=start_time,
                end_datetime=end_time
            )

            if len(df) > 0:
                print(f"[成功] 获取到 {len(df)} 条K线数据")
                print(f"数据形状: {df.shape}")
                print(f"数据时间范围: {df.index.min()} 到 {df.index.max()}")

                # 显示最新数据
                latest = df.iloc[-1]
                print(f"\n最新数据 ({df.index[-1].strftime('%Y-%m-%d')}):")
                print(f"   开盘: {latest['open']:.2f}")
                print(f"   收盘: {latest['close']:.2f}")
                print(f"   最高: {latest['high']:.2f}")
                print(f"   最低: {latest['low']:.2f}")
                print(f"   成交量: {latest['volume']:.0f}")

                if 'open_interest' in df.columns and not df['open_interest'].isna().all():
                    print(f"   持仓量: {latest['open_interest']:.0f}")
            else:
                print("[信息] 暂无数据（这很正常，演示环境可能没有历史数据）")

        except ValueError as e:
            if "未找到合约" in str(e):
                print("[信息] 该合约暂无数据（这是正常的，演示环境数据有限）")
            else:
                print(f"[错误] 数据获取失败: {e}")
        except Exception as e:
            print(f"[错误] 未知错误: {e}")

        # 显示支持的交易所信息
        print(f"\n支持的期货交易所:")
        from finstock.utils import get_exchange_info

        exchanges = ["SHFE", "DCE", "CZCE", "CFFEX", "INE"]
        for exchange in exchanges:
            symbol = f"TEST2401.{exchange}"
            info = get_exchange_info(symbol)
            if info:
                print(f"   {exchange}: {info.get('name', '未知交易所')}")

        print(f"\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"提示: 这是期货交易时间吗？")

    except Exception as e:
        print(f"[错误] 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 关闭客户端
        client.close()
        print("\n演示结束，客户端已关闭")


if __name__ == "__main__":
    main()