"""
百度股市通ETF数据获取 - API版本
直接调用百度API，无需浏览器，速度快，稳定性高
接口与 baidu_etf_playwright.py 保持一致
"""

import logging
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..constants import FuquanType, PeriodType

# 尝试导入pandas
PANDAS_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger(__name__)


class BaiduETFApiSpider:
    """
    百度股市通ETF数据API爬虫
    直接调用API，无需浏览器
    """

    BASE_URL = "https://finance.pae.baidu.com/vapi/v1/getquotation"
    PAGE_URL = "https://gushitong.baidu.com/etf/ab-{code}"

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Referer': 'https://gushitong.baidu.com/',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://gushitong.baidu.com',
        'Connection': 'keep-alive',
    }

    def __init__(self, timeout: int = 30):
        """
        初始化API爬虫

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        logger.info("百度API爬虫初始化成功")

    def get_kline_data(self, code: str, kline_type: str = "日K", wait_time: int = 5) -> Optional[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            code: ETF代码，如 "159941"
            kline_type: K线类型，可选 "日K", "周K", "月K"
            wait_time: 等待时间（API模式下忽略此参数）

        Returns:
            K线数据字典
        """
        # 转换K线类型
        ktype_mapping = {
            "日K": "day",
            "周K": "week",
            "月K": "month"
        }
        ktype = ktype_mapping.get(kline_type, "day")

        params = {
            "srcid": "5353",
            "all": "1",
            "code": code,
            "query": code,
            "financeType": "etf",
            "group": "quotation_kline_ab",
            "stock_type": "ab",
            "ktype": ktype,
            "finClientType": "pc"
        }

        try:
            logger.debug(f"正在请求: {self.BASE_URL}")
            logger.debug(f"参数: {params}")

            resp = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            result = data.get('Result', {})
            new_market_data = result.get('newMarketData', {})

            if not new_market_data:
                logger.debug("未找到 newMarketData")
                return None

            keys = new_market_data.get('keys', [])
            raw_data = new_market_data.get('marketData', '')

            if not raw_data:
                logger.debug("marketData 为空")
                return None

            kline_list = self._parse_kline_data(raw_data, keys)

            return {
                "code": code,
                "kline_type": kline_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": kline_list
            }

        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            return None

    def _parse_kline_data(self, raw_data: str, keys: List[str]) -> List[Dict]:
        """解析K线数据"""
        kline_list = []
        lines = raw_data.strip().split(';')

        for line in lines:
            if not line.strip():
                continue

            parts = line.split(',')
            if len(parts) < 7:
                continue

            kline = {}
            for i, key in enumerate(keys):
                if i >= len(parts):
                    break

                value = parts[i]
                if key == 'timestamp':
                    kline[key] = int(value) if value and value != '--' else 0
                elif key == 'time':
                    kline[key] = value
                elif value and value != '--':
                    try:
                        kline[key] = float(value.replace('+', ''))
                    except ValueError:
                        kline[key] = value
                else:
                    kline[key] = None

            if kline.get('time'):
                kline_list.append(kline)

        return kline_list

    def get_etf_data(self, code: str, wait_time: int = 5) -> Optional[Dict[str, Any]]:
        """
        获取ETF完整数据（兼容接口）

        Args:
            code: ETF代码
            wait_time: 等待时间（API模式下忽略）

        Returns:
            ETF数据字典
        """
        return self.get_kline_data(code, kline_type="日K", wait_time=wait_time)

    def close(self):
        """关闭会话"""
        self.session.close()
        logger.info("API会话已关闭")


# ============================================================================
# 简化接口函数 - 与 baidu_etf_playwright.py 保持一致的API风格
# ============================================================================

# 全局爬虫实例（惰性初始化）
_global_spider = None


def _get_spider(headless: bool = True) -> BaiduETFApiSpider:
    """获取或创建全局爬虫实例"""
    global _global_spider
    if _global_spider is None:
        _global_spider = BaiduETFApiSpider()
    return _global_spider


def close_spider():
    """关闭全局爬虫实例"""
    global _global_spider
    if _global_spider is not None:
        _global_spider.close()
        _global_spider = None


