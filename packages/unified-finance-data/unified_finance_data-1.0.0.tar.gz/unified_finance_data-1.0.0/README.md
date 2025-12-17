# Unified Finance Data

[![PyPI version](https://badge.fury.io/py/unified-finance-data.svg)](https://badge.fury.io/py/unified-finance-data)
[![Python versions](https://img.shields.io/pypi/pyversions/unified-finance-data.svg)](https://pypi.org/project/unified-finance-data/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://readthedocs.org/projects/unified-finance-data/badge/?version=latest)](https://unified-finance-data.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/your-username/unified-finance-data/workflows/CI/badge.svg)](https://github.com/your-username/unified-finance-data/actions)

一个统一的金融数据获取库，自动选择最优数据源获取ETF和股票的历史K线数据。

## ✨ 特性

- 🔄 **多数据源支持**: 集成同花顺、百度股市通、新浪财经等多个数据源
- 🎯 **智能选择**: 根据数据质量自动选择最佳数据源
- 🛡️ **故障容错**: 自动重试和降级机制，确保数据获取的可靠性
- 📊 **标准格式**: 统一的输出格式，包含完整的OHLCV数据
- 🚀 **简单易用**: 一行代码获取高质量金融数据
- 📈 **复权支持**: 支持前复权、后复权、不复权多种模式
- 🔧 **代理支持**: 支持SOCKS5代理配置

## 📦 安装

```bash
pip install unified-finance-data
```

或者安装开发版本：

```bash
pip install git+https://github.com/your-username/unified-finance-data.git
```

## 🚀 快速开始

```python
from unified_finance_data import get_fund_k_history, FuquanType

# 获取创业板ETF最近30天的数据
df = get_fund_k_history('159915')

# 获取指定日期范围的数据
df = get_fund_k_history('159915', '20240101', '20241201')

# 使用后复权
df = get_fund_k_history('159915', '20240101', '20241201', fqt=FuquanType.BACK)

# 显示调试信息
df = get_fund_k_history('159915', debug=True)

print(df.head())
```

输出格式：

```
         日期     开盘     收盘     最高    最低        成交量          成交额     涨跌幅    涨跌额        振幅  换手率
0  2024-12-01  2.8900  2.9150  2.9200  2.8850  123456789.0  356789012.0  0.864887  0.0250  1.211765  0.052
1  2024-11-29  2.8750  2.8920  2.8950  2.8700   98765432.0  284567890.0  0.592857  0.0170  0.871739  0.042
```

## 📊 数据源优先级

本库按照数据质量自动选择数据源：

1. **同花顺** (优先级最高) - 专业金融数据，数据质量最高
2. **百度股市通-Playwright版本** (优先级中等) - 数据更新及时，功能完整，但需要浏览器环境
3. **百度股市通-API版本** (优先级较低) - 速度快，无需浏览器，但功能有限
4. **新浪财经** (优先级最低) - 接口稳定，轻量级实现

当高优先级数据源失败时，自动切换到备用数据源。

## 🔧 API 参考

### `get_fund_k_history()`

获取基金/股票的历史K线数据。

**参数：**
- `fund_code` (str): 基金/股票代码，如 '159915'
- `beg` (str, 可选): 开始日期，格式 'YYYYMMDD'，默认 '20200101'
- `end` (str, 可选): 结束日期，格式 'YYYYMMDD'，默认今天
- `fqt` (int, 可选): 复权类型，默认 `FuquanType.FRONT`
- `proxy` (str, 可选): 代理地址
- `debug` (bool, 可选): 是否显示调试信息

**返回：**
- `pd.DataFrame`: 包含完整K线数据的DataFrame

### 复权类型

```python
class FuquanType:
    NONE = 0   # 不复权
    FRONT = 1  # 前复权 (默认)
    BACK = 2   # 后复权
```

### 输出列说明

| 列名 | 说明 |
|------|------|
| 日期 | 交易日期 (YYYY-MM-DD) |
| 开盘 | 开盘价 |
| 收盘 | 收盘价 |
| 最高 | 最高价 |
| 最低 | 最低价 |
| 成交量 | 成交量 |
| 成交额 | 成交额 |
| 涨跌幅 | 涨跌幅 (%) |
| 涨跌额 | 涨跌额 |
| 振幅 | 振幅 (%) |
| 换手率 | 换手率 (%) |

## 🧪 高级用法

### 获取可用数据源

```python
from unified_finance_data import get_available_sources

sources = get_available_sources()
print(f"可用数据源: {sources}")
# 可能输出: ['同花顺', '百度Playwright', '百度API', '新浪']
```

### 测试数据源

```python
from unified_finance_data import test_data_sources

# 测试默认配置
success = test_data_sources()

# 测试指定基金和日期范围
success = test_data_sources('510050', '20241101', '20241201')
```

### 自定义错误处理

```python
from unified_finance_data import get_fund_k_history, FuquanType

try:
    df = get_fund_k_history('159915', debug=True)
except RuntimeError as e:
    print(f"数据获取失败: {e}")
    # 实现备用逻辑
```

## 🔧 开发

### 安装开发环境

```bash
# 克隆仓库
git clone https://github.com/your-username/unified-finance-data.git
cd unified-finance-data

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest unit/

# 运行集成测试
pytest tests/

# 生成覆盖率报告
pytest --cov=unified_finance_data --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
black src/ unit/ tests/

# 排序导入
isort src/ unit/ tests/

# 类型检查
mypy src/unified_finance_data/
```

## 📋 支持

- 支持A股、ETF、指数等金融产品
- 支持多种时间周期（日线、周线、月线）
- 自动处理节假日和停牌数据
- 智能数据质量检查和清洗

## ⚠️ 免责声明

本库仅供学习和研究使用，不构成投资建议。使用本库获取的金融数据进行投资决策所产生的一切风险由用户自行承担。请遵守相关法律法规，尊重金融数据提供商的使用条款。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [同花顺](https://www.10jqka.com.cn/) - 提供专业金融数据
- [百度股市通](https://gushitong.baidu.com/) - 提供实时股市数据
- [新浪财经](https://finance.sina.com.cn/) - 提供稳定金融数据接口

## 📞 联系方式

- 项目主页: https://github.com/your-username/unified-finance-data
- 文档: https://unified-finance-data.readthedocs.io/
- 问题反馈: https://github.com/your-username/unified-finance-data/issues