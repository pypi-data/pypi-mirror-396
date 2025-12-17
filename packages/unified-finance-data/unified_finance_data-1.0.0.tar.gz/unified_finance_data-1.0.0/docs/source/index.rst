Unified Finance Data
====================

一个统一的金融数据获取库，自动选择最优数据源获取ETF和股票的历史K线数据。

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples
   data_sources
   contributing

特性
----

* 🔄 **多数据源支持**: 集成同花顺、百度股市通、新浪财经等多个数据源
* 🎯 **智能选择**: 根据数据质量自动选择最佳数据源
* 🛡️ **故障容错**: 自动重试和降级机制，确保数据获取的可靠性
* 📊 **标准格式**: 统一的输出格式，包含完整的OHLCV数据
* 🚀 **简单易用**: 一行代码获取高质量金融数据
* 📈 **复权支持**: 支持前复权、后复权、不复权多种模式
* 🔧 **代理支持**: 支持SOCKS5代理配置

快速开始
--------

安装::

    pip install unified-finance-data

基本用法::

    from unified_finance_data import get_fund_k_history

    # 获取创业板ETF最近30天的数据
    df = get_fund_k_history('159915')
    print(df.head())

数据源
-----

本库按照数据质量自动选择数据源：

1. **同花顺** (优先级最高) - 专业金融数据，数据质量最高
2. **百度股市通-Playwright版本** (优先级中等) - 数据更新及时，功能完整，但需要浏览器环境
3. **百度股市通-API版本** (优先级较低) - 速度快，无需浏览器，但功能有限
4. **新浪财经** (优先级最低) - 接口稳定，轻量级实现

当高优先级数据源失败时，自动切换到备用数据源。

索引和表格
==========

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`