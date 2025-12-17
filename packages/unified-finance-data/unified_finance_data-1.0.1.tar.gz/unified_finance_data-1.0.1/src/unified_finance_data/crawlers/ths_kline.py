"""
同花顺K线数据获取API
基于同花顺网站(10jqka.com)的K线数据接口实现
支持ETF、股票等多种证券的K线数据获取
"""

import logging
import pandas as pd
import requests
import re
import json
from datetime import datetime
from typing import Optional, Union
from enum import IntEnum

logger = logging.getLogger(__name__)


class ThsFuquanType(IntEnum):
    """同花顺复权类型"""
    NONE = 1       # 不复权
    BACK = 2       # 后复权
    # 注：同花顺API没有明确的前复权参数，ETF通常不需要复权


class ThsPeriodType(IntEnum):
    """同花顺K线周期类型"""
    DAILY = 1      # 日K
    WEEKLY = 2     # 周K
    MONTHLY = 3    # 月K


class ThsKLineCrawler:
    """同花顺K线数据爬虫"""

    def __init__(self):
        self.base_url = "https://d.10jqka.com.cn/v6/line/hs_{code}/{type}/{scope}.js"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://stockpage.10jqka.com.cn/',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

    def _get_type_code(self, period: ThsPeriodType, fuquan: ThsFuquanType) -> str:
        """获取同花顺API的type参数"""
        # 日K线
        if period == ThsPeriodType.DAILY:
            if fuquan == ThsFuquanType.BACK:
                return "02"  # 后复权
            else:
                return "01"  # 不复权
        # 周K线
        elif period == ThsPeriodType.WEEKLY:
            return "11"
        # 月K线
        elif period == ThsPeriodType.MONTHLY:
            return "21"
        else:
            raise ValueError(f"不支持的K线周期: {period}")

    def _parse_jsonp_response(self, response_text: str, code: str, type_code: str) -> dict:
        """解析JSONP响应"""
        # 同花顺返回的JSONP格式：quotebridge_v6_line_hs_159915_01_last({...}) 或 quotebridge_v6_line_hs_159915_01_all({...})
        # 使用更宽松的匹配模式
        patterns = [
            rf'quotebridge_v6_line_hs_{code}_{type_code}_last\((.+)\)',
            rf'quotebridge_v6_line_hs_{code}_{type_code}_all\((.+)\)'
        ]

        for pattern in patterns:
            match = re.search(pattern, response_text)
            if match:
                try:
                    data_str = match.group(1)
                    return json.loads(data_str)
                except json.JSONDecodeError as e:
                    continue

        raise ValueError(f"无法解析同花顺API响应: {response_text[:100]}...")

    def _parse_all_kline_data(self, data: dict) -> pd.DataFrame:
        """解析全部历史K线数据(all.js格式)"""
        price_str = data.get('price', '')
        dates_str = data.get('dates', '')

        if not price_str or not dates_str:
            return pd.DataFrame()

        try:
            # 解析价格数据，每4个字段为一条记录：开盘、最高、最低、收盘
            price_fields = price_str.split(',')
            dates_fields = dates_str.split(',')

            if len(price_fields) % 4 != 0:
                logger.warning(f"all.js数据格式异常，价格字段数: {len(price_fields)}")
                return pd.DataFrame()

            record_count = len(price_fields) // 4
            if len(dates_fields) != record_count:
                logger.warning(f"日期和价格数据不匹配：日期{len(dates_fields)}个，价格记录{record_count}个")
                return pd.DataFrame()

            price_factor = data.get('priceFactor', 1000)
            start_date = data.get('start', '20111209')
            sort_year = data.get('sortYear', [])

            # 构建日期到年份的映射
            date_to_year = {}
            if sort_year:
                current_idx = 0
                for year_info in sort_year:
                    year, count = year_info
                    for j in range(count):
                        if current_idx < len(dates_fields):
                            date_to_year[dates_fields[current_idx]] = year
                            current_idx += 1

            records = []
            for i in range(record_count):
                try:
                    # 解析日期（格式：1209 -> 2011-12-09）
                    date_str = dates_fields[i].strip()
                    if len(date_str) == 4:
                        # 格式：1209 -> 月日
                        month = int(date_str[:2])
                        day = int(date_str[2:])

                        # 使用sortYear信息获取正确的年份
                        year = date_to_year.get(date_str, int(start_date[:4]))
                        date = f"{year:04d}-{month:02d}-{day:02d}"
                    else:
                        # 其他格式暂不处理
                        date = "2000-01-01"

                    # 解析OHLC数据（按价格因子缩放）
                    base_idx = i * 4
                    open_price = float(price_fields[base_idx]) / price_factor if price_fields[base_idx] else 0
                    high_price = float(price_fields[base_idx + 1]) / price_factor if price_fields[base_idx + 1] else 0
                    low_price = float(price_fields[base_idx + 2]) / price_factor if price_fields[base_idx + 2] else 0
                    close_price = float(price_fields[base_idx + 3]) / price_factor if price_fields[base_idx + 3] else 0

                    record_data = {
                        '日期': date,
                        '开盘': open_price,
                        '最高': high_price,
                        '最低': low_price,
                        '收盘': close_price,
                        '成交量': 0,  # all.js格式中没有成交量信息
                        '成交额': 0,  # all.js格式中没有成交额信息
                        '换手率': 0.0,
                    }

                    # 计算派生指标
                    if record_data['开盘'] > 0:
                        record_data['振幅'] = (record_data['最高'] - record_data['最低']) / record_data['开盘'] * 100
                        record_data['涨跌幅'] = (record_data['收盘'] - record_data['开盘']) / record_data['开盘'] * 100
                        record_data['涨跌额'] = record_data['收盘'] - record_data['开盘']
                    else:
                        record_data['振幅'] = 0.0
                        record_data['涨跌幅'] = 0.0
                        record_data['涨跌额'] = 0.0

                    records.append(record_data)

                except (ValueError, IndexError) as e:
                    logger.debug(f"解析all.js记录失败: {i}, 错误: {e}")
                    continue

            df = pd.DataFrame(records)
            if not df.empty:
                # 按日期排序
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期').reset_index(drop=True)
                df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')

            return df

        except Exception as e:
            logger.error(f"解析all.js数据失败: {e}")
            return pd.DataFrame()

    def _parse_kline_data(self, data_str: str) -> pd.DataFrame:
        """解析K线数据字符串"""
        if not data_str:
            return pd.DataFrame()

        # 数据格式：日期,开盘,最高,最低,收盘,成交量,成交额,换手率,,,0
        records = []
        for record in data_str.split(';'):
            if not record.strip():
                continue

            fields = record.split(',')
            if len(fields) < 8:
                continue

            try:
                date_str = fields[0]
                # 转换日期格式：20250519 -> 2025-05-19
                date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')

                record_data = {
                    '日期': date,
                    '开盘': float(fields[1]),
                    '最高': float(fields[2]),
                    '最低': float(fields[3]),
                    '收盘': float(fields[4]),
                    '成交量': int(float(fields[5])),
                    '成交额': float(fields[6]),
                    '换手率': float(fields[7]) if fields[7] else 0.0,
                }

                # 计算派生指标
                if record_data['开盘'] > 0:
                    record_data['振幅'] = (record_data['最高'] - record_data['最低']) / record_data['开盘'] * 100
                    record_data['涨跌幅'] = (record_data['收盘'] - record_data['开盘']) / record_data['开盘'] * 100
                    record_data['涨跌额'] = record_data['收盘'] - record_data['开盘']
                else:
                    record_data['振幅'] = 0.0
                    record_data['涨跌幅'] = 0.0
                    record_data['涨跌额'] = 0.0

                records.append(record_data)

            except (ValueError, IndexError) as e:
                logger.debug(f"解析记录失败: {record}, 错误: {e}")
                continue

        df = pd.DataFrame(records)
        if not df.empty:
            # 按日期排序
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.sort_values('日期').reset_index(drop=True)
            df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')

        return df

    def get_k_history(self,
                     code: str,
                     beg: str = None,
                     end: str = None,
                     period: ThsPeriodType = ThsPeriodType.DAILY,
                     fuquan: ThsFuquanType = ThsFuquanType.BACK,
                     adjust_type: str = "last") -> pd.DataFrame:
        """
        获取K线历史数据

        参数:
            code: 证券代码，如 "159915" 或 "600519"
            beg: 开始日期，格式：20250101
            end: 结束日期，格式：20251231
            period: K线周期，默认日线
            fuquan: 复权类型，默认不复权
            adjust_type: "last"获取最近数据，"all"获取全部历史数据

        返回:
            pandas DataFrame，包含K线数据
        """
        try:
            # 获取type参数
            type_code = self._get_type_code(period, fuquan)

            # 构建URL
            url = self.base_url.format(
                code=code,
                type=type_code,
                scope=adjust_type
            )

            # 发送请求
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # 解析响应
            data = self._parse_jsonp_response(response.text, code, type_code)

            # 解析K线数据 - all.js和last.js的数据字段不同
            if adjust_type == "all":
                # all.js格式使用整个数据对象
                df = self._parse_all_kline_data(data)
            else:
                # last.js格式使用"data"字段
                df = self._parse_kline_data(data.get('data', ''))

            # 日期过滤
            if not df.empty and (beg or end):
                df['日期'] = pd.to_datetime(df['日期'])

                if beg:
                    beg_date = datetime.strptime(beg, '%Y%m%d')
                    df = df[df['日期'] >= beg_date]

                if end:
                    end_date = datetime.strptime(end, '%Y%m%d')
                    df = df[df['日期'] <= end_date]

                # 转换回字符串格式
                df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
                df = df.reset_index(drop=True)

            # 确保列的顺序
            if not df.empty:
                columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
                df = df[columns]

            return df

        except Exception as e:
            logger.error(f"获取K线数据失败，代码: {code}, 错误: {e}")
            return pd.DataFrame()

    def get_fund_k_history(self,
                          code: str,
                          beg: str = None,
                          end: str = None,
                          period: ThsPeriodType = ThsPeriodType.DAILY) -> pd.DataFrame:
        """
        获取基金K线历史数据（ETF专用，默认不复权）

        参数:
            code: 基金代码，如 "159915"
            beg: 开始日期，格式：20250101
            end: 结束日期，格式：20251231
            period: K线周期，默认日线

        返回:
            pandas DataFrame，包含K线数据
        """
        # ETF基金通常不需要复权
        return self.get_k_history(
            code=code,
            beg=beg,
            end=end,
            period=period,
            fuquan=ThsFuquanType.NONE,
            adjust_type="last"
        )