def _filter_by_date(kline_list: List[Dict], beg: str, end: str) -> List[Dict]:
    """按日期范围过滤K线数据"""
    if not kline_list:
        return []

    try:
        start_date = datetime.strptime(beg, '%Y%m%d').date()
        end_date = datetime.strptime(end, '%Y%m%d').date()
    except ValueError:
        return kline_list

    filtered = []
    for item in kline_list:
        try:
            date_str = item.get('time', '')
            if not date_str:
                continue
            item_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if start_date <= item_date <= end_date:
                filtered.append(item)
        except (ValueError, TypeError):
            continue

    return filtered


def _convert_to_standard_format(kline_list: List[Dict]):
    """
    将百度K线数据转换为标准格式

    Returns:
        pandas DataFrame 或 字典列表
    """
    if not kline_list:
        if PANDAS_AVAILABLE:
            return pd.DataFrame()
        return []

    # 转换为标准格式
    result = []
    for item in kline_list:
        row = {
            '日期': item.get('time', ''),
            '开盘': float(item.get('open', 0) or 0),
            '收盘': float(item.get('close', 0) or 0),
            '最高': float(item.get('high', 0) or 0),
            '最低': float(item.get('low', 0) or 0),
            '成交量': int(float(item.get('volume', 0) or 0)),
            '成交额': float(item.get('amount', 0) or 0),
            '振幅': float(item.get('range', 0) or 0),
            '涨跌幅': float(item.get('ratio', 0) or 0),
            '涨跌额': 0.0,  # 百度数据中没有此字段
            '换手率': float(item.get('turnoverratio', 0) or 0) if item.get('turnoverratio') and item.get('turnoverratio') != '--' else 0.0,
        }
        result.append(row)

    if PANDAS_AVAILABLE:
        df = pd.DataFrame(result)
        if not df.empty:
            # 转换日期列
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce').dt.date
            df = df.sort_values(by='日期', ascending=True)
            df = df.reset_index(drop=True)
        return df

    return result


def get_k_history(code: str, beg: str = '20200101', end: str = None,
                  klt: int = PeriodType.DAILY, fqt: int = FuquanType.FRONT,
                  headless: bool = True, debug: bool = None):
    """
    获取股票历史K线数据（百度股市通API）

    Parameters:
    ----------
    code : str
        股票代码，6位数字，如 '600519'（贵州茅台）

    beg : str
        开始日期，格式：YYYYMMDD，默认为 '20200101'

    end : str
        结束日期，格式：YYYYMMDD，默认为当前日期

    klt : int
        K线周期类型，使用 PeriodType 常量：
        - PeriodType.DAILY (101): 日线
        - PeriodType.WEEKLY (102): 周线
        - PeriodType.MONTHLY (103): 月线

    fqt : int
        复权方式，使用 FuquanType 常量（百度数据暂不支持复权，此参数保留兼容）

    headless : bool
        是否使用无头模式（API模式下忽略此参数）

    debug : bool
        是否启用调试模式

    Returns:
    -------
    pd.DataFrame 或 list
        标准化的K线数据，包含列：日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率
    """
    if end is None:
        end = datetime.now().strftime('%Y%m%d')

    logger.debug(f"开始获取股票 {code} 的K线数据")
    logger.debug(f"时间范围: {beg} 到 {end}")
    logger.debug(f"K线类型: {PeriodType.get_name(klt)}")

    # 验证参数
    if not PeriodType.validate(klt):
        raise ValueError(f"无效的K线类型: {klt}")
    if not FuquanType.validate(fqt):
        raise ValueError(f"无效的复权类型: {fqt}")

    try:
        spider = _get_spider(headless=headless)
        kline_type = PeriodType.to_baidu_type(klt)

        result = spider.get_kline_data(code, kline_type=kline_type, wait_time=5)

        if result and result.get('data'):
            kline_list = result['data']
            # 按日期过滤
            kline_list = _filter_by_date(kline_list, beg, end)
            # 转换为标准格式
            return _convert_to_standard_format(kline_list)

        if PANDAS_AVAILABLE:
            return pd.DataFrame()
        return []

    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")
        if PANDAS_AVAILABLE:
            return pd.DataFrame()
        return []


