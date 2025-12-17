#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫模块集合

提供多个数据源的K线数据获取功能。
"""

# 延迟导入以避免循环依赖
__all__ = [
    'ThsKLineCrawler',
    'get_sina_fund_k_history',
    'get_baidu_api_fund_k_history',
    'get_baidu_playwright_fund_k_history',
]


def get_ths_crawler():
    """获取同花顺爬虫实例"""
    from .ths_kline import ThsKLineCrawler
    return ThsKLineCrawler()


def get_sina_fund_k_history(*args, **kwargs):
    """获取新浪基金K线数据"""
    from .sina_kline import get_fund_k_history
    return get_fund_k_history(*args, **kwargs)


def get_baidu_api_fund_k_history(*args, **kwargs):
    """获取百度API基金K线数据"""
    from .baidu_api import get_fund_k_history
    return get_fund_k_history(*args, **kwargs)


def get_baidu_playwright_fund_k_history(*args, **kwargs):
    """获取百度Playwright基金K线数据"""
    from .baidu_playwright import get_fund_k_history
    return get_fund_k_history(*args, **kwargs)
