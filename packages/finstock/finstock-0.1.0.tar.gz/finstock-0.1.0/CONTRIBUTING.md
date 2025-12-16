# 贡献指南

感谢您对FinStock项目的关注！我们欢迎各种形式的贡献。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- uv (推荐) 或 pip
- Git

### 设置开发环境

1. **Fork并克隆项目**
   ```bash
   git clone https://github.com/YOUR_USERNAME/finstock.git
   cd finstock
   ```

2. **安装uv（如果尚未安装）**
   ```bash
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **创建虚拟环境并安装依赖**
   ```bash
   uv sync --dev
   ```

4. **验证安装**
   ```bash
   uv run pytest
   ```

## 📋 开发流程

### 1. 创建分支

```bash
# 从develop分支创建新的特性分支
git checkout develop
git checkout -b feature/your-feature-name

# 或者修复bug
git checkout -b fix/bug-description
```

### 2. 进行开发

- 遵循现有的代码风格
- 添加必要的测试
- 更新相关文档

### 3. 代码质量检查

```bash
# 代码格式化
uv run black .

# 代码检查
uv run ruff check .

# 类型检查
uv run mypy finstock/

# 运行测试
uv run pytest tests/ -v

# 生成覆盖率报告
uv run pytest tests/ --cov=finstock --cov-report=html
```

### 4. 提交更改

使用[约定式提交](https://www.conventionalcommits.org/zh-hans/v1.0.0/)格式：

```bash
# 功能添加
git commit -m "feat: 添加新的技术指标计算功能"

# 问题修复
git commit -m "fix: 修复DataFrame索引时区问题"

# 文档更新
git commit -m "docs: 更新API文档"

# 样式调整
git commit -m "style: 调整代码格式"

# 重构
git commit -m "refactor: 重构客户端请求逻辑"

# 测试
git commit -m "test: 添加数据验证测试"
```

### 5. 推送并创建Pull Request

```bash
git push origin feature/your-feature-name
```

然后在GitHub上创建Pull Request，目标分支为`develop`。

## 📝 代码规范

### Python代码风格

我们使用以下工具确保代码质量：

- **Black**: 代码格式化
- **Ruff**: 代码检查和格式化
- **MyPy**: 静态类型检查
- **isort**: 导入排序

### 命名规范

- **类名**: PascalCase（如 `FinStockClient`）
- **函数/变量名**: snake_case（如 `get_kline_data`）
- **常量**: UPPER_SNAKE_CASE（如 `DEFAULT_TIMEOUT`）
- **私有方法**: 以下划线开头（如 `_make_request`）

### 文档字符串

使用Google风格的文档字符串：

```python
def get_kline(
    self,
    symbol: str,
    interval: str,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
) -> KLineData:
    """获取K线数据

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
    """
```

## 🧪 测试指南

### 测试结构

```
tests/
├── test_client.py      # 客户端功能测试
├── test_models.py      # 数据模型测试
├── test_utils.py       # 工具函数测试
└── conftest.py         # pytest配置
```

### 编写测试

- 使用pytest框架
- 遵循Arrange-Act-Assert模式
- 使用mock进行外部依赖测试
- 确保高测试覆盖率

```python
class TestFinStockClient:
    def test_get_kline_success(self, mock_api_response):
        """测试成功获取K线数据"""
        # Arrange
        client = FinStockClient()

        # Act
        kline_data = client.get_kline("CU2401.SHFE", "1d")

        # Assert
        assert kline_data.data.symbol == "CU2401.SHFE"
        assert len(kline_data) > 0
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_client.py

# 运行测试并生成覆盖率报告
uv run pytest --cov=finstock --cov-report=html

# 运行性能测试
uv run pytest -m performance
```

## 📖 文档贡献

### 文档类型

- **README.md**: 项目概述和快速开始
- **API文档**: 详细的API参考
- **示例代码**: `examples/`目录下的使用示例
- **更新日志**: `CHANGELOG.md`

### 文档规范

- 使用清晰的标题结构
- 提供代码示例
- 保持中英文术语一致性
- 定期更新文档内容

## 🔧 发布流程

### 版本管理

项目遵循[语义版本控制](https://semver.org/lang/zh-CN/)：
- **主版本号**: 不兼容的API修改
- **次版本号**: 向下兼容的功能性新增
- **修订号**: 向下兼容的问题修正

### 发布步骤

1. **更新版本号**
   ```bash
   # 更新pyproject.toml中的版本号
   # 例如: 0.1.0 -> 0.2.0
   ```

2. **更新CHANGELOG.md**
   ```markdown
   ## [0.2.0] - 2024-XX-XX

   ### 新增
   - 新功能描述

   ### 修复
   - 问题修复描述
   ```

3. **创建发布标签**
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```

4. **自动发布**
   - GitHub Actions会自动构建并发布到PyPI
   - 自动创建GitHub Release

## 🤝 问题报告

使用以下模板报告问题：

### Bug报告

**描述**: 简要描述问题

**重现步骤**:
1. 执行命令A
2. 点击按钮B
3. 查看结果C

**期望行为**: 描述期望的正确行为

**实际行为**: 描述实际发生的情况

**环境信息**:
- Python版本:
- 操作系统:
- FinStock版本:

### 功能请求

**功能描述**: 清晰描述需要的功能

**使用场景**: 为什么需要这个功能

**预期实现**: 如何实现这个功能的建议

## 📞 联系方式

- **邮箱**: contact@finstock.com
- **GitHub Issues**: [项目Issues页面](https://github.com/finstock/finstock/issues)
- **讨论**: [GitHub Discussions](https://github.com/finstock/finstock/discussions)

## 🙏 致谢

感谢所有为FinStock项目做出贡献的开发者！

---

在贡献代码前，请确保已经阅读并理解本指南。如有任何疑问，随时通过上述方式联系我们。