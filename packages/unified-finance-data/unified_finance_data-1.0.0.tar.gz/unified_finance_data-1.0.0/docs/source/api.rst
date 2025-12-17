API 参考
========

核心模块
--------

.. automodule:: unified_finance_data
   :members:
   :undoc-members:
   :show-inheritance:

异常类
------

.. automodule:: unified_finance_data.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

数据类型
--------

复权类型
~~~~~~~~

.. data:: unified_finance_data.FuquanType.NONE
   :noindex:

   不复权 (值为 0)

.. data:: unified_finance_data.FuquanType.FRONT
   :noindex:

   前复权 (值为 1)

.. data:: unified_finance_data.FuquanType.BACK
   :noindex:

   后复权 (值为 2)

数据格式
--------

返回的DataFrame包含以下列：

===========  ============  ===================================
列名         数据类型       说明
===========  ============  ===================================
日期         str           交易日期，格式 YYYY-MM-DD
开盘         float         开盘价
收盘         float         收盘价
最高         float         最高价
最低         float         最低价
成交量       float/int     成交量
成交额       float/int     成交额
涨跌幅       float         涨跌幅 (%)
涨跌额       float         涨跌额
振幅         float         振幅 (%)
换手率       float         换手率 (%)
===========  ============  ===================================