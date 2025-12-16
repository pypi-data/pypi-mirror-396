# 更新日志

本项目的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义版本控制](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 初始版本发布

## [0.1.0] - 2024-12-13

### 新增
- 🎉 FinStock v0.1.0 初始版本发布
- ✨ 基础K线数据获取功能
- 🐼 pandas DataFrame自动转换
- 📊 支持多种时间间隔（1m, 5m, 15m, 1h, 1d, 1w, 1M）
- 🏢 支持中国主要期货交易所（SHFE, DCE, CZCE, CFFEX, INE）
- 🔒 使用Pydantic进行数据验证
- 🧪 完整的测试套件
- 📖 详细的文档和示例
- 🚀 GitHub Actions自动化CI/CD
- 📦 PyPI自动发布

### 支持的数据字段
- OHLCV基础数据（开高低收成交量）
- 成交额（turnover）
- 期货特有字段（持仓量、结算价、涨跌停价等）
- 交易日期和日盘开盘价

### API功能
- `/user/v1/kline` 统一查询接口
- 健康检查功能
- 上下文管理器支持
- 自定义超时和请求头

### 开发工具
- Black代码格式化
- Ruff代码检查
- MyPy类型检查
- pytest测试框架
- 代码覆盖率报告

---

## 版本说明

- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正