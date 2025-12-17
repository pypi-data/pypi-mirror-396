#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试：统一金融数据获取功能测试
"""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unified_finance_data import (
    get_fund_k_history,
    get_available_sources,
    test_data_sources,
    FuquanType,
)


class TestBasicIntegration:
    """基础集成测试"""

    @pytest.mark.integration
    def test_get_available_sources(self):
        """测试获取可用数据源"""
        sources = get_available_sources()
        assert isinstance(sources, list)
        assert len(sources) > 0

        # 检查数据源名称
        valid_source_names = ['同花顺', '百度Playwright', '百度API', '新浪']
        for source in sources:
            assert source in valid_source_names

    @pytest.mark.integration
    @pytest.mark.slow
    def test_basic_data_fetch(self):
        """测试基本数据获取"""
        # 获取最近5天的数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')

        df = get_fund_k_history('159915', start_date, end_date, debug=False)

        # 检查返回结果
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

        # 检查必需的列
        required_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']
        for col in required_columns:
            assert col in df.columns

        # 检查数据格式
        assert len(df) > 0
        assert df['日期'].notna().all()
        assert (df['开盘'] > 0).all()
        assert (df['收盘'] > 0).all()
        assert (df['最高'] > 0).all()
        assert (df['最低'] > 0).all()
        assert (df['成交量'] >= 0).all()

    @pytest.mark.integration
    @pytest.mark.slow
    def test_different_fqt_types(self):
        """测试不同复权类型"""
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')

        fqt_types = [
            (FuquanType.NONE, "不复权"),
            (FuquanType.FRONT, "前复权"),
            (FuquanType.BACK, "后复权")
        ]

        results = {}

        for fqt, name in fqt_types:
            try:
                df = get_fund_k_history('159915', start_date, end_date, fqt=fqt, debug=False)

                if df is not None and not df.empty:
                    results[name] = {
                        'count': len(df),
                        'close_mean': df['收盘'].mean(),
                        'close_last': df['收盘'].iloc[-1] if not df.empty else None
                    }
                else:
                    pytest.skip(f"复权类型 {name} 未获取到数据")

            except Exception as e:
                pytest.fail(f"复权类型 {name} 获取数据失败: {e}")

        # 至少应该有一种复权类型成功
        assert len(results) > 0

    @pytest.mark.integration
    @pytest.mark.slow
    def test_multiple_funds(self):
        """测试多个基金数据获取"""
        test_funds = ['159915', '510050']  # 只测试两个基金以节省时间
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')

        results = {}

        for fund_code in test_funds:
            try:
                df = get_fund_k_history(fund_code, start_date, end_date, debug=False)

                if df is not None and not df.empty:
                    results[fund_code] = {
                        'count': len(df),
                        'has_data': True
                    }
                else:
                    results[fund_code] = {
                        'count': 0,
                        'has_data': False
                    }

            except Exception as e:
                # 记录失败但继续测试其他基金
                results[fund_code] = {
                    'count': 0,
                    'has_data': False,
                    'error': str(e)
                }

        # 至少应该有一个基金成功获取数据
        successful_funds = [k for k, v in results.items() if v.get('has_data', False)]
        assert len(successful_funds) > 0, f"所有基金都获取失败: {results}"

    @pytest.mark.integration
    @pytest.mark.slow
    def test_date_format_handling(self):
        """测试日期格式处理"""
        fund_code = '159915'

        # 测试不同的日期格式
        test_cases = [
            # (开始日期, 结束日期, 格式说明)
            ('20241201', '20241205', 'YYYYMMDD格式'),
            ('2024-12-01', '2024-12-05', 'YYYY-MM-DD格式'),
        ]

        for start_date, end_date, desc in test_cases:
            try:
                df = get_fund_k_history(fund_code, start_date, end_date, debug=False)

                if df is not None and not df.empty:
                    # 检查日期格式是否正确
                    assert df['日期'].str.match(r'\d{4}-\d{2}-\d{2}').all()
                else:
                    pytest.skip(f"日期格式 {desc} 未获取到数据")

            except Exception as e:
                pytest.fail(f"日期格式 {desc} 处理失败: {e}")

    @pytest.mark.integration
    def test_default_parameters(self):
        """测试默认参数"""
        try:
            # 只使用基金代码，其他参数使用默认值
            df = get_fund_k_history('159915', debug=False)

            if df is not None and not df.empty:
                assert isinstance(df, pd.DataFrame)
                assert len(df) > 0
            else:
                pytest.skip("默认参数未获取到数据")

        except Exception as e:
            pytest.fail(f"默认参数测试失败: {e}")


class TestErrorHandling:
    """错误处理集成测试"""

    @pytest.mark.integration
    def test_invalid_fund_code(self):
        """测试无效基金代码"""
        invalid_codes = ['999999', '000000', 'invalid']

        for code in invalid_codes:
            with pytest.raises(Exception):  # 应该抛出某种异常
                get_fund_k_history(code, '20241201', '20241201', debug=False)

    @pytest.mark.integration
    def test_invalid_fqt_parameter(self):
        """测试无效复权类型参数"""
        invalid_fqt_values = [999, -1, 100]

        for fqt in invalid_fqt_values:
            with pytest.raises(Exception):  # 应该抛出参数异常
                get_fund_k_history('159915', '20241201', '20241201', fqt=fqt, debug=False)

    @pytest.mark.integration
    def test_invalid_date_range(self):
        """测试无效日期范围"""
        # 开始日期晚于结束日期
        with pytest.raises(Exception):  # 应该抛出某种异常
            get_fund_k_history('159915', '20241231', '20241201', debug=False)


class TestTestFunctions:
    """测试函数集成测试"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_test_data_sources_function(self):
        """测试数据源测试函数"""
        try:
            result = test_data_sources('159915', debug=False)
            assert isinstance(result, bool)
            # 由于网络和数据源的不确定性，我们只检查函数是否正常执行
        except Exception as e:
            pytest.fail(f"test_data_sources函数执行失败: {e}")


