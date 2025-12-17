#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Finance Data - 统一金融数据获取库

一个统一的金融数据获取库，自动选择最优数据源获取ETF和股票的历史K线数据。

主要功能：
- 支持多个数据源（同花顺、百度、新浪）
- 自动选择最优数据源
- 故障容错和重试机制
- 标准化数据格式

作者: Quant Trading System
版本: 1.0.0
许可证: MIT
"""

from .core import get_fund_k_history, FuquanType, get_available_sources, test_data_sources
from .constants import PeriodType
from .exceptions import UnifiedFinanceDataError, DataSourceUnavailableError, InvalidParameterError

__version__ = "1.0.0"
__author__ = "Quant Trading System"
__email__ = "quant@example.com"
__license__ = "MIT"
__description__ = "统一的金融数据获取库，自动选择最优数据源"

__all__ = [
    # 核心功能
    "get_fund_k_history",
    "get_available_sources",
    "test_data_sources",

    # 类型定义
    "FuquanType",
    "PeriodType",

    # 异常类
    "UnifiedFinanceDataError",
    "DataSourceUnavailableError",
    "InvalidParameterError",
]

# 设置日志
import logging

# 创建库级别的logger
logger = logging.getLogger(__name__)

# 设置默认日志级别
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(name)s] %(levelname)s: %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)