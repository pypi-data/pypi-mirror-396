#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享常量定义

包含复权类型、K线周期类型等所有爬虫模块共用的常量。
"""


class FuquanType:
    """复权类型常量"""
    NONE = 0      # 不复权
    FRONT = 1     # 前复权
    BACK = 2      # 后复权

    @classmethod
    def get_name(cls, fqt: int) -> str:
        """获取复权类型的中文名称"""
        mapping = {
            cls.NONE: "不复权",
            cls.FRONT: "前复权",
            cls.BACK: "后复权"
        }
        return mapping.get(fqt, "未知")

    @classmethod
    def validate(cls, fqt: int) -> bool:
        """验证复权类型是否有效"""
        return fqt in [cls.NONE, cls.FRONT, cls.BACK]


class PeriodType:
    """K线周期类型常量"""
    DAILY = 101     # 日线
    WEEKLY = 102    # 周线
    MONTHLY = 103   # 月线

    @classmethod
    def get_name(cls, period: int) -> str:
        """获取周期类型的中文名称"""
        mapping = {
            cls.DAILY: "日线",
            cls.WEEKLY: "周线",
            cls.MONTHLY: "月线"
        }
        return mapping.get(period, "未知")

    @classmethod
    def validate(cls, period: int) -> bool:
        """验证周期类型是否有效"""
        return period in [cls.DAILY, cls.WEEKLY, cls.MONTHLY]

    @classmethod
    def to_baidu_ktype(cls, period: int) -> int:
        """转换为百度API的ktype参数"""
        mapping = {
            cls.DAILY: 1,
            cls.WEEKLY: 2,
            cls.MONTHLY: 3
        }
        return mapping.get(period, 1)

    @classmethod
    def to_baidu_type(cls, period: int) -> str:
        """转换为百度K线类型字符串（兼容旧接口）"""
        mapping = {
            cls.DAILY: "日K",
            cls.WEEKLY: "周K",
            cls.MONTHLY: "月K"
        }
        return mapping.get(period, "日K")