def get_fund_k_history(fund_code: str, beg: str = '20200101', end: str = None,
                       klt: int = PeriodType.DAILY, fqt: int = FuquanType.FRONT,
                       headless: bool = True, debug: bool = None):
    """
    获取ETF/基金历史K线数据（百度股市通API）

    Parameters:
    ----------
    fund_code : str
        基金代码，如 '159941'（纳指ETF）、'510050'（上证50ETF）

    beg : str
        开始日期，格式：YYYYMMDD，默认为 '20200101'

    end : str
        结束日期，格式：YYYYMMDD，默认为当前日期

    klt : int
        K线周期类型，使用 PeriodType 常量：
        - PeriodType.DAILY (101): 日线
        - PeriodType.WEEKLY (102): 周线
        - PeriodType.MONTHLY (103): 月线

    fqt : int
        复权方式，使用 FuquanType 常量（百度数据暂不支持复权，此参数保留兼容）

    headless : bool
        是否使用无头模式（API模式下忽略此参数）

    debug : bool
        是否启用调试模式

    Returns:
    -------
    pd.DataFrame 或 list
        标准化的K线数据，包含列：日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率
    """
    # ETF基金数据获取逻辑与股票相同
    return get_k_history(fund_code, beg, end, klt, fqt, headless, debug)


def save_to_csv(data, filename: str):
    """
    将K线数据保存为CSV文件

    Parameters:
    ----------
    data : pd.DataFrame 或 list
        K线数据

    filename : str
        保存的文件名
    """
    if PANDAS_AVAILABLE:
        if isinstance(data, pd.DataFrame):
            if data.empty:
                logger.warning("没有数据可保存")
                return
            data.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f'数据已保存到 {filename}')
            return

    # 字典列表格式
    if not data:
        logger.warning("没有数据可保存")
        return

    import csv
    headers = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            line = [row.get(h, '') for h in headers]
            writer.writerow(line)

    logger.info(f'数据已保存到 {filename}')


def export_to_csv(kline_data: List[Dict], filename: str):
    """导出K线数据到CSV文件（兼容旧接口）"""
    if not kline_data:
        return

    import csv

    # 定义要导出的字段
    fields = ['time', 'open', 'close', 'high', 'low', 'volume', 'amount', 'ratio', 'preClose']
    headers = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '涨跌幅', '昨收']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for item in kline_data:
            row = []
            for field in fields:
                value = item.get(field, '')
                if value is None:
                    value = ''
                row.append(value)
            writer.writerow(row)


def main():
    """主函数：演示如何使用"""
    print("=" * 70)
    print("百度股市通ETF数据获取 - API版本")
    print("=" * 70)

    # 测试ETF列表
    test_etfs = [
        {"code": "159941", "name": "纳指ETF"},
    ]

    for etf in test_etfs:
        print(f"\n【正在获取 {etf['name']} ({etf['code']}) 日线数据】")
        print("-" * 70)

        # 获取日线K线数据
        df = get_k_history(etf['code'], beg='20240101')

        if PANDAS_AVAILABLE and isinstance(df, pd.DataFrame):
            if not df.empty:
                print(f"[OK] 获取到 {len(df)} 条K线数据")

                # 显示最近10条数据
                print("\n【最近10条日线数据】")
                print("-" * 85)
                print(f"{'日期':<12} {'开盘':>8} {'收盘':>8} {'最高':>8} {'最低':>8} {'成交量':>14} {'涨跌幅':>8}")
                print("-" * 85)

                for _, row in df.tail(10).iterrows():
                    print(f"{str(row['日期']):<12} {row['开盘']:>8.3f} {row['收盘']:>8.3f} {row['最高']:>8.3f} {row['最低']:>8.3f} {row['成交量']:>14,.0f} {row['涨跌幅']:>7.2f}%")

                # 导出到CSV
                csv_file = f"etf_{etf['code']}_daily.csv"
                save_to_csv(df, csv_file)
                print(f"\n[OK] 数据已导出到 {csv_file}")
            else:
                print("[FAIL] 未能获取K线数据")
        elif isinstance(df, list) and df:
            print(f"[OK] 获取到 {len(df)} 条K线数据")
            for row in df[-5:]:
                print(row)
        else:
            print("[FAIL] 未能获取K线数据")

        print("\n" + "=" * 70)

    # 关闭爬虫
    close_spider()


if __name__ == "__main__":
    main()