def demo_usage():
    """使用示例"""
    crawler = ThsKLineCrawler()

    print("=== 获取ETF数据(159915) ===")
    etf_data = crawler.get_fund_k_history("159915")
    print(f"获取到 {len(etf_data)} 条ETF数据")
    if not etf_data.empty:
        print(etf_data.head())
        print(f"数据列: {list(etf_data.columns)}")

    print("=== 获取ETF数据(162411) ===")
    etf_data = crawler.get_fund_k_history("162411")
    print(f"获取到 {len(etf_data)} 条ETF数据")
    if not etf_data.empty:
        print(etf_data.head())
        print(f"数据列: {list(etf_data.columns)}")

    print("\n=== 获取股票后复权数据(600519贵州茅台) ===")
    stock_data = crawler.get_k_history(
        code="600519",
        period=ThsPeriodType.DAILY,
        fuquan=ThsFuquanType.BACK
    )
    print(f"获取到 {len(stock_data)} 条股票后复权数据")
    if not stock_data.empty:
        print(stock_data.head())
        print(f"最新收盘价: {stock_data['收盘'].iloc[-1]:.2f}")

    print("\n=== 获取周K线数据 ===")
    weekly_data = crawler.get_k_history(
        code="159915",
        period=ThsPeriodType.WEEKLY
    )
    print(f"获取到 {len(weekly_data)} 条周K线数据")
    if not weekly_data.empty:
        print(weekly_data.head())

    print("\n=== 获取全部历史数据 ===")
    all_data = crawler.get_k_history(
        code="159915",
        adjust_type="all"
    )
    print(f"获取到 {len(all_data)} 条全部历史数据")
    if not all_data.empty:
        print(f"数据范围: {all_data['日期'].iloc[0]} 至 {all_data['日期'].iloc[-1]}")


if __name__ == "__main__":
    demo_usage()