class TestPerformance:
    """性能测试"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_response_time(self):
        """测试响应时间（简单的性能检查）"""
        import time

        fund_code = '159915'
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')

        start_time = time.time()

        try:
            df = get_fund_k_history(fund_code, start_date, end_date, debug=False)

            end_time = time.time()
            response_time = end_time - start_time

            if df is not None and not df.empty:
                # 响应时间应该在合理范围内（比如30秒）
                assert response_time < 30, f"响应时间过长: {response_time:.2f}秒"
            else:
                pytest.skip("性能测试未获取到数据")

        except Exception as e:
            pytest.fail(f"性能测试失败: {e}")


@pytest.mark.integration
class TestRealDataQuality:
    """真实数据质量测试"""

    @pytest.mark.slow
    def test_data_completeness(self):
        """测试数据完整性"""
        try:
            df = get_fund_k_history('159915', '20241101', '20241210', debug=False)

            if df is None or df.empty:
                pytest.skip("数据质量测试未获取到数据")
                return

            # 检查空值
            null_counts = df.isnull().sum()
            critical_columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量']

            for col in critical_columns:
                assert null_counts[col] == 0, f"关键列 {col} 存在空值"

            # 检查数据连续性
            df_sorted = df.sort_values('日期')
            date_gaps = pd.to_datetime(df_sorted['日期']).diff().dt.days
            # 允许有一些间隔（周末、节假日）
            assert (date_gaps.dropna() <= 10).all(), "日期间隔过大，可能存在数据缺失"

        except Exception as e:
            pytest.fail(f"数据完整性测试失败: {e}")

    @pytest.mark.slow
    def test_price_consistency(self):
        """测试价格数据一致性"""
        try:
            df = get_fund_k_history('159915', '20241101', '20241210', debug=False)

            if df is None or df.empty:
                pytest.skip("价格一致性测试未获取到数据")
                return

            # 检查价格逻辑关系
            assert (df['最高'] >= df['开盘']).all(), "最高价应该大于等于开盘价"
            assert (df['最高'] >= df['收盘']).all(), "最高价应该大于等于收盘价"
            assert (df['最低'] <= df['开盘']).all(), "最低价应该小于等于开盘价"
            assert (df['最低'] <= df['收盘']).all(), "最低价应该小于等于收盘价"
            assert (df['最高'] >= df['最低']).all(), "最高价应该大于等于最低价"

            # 检查价格合理性（无负值，无零值）
            price_columns = ['开盘', '收盘', '最高', '最低']
            for col in price_columns:
                assert (df[col] > 0).all(), f"价格列 {col} 存在非正值"

        except Exception as e:
            pytest.fail(f"价格一致性测试失败: {e}")


# 运行集成测试的快捷函数
def run_integration_tests():
    """运行所有集成测试的快捷函数"""
    import subprocess
    import sys

    # 运行集成测试
    result = subprocess.run([
        sys.executable, '-m', 'pytest',
        __file__,
        '-v',
        '-m', 'integration',
        '--tb=short'
    ], capture_output=True, text=True)

    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")

    return result.returncode == 0


if __name__ == "__main__":
    # 如果直接运行此文件，执行集成测试
    success = run_integration_tests()
    sys.exit(0 if success else 1)