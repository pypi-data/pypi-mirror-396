#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：复权类型测试
"""

import pytest
from unified_finance_data.core import FuquanType
from unified_finance_data.exceptions import InvalidParameterError


class TestFuquanType:
    """FuquanType类的单元测试"""

    def test_constants(self):
        """测试常量定义"""
        assert FuquanType.NONE == 0
        assert FuquanType.FRONT == 1
        assert FuquanType.BACK == 2

    def test_get_name(self):
        """测试获取复权类型名称"""
        assert FuquanType.get_name(FuquanType.NONE) == "不复权"
        assert FuquanType.get_name(FuquanType.FRONT) == "前复权"
        assert FuquanType.get_name(FuquanType.BACK) == "后复权"
        assert FuquanType.get_name(999) == "未知"

    def test_validate(self):
        """测试复权类型验证"""
        assert FuquanType.validate(FuquanType.NONE) is True
        assert FuquanType.validate(FuquanType.FRONT) is True
        assert FuquanType.validate(FuquanType.BACK) is True
        assert FuquanType.validate(999) is False
        assert FuquanType.validate(-1) is False

    def test_all_values(self):
        """测试所有可能的值"""
        valid_values = [FuquanType.NONE, FuquanType.FRONT, FuquanType.BACK]
        for value in valid_values:
            assert FuquanType.validate(value) is True
            name = FuquanType.get_name(value)
            assert name != "未知"

    def test_invalid_values(self):
        """测试无效值"""
        invalid_values = [-1, 3, 999, None, "string"]
        for value in invalid_values:
            if value is not None and isinstance(value, int):
                assert FuquanType.validate(value) is False