#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：异常类测试
"""

import pytest
from unified_finance_data.exceptions import (
    UnifiedFinanceDataError,
    DataSourceUnavailableError,
    InvalidParameterError,
    DataFetchError,
    DataQualityError,
    NetworkError,
    ParsingError,
)


class TestUnifiedFinanceDataError:
    """基础异常类测试"""

    def test_basic_error(self):
        """测试基本异常"""
        error = UnifiedFinanceDataError("测试错误")
        assert str(error) == "测试错误"
        assert error.message == "测试错误"
        assert error.error_code is None

    def test_error_with_code(self):
        """测试带错误代码的异常"""
        error = UnifiedFinanceDataError("测试错误", "TEST_CODE")
        assert str(error) == "[TEST_CODE] 测试错误"
        assert error.message == "测试错误"
        assert error.error_code == "TEST_CODE"


class TestDataSourceUnavailableError:
    """数据源不可用异常测试"""

    def test_basic_unavailable_error(self):
        """测试基本数据源不可用异常"""
        error = DataSourceUnavailableError("测试数据源")
        assert str(error) == "[DATA_SOURCE_UNAVAILABLE] 数据源 '测试数据源' 不可用"
        assert error.source_name == "测试数据源"
        assert error.reason is None

    def test_unavailable_error_with_reason(self):
        """测试带原因的数据源不可用异常"""
        error = DataSourceUnavailableError("测试数据源", "网络连接失败")
        assert str(error) == "[DATA_SOURCE_UNAVAILABLE] 数据源 '测试数据源' 不可用: 网络连接失败"
        assert error.source_name == "测试数据源"
        assert error.reason == "网络连接失败"


class TestInvalidParameterError:
    """无效参数异常测试"""

    def test_basic_invalid_parameter(self):
        """测试基本无效参数异常"""
        error = InvalidParameterError("test_param")
        assert str(error) == "[INVALID_PARAMETER] 参数 'test_param' 无效"
        assert error.parameter_name == "test_param"
        assert error.parameter_value is None
        assert error.reason is None

    def test_invalid_parameter_with_value(self):
        """测试带值的无效参数异常"""
        error = InvalidParameterError("test_param", "invalid_value")
        assert str(error) == "[INVALID_PARAMETER] 参数 'test_param' 无效 (值: invalid_value)"
        assert error.parameter_name == "test_param"
        assert error.parameter_value == "invalid_value"
        assert error.reason is None

    def test_invalid_parameter_with_reason(self):
        """测试带原因的无效参数异常"""
        error = InvalidParameterError("test_param", "invalid_value", "参数类型错误")
        expected = "[INVALID_PARAMETER] 参数 'test_param' 无效 (值: invalid_value): 参数类型错误"
        assert str(error) == expected
        assert error.parameter_name == "test_param"
        assert error.parameter_value == "invalid_value"
        assert error.reason == "参数类型错误"


class TestDataFetchError:
    """数据获取失败异常测试"""

    def test_basic_fetch_error(self):
        """测试基本数据获取失败异常"""
        error = DataFetchError("159915")
        assert str(error) == "[DATA_FETCH_ERROR] 获取基金/股票 '159915' 数据失败"
        assert error.fund_code == "159915"
        assert error.last_error is None

    def test_fetch_error_with_last_error(self):
        """测试带最后错误的数据获取失败异常"""
        original_error = Exception("原始错误")
        error = DataFetchError("159915", original_error)
        assert str(error) == "[DATA_FETCH_ERROR] 获取基金/股票 '159915' 数据失败: 原始错误"
        assert error.fund_code == "159915"
        assert error.last_error == original_error


class TestDataQualityError:
    """数据质量异常测试"""

    def test_data_quality_error(self):
        """测试数据质量异常"""
        issues = ["价格异常", "成交量异常", "日期缺失"]
        error = DataQualityError(issues)
        expected = "[DATA_QUALITY_ERROR] 数据质量问题: 价格异常, 成交量异常, 日期缺失"
        assert str(error) == expected
        assert error.issues == issues

    def test_empty_issues(self):
        """测试空问题列表"""
        issues = []
        error = DataQualityError(issues)
        expected = "[DATA_QUALITY_ERROR] 数据质量问题: "
        assert str(error) == expected
        assert error.issues == []


class TestNetworkError:
    """网络错误异常测试"""

    def test_basic_network_error(self):
        """测试基本网络错误异常"""
        error = NetworkError()
        assert str(error) == "[NETWORK_ERROR] 网络请求失败"
        assert error.url is None
        assert error.status_code is None
        assert error.reason is None

    def test_network_error_with_url(self):
        """测试带URL的网络错误异常"""
        error = NetworkError(url="https://example.com")
        expected = "[NETWORK_ERROR] 网络请求失败 (URL: https://example.com)"
        assert str(error) == expected
        assert error.url == "https://example.com"
        assert error.status_code is None
        assert error.reason is None

    def test_network_error_with_status_code(self):
        """测试带状态码的网络错误异常"""
        error = NetworkError(status_code=404)
        expected = "[NETWORK_ERROR] 网络请求失败 (状态码: 404)"
        assert str(error) == expected
        assert error.url is None
        assert error.status_code == 404
        assert error.reason is None

    def test_network_error_with_reason(self):
        """测试带原因的网络错误异常"""
        error = NetworkError(reason="连接超时")
        expected = "[NETWORK_ERROR] 网络请求失败: 连接超时"
        assert str(error) == expected
        assert error.url is None
        assert error.status_code is None
        assert error.reason == "连接超时"

    def test_network_error_with_all(self):
        """测试包含所有信息的网络错误异常"""
        error = NetworkError(
            url="https://example.com",
            status_code=500,
            reason="服务器内部错误"
        )
        expected = "[NETWORK_ERROR] 网络请求失败 (URL: https://example.com) (状态码: 500): 服务器内部错误"
        assert str(error) == expected
        assert error.url == "https://example.com"
        assert error.status_code == 500
        assert error.reason == "服务器内部错误"


class TestParsingError:
    """数据解析错误异常测试"""

    def test_basic_parsing_error(self):
        """测试基本解析错误异常"""
        error = ParsingError("测试数据源")
        expected = "[PARSING_ERROR] 解析 '测试数据源' 数据失败"
        assert str(error) == expected
        assert error.source_name == "测试数据源"
        assert error.data_type is None
        assert error.reason is None

    def test_parsing_error_with_data_type(self):
        """测试带数据类型的解析错误异常"""
        error = ParsingError("测试数据源", "JSON")
        expected = "[PARSING_ERROR] 解析 '测试数据源' 数据失败 (类型: JSON)"
        assert str(error) == expected
        assert error.source_name == "测试数据源"
        assert error.data_type == "JSON"
        assert error.reason is None

    def test_parsing_error_with_reason(self):
        """测试带原因的解析错误异常"""
        error = ParsingError("测试数据源", reason="格式错误")
        expected = "[PARSING_ERROR] 解析 '测试数据源' 数据失败: 格式错误"
        assert str(error) == expected
        assert error.source_name == "测试数据源"
        assert error.data_type is None
        assert error.reason == "格式错误"

    def test_parsing_error_with_all(self):
        """测试包含所有信息的解析错误异常"""
        error = ParsingError("测试数据源", "HTML", "缺少必需标签")
        expected = "[PARSING_ERROR] 解析 '测试数据源' 数据失败 (类型: HTML): 缺少必需标签"
        assert str(error) == expected
        assert error.source_name == "测试数据源"
        assert error.data_type == "HTML"
        assert error.reason == "缺少必需标签"


class TestExceptionHierarchy:
    """异常层次结构测试"""

    def test_inheritance(self):
        """测试异常继承关系"""
        assert issubclass(DataSourceUnavailableError, UnifiedFinanceDataError)
        assert issubclass(InvalidParameterError, UnifiedFinanceDataError)
        assert issubclass(DataFetchError, UnifiedFinanceDataError)
        assert issubclass(DataQualityError, UnifiedFinanceDataError)
        assert issubclass(NetworkError, UnifiedFinanceDataError)
        assert issubclass(ParsingError, UnifiedFinanceDataError)

    def test_exception_catching(self):
        """测试异常捕获"""
        # 基础异常应该能捕获所有子异常
        try:
            raise DataSourceUnavailableError("测试")
        except UnifiedFinanceDataError as e:
            assert isinstance(e, DataSourceUnavailableError)

        try:
            raise InvalidParameterError("test")
        except UnifiedFinanceDataError as e:
            assert isinstance(e, InvalidParameterError)

        try:
            raise DataFetchError("159915")
        except UnifiedFinanceDataError as e:
            assert isinstance(e, DataFetchError)