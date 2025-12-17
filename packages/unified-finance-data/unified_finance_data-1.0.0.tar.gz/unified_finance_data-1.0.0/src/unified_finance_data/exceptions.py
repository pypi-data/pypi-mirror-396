#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Finance Data 异常类定义

定义了库中使用的所有异常类型，提供清晰的错误信息。
"""


class UnifiedFinanceDataError(Exception):
    """统一金融数据库基础异常类"""

    def __init__(self, message: str, error_code: str = None):
        """
        初始化异常

        Args:
            message: 错误信息
            error_code: 错误代码（可选）
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class DataSourceUnavailableError(UnifiedFinanceDataError):
    """数据源不可用异常"""

    def __init__(self, source_name: str, reason: str = None):
        """
        初始化数据源不可用异常

        Args:
            source_name: 数据源名称
            reason: 不可用的原因
        """
        message = f"数据源 '{source_name}' 不可用"
        if reason:
            message += f": {reason}"
        super().__init__(message, "DATA_SOURCE_UNAVAILABLE")
        self.source_name = source_name
        self.reason = reason


class InvalidParameterError(UnifiedFinanceDataError):
    """无效参数异常"""

    def __init__(self, parameter_name: str, parameter_value: str = None, reason: str = None):
        """
        初始化无效参数异常

        Args:
            parameter_name: 参数名称
            parameter_value: 参数值
            reason: 无效的原因
        """
        message = f"参数 '{parameter_name}' 无效"
        if parameter_value:
            message += f" (值: {parameter_value})"
        if reason:
            message += f": {reason}"
        super().__init__(message, "INVALID_PARAMETER")
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        self.reason = reason


class DataFetchError(UnifiedFinanceDataError):
    """数据获取失败异常"""

    def __init__(self, fund_code: str, last_error: Exception = None):
        """
        初始化数据获取失败异常

        Args:
            fund_code: 基金/股票代码
            last_error: 最后的错误信息
        """
        message = f"获取基金/股票 '{fund_code}' 数据失败"
        if last_error:
            message += f": {last_error}"
        super().__init__(message, "DATA_FETCH_ERROR")
        self.fund_code = fund_code
        self.last_error = last_error


class DataQualityError(UnifiedFinanceDataError):
    """数据质量异常"""

    def __init__(self, issues: list):
        """
        初始化数据质量异常

        Args:
            issues: 数据质量问题列表
        """
        message = f"数据质量问题: {', '.join(issues)}"
        super().__init__(message, "DATA_QUALITY_ERROR")
        self.issues = issues


class NetworkError(UnifiedFinanceDataError):
    """网络错误异常"""

    def __init__(self, url: str = None, status_code: int = None, reason: str = None):
        """
        初始化网络错误异常

        Args:
            url: 请求URL
            status_code: HTTP状态码
            reason: 错误原因
        """
        message = "网络请求失败"
        if url:
            message += f" (URL: {url})"
        if status_code:
            message += f" (状态码: {status_code})"
        if reason:
            message += f": {reason}"
        super().__init__(message, "NETWORK_ERROR")
        self.url = url
        self.status_code = status_code
        self.reason = reason


class ParsingError(UnifiedFinanceDataError):
    """数据解析错误异常"""

    def __init__(self, source_name: str, data_type: str = None, reason: str = None):
        """
        初始化数据解析错误异常

        Args:
            source_name: 数据源名称
            data_type: 数据类型（如JSON、HTML等）
            reason: 解析失败的原因
        """
        message = f"解析 '{source_name}' 数据失败"
        if data_type:
            message += f" (类型: {data_type})"
        if reason:
            message += f": {reason}"
        super().__init__(message, "PARSING_ERROR")
        self.source_name = source_name
        self.data_type = data_type
        self.reason = reason