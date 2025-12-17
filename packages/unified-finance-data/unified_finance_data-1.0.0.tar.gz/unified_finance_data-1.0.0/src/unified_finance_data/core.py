#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Finance Data 核心模块

提供统一的数据获取接口，自动选择最优数据源。

遵循Golang设计哲学：
- 简单性优于复杂性
- 接口应该小而专注
- 组合优于继承
- 显式优于隐式
- 减少抽象层次
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import warnings
from typing import Optional, List, Dict, Any

from .exceptions import (
    UnifiedFinanceDataError,
    DataSourceUnavailableError,
    InvalidParameterError,
    DataFetchError,
    DataQualityError,
    NetworkError,
    ParsingError,
)

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


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


class DataSourceManager:
    """数据源管理器 - 简单、专注的设计"""

    def __init__(self, debug: bool = False):
        self.sources = []
        self.debug = debug
        self._init_sources()

    def _init_sources(self):
        """按照数据质量优先级初始化数据源"""
        # 导入数据源模块
        self._ths_crawler = None
        self._baidu_playwright_get_data = None
        self._baidu_api_get_data = None
        self._sina_get_data = None

        # 1. 同花顺 (数据质量最高)
        try:
            from .crawlers.ths_kline import ThsKLineCrawler
            self._ths_crawler = ThsKLineCrawler()
            self.sources.append({
                'name': '同花顺',
                'priority': 1,
                'function': self._get_ths_data,
                'available': True
            })
            if self.debug:
                logger.info("✓ 同花顺数据源初始化成功")
        except ImportError as e:
            if self.debug:
                logger.warning(f"✗ 同花顺数据源不可用: {e}")

        # 2. 百度股市通-Playwright版本 (数据更新及时，功能完整)
        try:
            from .crawlers.baidu_playwright import get_fund_k_history as baidu_playwright_get_data
            self._baidu_playwright_get_data = baidu_playwright_get_data
            self.sources.append({
                'name': '百度Playwright',
                'priority': 2,
                'function': self._get_baidu_playwright_data,
                'available': True
            })
            if self.debug:
                logger.info("✓ 百度Playwright数据源初始化成功")
        except ImportError as e:
            if self.debug:
                logger.warning(f"✗ 百度Playwright数据源不可用: {e}")

        # 3. 百度股市通-API版本 (速度快，但功能有限)
        try:
            from .crawlers.baidu_api import get_fund_k_history as baidu_api_get_data
            self._baidu_api_get_data = baidu_api_get_data
            self.sources.append({
                'name': '百度API',
                'priority': 3,
                'function': self._get_baidu_api_data,
                'available': True
            })
            if self.debug:
                logger.info("✓ 百度API数据源初始化成功")
        except ImportError as e:
            if self.debug:
                logger.warning(f"✗ 百度API数据源不可用: {e}")

        # 4. 新浪财经 (稳定性好)
        try:
            from .crawlers.sina_kline import get_fund_k_history as sina_get_data
            self._sina_get_data = sina_get_data
            self.sources.append({
                'name': '新浪',
                'priority': 4,
                'function': self._get_sina_data,
                'available': True
            })
            if self.debug:
                logger.info("✓ 新浪数据源初始化成功")
        except ImportError as e:
            if self.debug:
                logger.warning(f"✗ 新浪数据源不可用: {e}")

        if not self.sources:
            raise DataSourceUnavailableError("所有数据源都不可用，请检查依赖安装")

        # 按优先级排序
        self.sources.sort(key=lambda x: x['priority'])

    def _get_ths_data(self, fund_code: str, beg: str, end: str, fqt: int, proxy: Optional[str]) -> Optional[pd.DataFrame]:
        """获取同花顺数据"""
        try:
            if self.debug:
                logger.info(f"🔄 尝试从同花顺获取 {fund_code} 数据...")

            # 同花顺参数格式
            data = self._ths_crawler.get_fund_k_history(
                code=fund_code,
                beg=beg,
                end=end
            )

            if data is not None and not data.empty:
                if self.debug:
                    logger.info(f"✅ 同花顺数据获取成功: {len(data)} 条记录")
                return self._standardize_data(data, '同花顺')
            else:
                if self.debug:
                    logger.warning(f"❌ 同花顺返回空数据")
                return None
        except Exception as e:
            if self.debug:
                logger.error(f"❌ 同花顺数据获取失败: {e}")
            return None

    def _get_baidu_playwright_data(self, fund_code: str, beg: str, end: str, fqt: int, proxy: Optional[str]) -> Optional[pd.DataFrame]:
        """获取百度Playwright数据"""
        try:
            if self.debug:
                logger.info(f"🔄 尝试从百度Playwright获取 {fund_code} 数据...")

            # 百度Playwright参数格式
            data = self._baidu_playwright_get_data(
                fund_code=fund_code,
                beg=beg,
                end=end,
                headless=True,
                debug=self.debug
            )

            if data is not None and not data.empty:
                if self.debug:
                    logger.info(f"✅ 百度Playwright数据获取成功: {len(data)} 条记录")
                return self._standardize_data(data, '百度Playwright')
            else:
                if self.debug:
                    logger.warning(f"❌ 百度Playwright返回空数据")
                return None
        except Exception as e:
            if self.debug:
                logger.error(f"❌ 百度Playwright数据获取失败: {e}")
            return None

    def _get_baidu_api_data(self, fund_code: str, beg: str, end: str, fqt: int, proxy: Optional[str]) -> Optional[pd.DataFrame]:
        """获取百度API数据"""
        try:
            if self.debug:
                logger.info(f"🔄 尝试从百度API获取 {fund_code} 数据...")

            # 百度API参数格式 - 注意参数不同
            data = self._baidu_api_get_data(
                fund_code=fund_code,
                beg=beg,
                end=end,
                debug=self.debug
            )

            if data is not None and not data.empty:
                if self.debug:
                    logger.info(f"✅ 百度API数据获取成功: {len(data)} 条记录")
                return self._standardize_data(data, '百度API')
            else:
                if self.debug:
                    logger.warning(f"❌ 百度API返回空数据")
                return None
        except Exception as e:
            if self.debug:
                logger.error(f"❌ 百度API数据获取失败: {e}")
            return None

    def _get_sina_data(self, fund_code: str, beg: str, end: str, fqt: int, proxy: Optional[str]) -> Optional[pd.DataFrame]:
        """获取新浪数据"""
        try:
            if self.debug:
                logger.info(f"🔄 尝试从新浪获取 {fund_code} 数据...")

            # 新浪参数格式
            data = self._sina_get_data(
                fund_code=fund_code,
                beg=beg,
                end=end,
                debug=self.debug
            )

            if data is not None and not data.empty:
                if self.debug:
                    logger.info(f"✅ 新浪数据获取成功: {len(data)} 条记录")
                return self._standardize_data(data, '新浪')
            else:
                if self.debug:
                    logger.warning(f"❌ 新浪返回空数据")
                return None
        except Exception as e:
            if self.debug:
                logger.error(f"❌ 新浪数据获取失败: {e}")
            return None

    def _standardize_data(self, df: pd.DataFrame, source_name: str) -> pd.DataFrame:
        """标准化数据格式"""
        # 确保必要的列存在
        required_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']

        # 创建新的DataFrame
        result_df = pd.DataFrame()

        # 复制原始数据
        for col in required_columns:
            if col in df.columns:
                result_df[col] = df[col]
            else:
                # 百度API和新浪的成交额为空是正常的
                if source_name not in ['新浪', '百度API'] or col not in ['成交额']:
                    logger.warning(f"⚠️  {source_name}数据缺少列 '{col}'，用0填充")
                result_df[col] = 0

        # 添加派生列
        if '涨跌幅' not in df.columns:
            result_df['涨跌幅'] = ((result_df['收盘'] - result_df['开盘']) / result_df['开盘'] * 100).round(2)
        else:
            result_df['涨跌幅'] = df['涨跌幅']

        if '涨跌额' not in df.columns:
            result_df['涨跌额'] = (result_df['收盘'] - result_df['开盘']).round(3)
        else:
            result_df['涨跌额'] = df['涨跌额']

        if '振幅' not in df.columns:
            if len(result_df) > 0 and result_df['开盘'].iloc[0] > 0:
                result_df['振幅'] = ((result_df['最高'] - result_df['最低']) / result_df['开盘'].iloc[0] * 100).round(2)
            else:
                result_df['振幅'] = 0.0
        else:
            result_df['振幅'] = df['振幅']

        if '换手率' not in df.columns:
            result_df['换手率'] = 0.0
        else:
            result_df['换手率'] = df['换手率']

        # 确保日期格式正确
        result_df['日期'] = pd.to_datetime(result_df['日期']).dt.strftime('%Y-%m-%d')

        # 按日期排序
        result_df = result_df.sort_values('日期').reset_index(drop=True)

        # 添加数据源标识列
        result_df['数据源'] = source_name

        # 数据质量检查
        if self.debug:
            self._validate_data(result_df, source_name)

        return result_df

    def _validate_data(self, df: pd.DataFrame, source_name: str):
        """验证数据质量"""
        if df.empty:
            return

        issues = []

        # 检查价格数据
        for col in ['开盘', '收盘', '最高', '最低']:
            if col in df.columns:
                invalid_count = (df[col] <= 0).sum()
                if invalid_count > 0:
                    issues.append(f"{col}<=0: {invalid_count}处")

        # 检查成交量
        if '成交量' in df.columns:
            invalid_volume = (df['成交量'] < 0).sum()
            if invalid_volume > 0:
                issues.append(f"成交量<0: {invalid_volume}处")

        # 检查价格跳跃
        if '收盘' in df.columns and len(df) > 1:
            price_change = df['收盘'].pct_change().abs()
            jumps = (price_change > 0.2).sum()
            if jumps > 0:
                issues.append(f"价格跳跃>20%: {jumps}处")

        if issues:
            logger.warning(f"⚠️  {source_name}数据质量警告: {', '.join(issues)}")

    def get_data(self, fund_code: str, beg: str, end: str, fqt: int, proxy: Optional[str]) -> pd.DataFrame:
        """按优先级获取数据"""
        # 验证参数
        if not FuquanType.validate(fqt):
            raise InvalidParameterError("fqt", str(fqt), "必须是 FuquanType.NONE, FuquanType.FRONT 或 FuquanType.BACK")

        if self.debug:
            logger.info(f"🎯 开始获取基金 {fund_code} 数据，时间范围: {beg} ~ {end}")
            logger.info(f"📊 可用数据源: {[s['name'] for s in self.sources]} (按质量排序)")

        last_error = None

        # 按优先级尝试各个数据源
        for source in self.sources:
            try:
                data = source['function'](fund_code, beg, end, fqt, proxy)

                if data is not None and not data.empty:
                    # 验证数据质量
                    if self._is_data_acceptable(data):
                        if self.debug:
                            logger.info(f"🎉 成功从 {source['name']} 获取数据")
                        return data
                    else:
                        if self.debug:
                            logger.warning(f"⚠️  {source['name']} 数据质量不佳，尝试下一个数据源")
                        continue
                else:
                    if self.debug:
                        logger.warning(f"⚠️  {source['name']} 返回空数据，尝试下一个数据源")

            except Exception as e:
                last_error = e
                if self.debug:
                    logger.error(f"❌ {source['name']} 获取失败: {e}")
                continue

        # 所有数据源都失败
        error_msg = f"所有数据源都失败了"
        if last_error:
            error_msg += f"。最后错误: {last_error}"

        raise DataFetchError(fund_code, last_error)

    def _is_data_acceptable(self, df: pd.DataFrame) -> bool:
        """检查数据质量是否可接受"""
        if df.empty:
            return False

        # 基本质量检查
        if len(df) < 5:  # 数据太少
            return False

        # 检查必要的列
        required_cols = ['日期', '开盘', '收盘', '最高', '最低', '成交量']
        for col in required_cols:
            if col not in df.columns:
                return False

        # 检查价格数据合理性
        price_cols = ['开盘', '收盘', '最高', '最低']
        for col in price_cols:
            if col in df.columns:
                invalid_count = (df[col] <= 0).sum()
                if invalid_count > len(df) * 0.1:  # 超过10%的数据无效
                    return False

        return True

    def get_available_sources(self) -> List[str]:
        """获取可用数据源列表"""
        return [source['name'] for source in self.sources]


