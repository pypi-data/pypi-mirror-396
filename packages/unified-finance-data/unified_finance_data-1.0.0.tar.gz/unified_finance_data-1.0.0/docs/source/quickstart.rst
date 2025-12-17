快速开始
========

安装
----

通过pip安装::

    pip install unified-finance-data

或者从源码安装::

    git clone https://github.com/your-username/unified-finance-data.git
    cd unified-finance-data
    pip install -e .

基本用法
--------

获取数据
~~~~~~~~

最简单的使用方式：

.. code-block:: python

    from unified_finance_data import get_fund_k_history

    # 获取创业板ETF最近的数据（使用默认参数）
    df = get_fund_k_history('159915')
    print(df.head())

指定日期范围：

.. code-block:: python

    # 获取指定日期范围的数据
    df = get_fund_k_history('159915', '20240101', '20241201')
    print(f"获取到 {len(df)} 条数据")

复权类型
~~~~~~~~

支持三种复权类型：

.. code-block:: python

    from unified_finance_data import get_fund_k_history, FuquanType

    # 前复权（默认）
    df_front = get_fund_k_history('159915', fqt=FuquanType.FRONT)

    # 后复权
    df_back = get_fund_k_history('159915', fqt=FuquanType.BACK)

    # 不复权
    df_none = get_fund_k_history('159915', fqt=FuquanType.NONE)

调试模式
~~~~~~~~

启用调试信息：

.. code-block:: python

    # 显示详细的获取过程信息
    df = get_fund_k_history('159915', debug=True)

实用示例
--------

获取多只基金数据
~~~~~~~~~~~~~~~~

.. code-block:: python

    from unified_finance_data import get_fund_k_history

    funds = ['159915', '510050', '512100']  # 创业板ETF、上证50ETF、中证1000ETF
    all_data = {}

    for fund in funds:
        try:
            df = get_fund_k_history(fund, '20240101', '20241201')
            all_data[fund] = df
            print(f"{fund}: 获取到 {len(df)} 条数据")
        except Exception as e:
            print(f"{fund}: 获取失败 - {e}")

数据质量检查
~~~~~~~~~~~~

.. code-block:: python

    import pandas as pd
    from unified_finance_data import get_fund_k_history

    df = get_fund_k_history('159915', '20240101', '20241201')

    # 检查空值
    null_counts = df.isnull().sum()
    print("空值统计:")
    print(null_counts[null_counts > 0])

    # 检查价格异常
    price_issues = 0
    for col in ['开盘', '收盘', '最高', '最低']:
        issues = (df[col] <= 0).sum()
        if issues > 0:
            print(f"{col} 存在 {issues} 个非正值")
            price_issues += issues

    if price_issues == 0:
        print("✅ 价格数据检查通过")

获取可用数据源
~~~~~~~~~~~~~~

.. code-block:: python

    from unified_finance_data import get_available_sources

    sources = get_available_sources()
    print(f"当前可用数据源: {sources}")

测试数据源
~~~~~~~~~~

.. code-block:: python

    from unified_finance_data import test_data_sources

    # 测试数据源可用性
    success = test_data_sources('159915', debug=True)
    if success:
        print("✅ 数据源测试通过")
    else:
        print("❌ 数据源测试失败")

错误处理
--------

基本错误处理
~~~~~~~~~~~~

.. code-block:: python

    from unified_finance_data import get_fund_k_history
    from unified_finance_data.exceptions import UnifiedFinanceDataError

    try:
        df = get_fund_k_history('999999', '20240101', '20240101')  # 无效代码
    except UnifiedFinanceDataError as e:
        print(f"获取数据失败: {e}")
        # 实现备用逻辑或通知用户

特定异常处理
~~~~~~~~~~~~

.. code-block:: python

    from unified_finance_data.exceptions import (
        DataFetchError,
        InvalidParameterError,
        DataSourceUnavailableError
    )

    try:
        df = get_fund_k_history('159915', fqt=999)  # 无效复权类型
    except InvalidParameterError as e:
        print(f"参数错误: {e}")
    except DataFetchError as e:
        print(f"数据获取失败: {e}")
    except DataSourceUnavailableError as e:
        print(f"数据源不可用: {e}")

高级用法
--------

使用代理
~~~~~~~~

.. code-block:: python

    # 使用代理（如果有）
    df = get_fund_k_history(
        '159915',
        '20240101',
        '20241201',
        proxy='socks5://127.0.0.1:1080'
    )

批量处理
~~~~~~~~

.. code-block:: python

    import pandas as pd
    from unified_finance_data import get_fund_k_history
    import time

    def batch_fetch_funds(fund_codes, start_date, end_date, delay=1):
        """批量获取多只基金数据"""
        results = {}

        for i, fund_code in enumerate(fund_codes):
            try:
                print(f"正在获取 {fund_code} ({i+1}/{len(fund_codes)})...")
                df = get_fund_k_history(fund_code, start_date, end_date)
                results[fund_code] = df

                # 添加延迟避免请求过频繁
                if i < len(fund_codes) - 1:
                    time.sleep(delay)

            except Exception as e:
                print(f"{fund_code} 获取失败: {e}")
                results[fund_code] = None

        return results

    # 使用示例
    funds = ['159915', '510050', '512100', '159941']
    data = batch_fetch_funds(funds, '20240101', '20241201')

数据导出
~~~~~~~~

.. code-block:: python

    from unified_finance_data import get_fund_k_history

    df = get_fund_k_history('159915', '20240101', '20241201')

    # 导出到CSV
    df.to_csv('etf_159915_data.csv', index=False, encoding='utf-8-sig')

    # 导出到Excel
    df.to_excel('etf_159915_data.xlsx', index=False)

    # 导出到JSON
    df.to_json('etf_159915_data.json', orient='records', date_format='iso')

最佳实践
--------

1. **错误处理**: 始终使用try-except处理可能的异常
2. **数据验证**: 获取数据后进行基本的完整性检查
3. **缓存策略**: 对于重复请求，考虑实现本地缓存
4. **请求限制**: 避免过于频繁的请求，尊重数据源的限制
5. **日志记录**: 在生产环境中启用适当的日志记录

常见问题
--------

Q: 获取数据时返回空DataFrame？
A: 可能原因：基金代码无效、日期范围内无交易日、网络连接问题。建议检查基金代码和网络连接。

Q: 不同数据源返回的价格略有差异？
A: 这是正常现象，可能由于数据更新时间、复权方式或处理逻辑不同导致。建议在同一分析中使用同一数据源。

Q: 如何处理网络连接问题？
A: 可以配置代理、增加重试机制，或者在网络状况较好时获取数据。

Q: 支持哪些类型的金融产品？
A: 目前主要支持A股、ETF、指数等，具体支持情况取决于各个数据源。