# 全局数据源管理器实例
_data_manager: Optional[DataSourceManager] = None


def get_fund_k_history(fund_code: str, beg: str = '20200101', end: Optional[str] = None,
                       fqt: int = FuquanType.FRONT, proxy: Optional[str] = None,
                       debug: Optional[bool] = None) -> pd.DataFrame:
    """
    统一的基金K线历史数据获取函数

    按照数据质量优先级自动尝试不同数据源：
    1. 同花顺 (数据质量最高)
    2. 百度股市通 (数据更新及时)
    3. 新浪财经 (稳定性好)

    Args:
        fund_code: 基金代码，如 '159915'
        beg: 开始日期，格式YYYYMMDD，默认'20200101'
        end: 结束日期，格式YYYYMMDD，默认今天
        fqt: 复权类型，FuquanType.FRONT(1)前复权，FuquanType.BACK(2)后复权，FuquanType.NONE(0)不复权
        proxy: 代理地址（可选）
        debug: 是否显示调试信息

    Returns:
        pd.DataFrame: 标准化的K线数据

    Raises:
        DataFetchError: 当所有数据源都失败时
        InvalidParameterError: 当参数无效时

    Examples:
        # 基本用法
        df = get_fund_k_history('159915', '20240101', '20241201')

        # 使用后复权
        df = get_fund_k_history('159915', '20240101', '20241201', fqt=FuquanType.BACK)

        # 显示调试信息
        df = get_fund_k_history('159915', debug=True)
    """
    global _data_manager

    # 初始化数据源管理器
    if _data_manager is None:
        try:
            _data_manager = DataSourceManager(debug=debug if debug is not None else False)
        except DataSourceUnavailableError as e:
            raise DataFetchError(fund_code, e)

    # 处理默认值
    if end is None:
        end = datetime.now().strftime('%Y%m%d')

    if debug is None:
        debug = False

    # 格式化日期
    if len(beg) == 8:  # YYYYMMDD格式
        beg_formatted = f"{beg[:4]}-{beg[4:6]}-{beg[6:8]}"
    else:  # YYYY-MM-DD格式
        beg_formatted = beg
        beg = beg.replace('-', '')

    if len(end) == 8:  # YYYYMMDD格式
        end_formatted = f"{end[:4]}-{end[4:6]}-{end[6:8]}"
    else:  # YYYY-MM-DD格式
        end_formatted = end
        end = end.replace('-', '')

    # 获取数据
    try:
        data = _data_manager.get_data(fund_code, beg, end, fqt, proxy)
        return data
    except Exception as e:
        if isinstance(e, UnifiedFinanceDataError):
            raise
        else:
            raise DataFetchError(fund_code, e)


def get_available_sources() -> List[str]:
    """获取可用的数据源列表"""
    global _data_manager

    if _data_manager is None:
        try:
            _data_manager = DataSourceManager()
        except DataSourceUnavailableError:
            return []

    return _data_manager.get_available_sources()


def test_data_sources(fund_code: str = '159915', beg: str = None, end: str = None, debug: bool = True) -> bool:
    """测试所有数据源的可用性"""
    logger.info("🧪 测试数据源可用性...")
    logger.info("=" * 60)

    # 设置默认日期
    if end is None:
        end = datetime.now().strftime('%Y%m%d')
    if beg is None:
        beg = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

    available_sources = get_available_sources()
    logger.info(f"📊 可用数据源: {available_sources}")

    # 测试统一接口
    try:
        logger.info(f"\n🔄 测试统一接口获取 {fund_code} 数据...")
        df = get_fund_k_history(fund_code, beg, end, debug=debug)
        logger.info(f"✅ 统一接口测试成功: 获取到 {len(df)} 条数据")
        logger.info(f"📅 数据范围: {df['日期'].min()} ~ {df['日期'].max()}")
        return True
    except Exception as e:
        logger.error(f"❌ 统一接口测试失败: {e}")
        return False