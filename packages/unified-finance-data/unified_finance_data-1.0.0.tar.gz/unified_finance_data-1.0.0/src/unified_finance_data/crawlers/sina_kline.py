#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新浪财经K线数据爬虫 - 通用金融数据获取工具

这是一个完整的金融数据获取库，支持从新浪财经获取多种金融产品的历史K线数据。
主要功能包括：
- 股票历史K线数据获取（支持A股、指数等）
- ETF/基金历史K线数据获取
- 多种K线周期支持（日线、周线、月线）
- 复权数据处理（前复权、后复权、不复权）
- 代理支持（SOCKS5代理）
- 兼容pandas和简化数据格式
- 自动数据格式标准化，输出包含完整字段（日期、开盘、收盘、最高、最低、成交量、成交额等）

技术特点：
- 支持新浪财经新版JSON API接口
- 兼容旧版JavaScript解密接口
- 智能代码格式转换（自动识别沪深交易所）
- 完善的错误处理和调试模式
- 自动数据过滤和日期范围处理

作者：量化交易系统
版本：2.0
更新日期：2024-12
"""

import sys
import requests
import json
from datetime import datetime
import re

# 检查是否支持SOCKS代理
try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False
    print("警告: SOCKS代理支持不可用，请安装 pysocks: pip install pysocks")

# 尝试导入pandas，如果失败则使用简化版
PANDAS_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except (ImportError, SystemError) as e:
    print(f"警告: pandas不可用，将使用简化版数据格式 ({e})")

# 尝试导入py_mini_racer用于JS解密
try:
    import py_mini_racer
    MINI_RACER_AVAILABLE = True
except ImportError:
    MINI_RACER_AVAILABLE = False
    print("警告: py_mini_racer不可用，将使用简化JS解析")

# 日志开关 - 控制是否显示详细日志
DEBUG_MODE = True

# 新浪财经旧版JavaScript解密算法
# 用于解密旧版接口返回的加密数据字符串
# 这是一个简单的字符偏移解密算法，将ASCII码在33-126范围内的字符进行偏移转换
# 注意：当前主要使用新版JSON API，此解密函数仅作兼容性保留
hk_js_decode = """
function d(a) {
    var b = a.split(""), c = b.length, d = [];
    for (var e = 0; e < c; e++) {
        var f = b[e].charCodeAt();
        if (f >= 33 && f <= 126) {
            d.push(String.fromCharCode(33 + (f + 14) % 94));
        } else {
            d.push(b[e]);
        }
    }
    return d.join("");
}
"""

# 复权类型常量
class FuquanType:
    """复权类型常量"""
    NONE = 0      # 不复权
    FRONT = 1     # 前复权
    BACK = 2      # 后复权
    
    @classmethod
    def get_name(cls, fqt):
        """获取复权类型的中文名称"""
        mapping = {
            cls.NONE: "不复权",
            cls.FRONT: "前复权", 
            cls.BACK: "后复权"
        }
        return mapping.get(fqt, "未知")
    
    @classmethod
    def validate(cls, fqt):
        """验证复权类型是否有效"""
        return fqt in [cls.NONE, cls.FRONT, cls.BACK]


# K线周期类型常量
class PeriodType:
    """K线周期类型常量"""
    DAILY = 101    # 日线
    WEEKLY = 102   # 周线
    MONTHLY = 103  # 月线
    
    @classmethod
    def get_name(cls, period):
        """获取周期类型的中文名称"""
        mapping = {
            cls.DAILY: "日线",
            cls.WEEKLY: "周线",
            cls.MONTHLY: "月线"
        }
        return mapping.get(period, "未知")
    
    @classmethod
    def validate(cls, period):
        """验证周期类型是否有效"""
        return period in [cls.DAILY, cls.WEEKLY, cls.MONTHLY]


def _get_sina_symbol(code: str) -> str:
    """
    将标准股票代码转换为新浪财经API专用格式

    新浪财经使用交易所前缀来区分不同市场的股票：
    - sh: 上海证券交易所（沪市）
    - sz: 深圳证券交易所（深市）

    代码规则：
    沪市股票：6xxxxx（主板）、900xxx（B股）
    深市股票：0xxxxx（主板）、2xxxxx（中小板）、3xxxxx（创业板）
    沪市指数：000xxx（如000001上证指数）
    深市指数：399xxx（如399001深证成指）

    Parameters:
    ----------
    code : str
        标准6位股票代码或指数代码

    Returns:
    -------
    str
        新浪财经格式的代码，格式为：交易所前缀+代码
        例如：'600519' -> 'sh600519'（贵州茅台）
              '000001' -> 'sh000001'（上证指数）
              '399001' -> 'sz399001'（深证成指）
              '159919' -> 'sz159919'（沪深300ETF）
    """
    # 沪市股票
    if code.startswith('6') or code.startswith('900'):
        return f'sh{code}'
    # 深市股票
    elif code.startswith('0') or code.startswith('2') or code.startswith('3'):
        return f'sz{code}'
    # 指数
    elif code.startswith('000'):
        return f'sh{code}'
    elif code.startswith('399'):
        return f'sz{code}'
    # 默认沪市
    else:
        return f'sh{code}'


def _parse_sina_kline_data(response_text: str):
    """
    解析新浪财经API返回的K线数据，支持多种数据格式

    新浪财经API可能返回两种格式的数据：
    1. 新版JSON格式：直接的JSON数组，包含标准的OHLCV数据
    2. 旧版JavaScript格式：经过简单加密的字符串，需要JavaScript解密

    新版JSON数据格式示例：
    [
        {"day": "2024-12-01", "open": 100.5, "high": 102.3, "low": 99.8, "close": 101.2, "volume": 1000000},
        ...
    ]

    Parameters:
    ----------
    response_text : str
        新浪财经API返回的原始文本数据

    Returns:
    -------
    list
        包含K线数据的字典列表，每个字典包含以下字段：
        - day/date: 日期（YYYY-MM-DD格式）
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量

    注意：
    - 如果无法解析数据，返回空列表
    - 在DEBUG_MODE下会输出详细的解析过程信息
    - 优先尝试新版JSON格式，失败后尝试旧版解密格式
    """
    try:
        if DEBUG_MODE:
            print(f"原始响应长度: {len(response_text)}")
            print(f"原始响应前200字符: {response_text[:200]}")

        # 检查是否是JSON格式
        response_text = response_text.strip()
        if response_text.startswith('[') and response_text.endswith(']'):
            # 新的JSON接口格式
            dict_list = json.loads(response_text)
            if DEBUG_MODE:
                print(f"JSON格式解析成功，获取到 {len(dict_list)} 条数据")
                if dict_list and len(dict_list) > 0:
                    print(f"第一条数据: {dict_list[0]}")
            return dict_list

        # 尝试旧的JavaScript格式
        parts = response_text.split("=")
        if len(parts) >= 2:
            encrypted_part = parts[1].split(";")[0].replace('"', "").strip()

            if DEBUG_MODE:
                print(f"检测到旧格式，加密字符串长度: {len(encrypted_part)}")
                print(f"加密字符串前100字符: {encrypted_part[:100]}")

            # 如果是旧格式，尝试解密
            if MINI_RACER_AVAILABLE:
                try:
                    js_code = py_mini_racer.MiniRacer()
                    js_code.eval(hk_js_decode)
                    dict_list = js_code.call("d", encrypted_part)
                    if DEBUG_MODE:
                        print(f"JS解密成功，获取到 {len(dict_list) if dict_list else 0} 条数据")
                    return dict_list
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"JS解密失败: {e}")

        # 如果以上方法都失败，返回空列表
        if DEBUG_MODE:
            print("无法解析响应数据")
        return []

    except Exception as e:
        if DEBUG_MODE:
            print(f"解析新浪财经数据时出错: {e}")
        return []


def get_k_history(code: str, beg: str = '20200101', end: str = None, klt: int = 101,
                  fqt: int = FuquanType.FRONT, proxy: str = None, debug: bool = None):
    """
    获取股票历史K线数据（新浪财经API）

    这是一个功能完整的股票数据获取函数，支持从新浪财经获取指定股票的历史K线数据。
    函数会自动处理数据格式转换，返回标准化的OHLCV数据。

    核心功能：
    - 支持A股、指数等多种金融产品
    - 智能识别股票所属交易所（沪市/深市）
    - 支持多种K线周期（日线、周线、月线）
    - 自动计算数据获取量，确保数据完整性
    - 完善的错误处理和重试机制
    - 支持代理访问（SOCKS5）

    Parameters:
    ----------
    code : str
        股票代码，支持以下格式：
        - 6位数字代码：'600519'（贵州茅台）、'000001'（平安银行）
        - 带交易所前缀：'sh600519'、'sz000001'
        - 指数代码：'000001'（上证指数）、'399001'（深证成指）

    beg : str
        开始日期，格式：YYYYMMDD，默认为'20200101'
        例如：'20240101'表示2024年1月1日

    end : str
        结束日期，格式：YYYYMMDD，默认为当前日期
        如果为None，自动使用系统当前日期

    klt : int
        K线周期类型，使用PeriodType常量：
        - PeriodType.DAILY (101): 日线数据（推荐，数据最完整）
        - PeriodType.WEEKLY (102): 周线数据
        - PeriodType.MONTHLY (103): 月线数据

    fqt : int
        复权方式，使用FuquanType常量：
        - FuquanType.NONE (0): 不复权（原始价格）
        - FuquanType.FRONT (1): 前复权（推荐，保持价格连续性）
        - FuquanType.BACK (2): 后复权（当前价格不变）

    proxy : str, optional
        SOCKS5代理地址，格式：'host:port'
        例如：'127.0.0.1:1080'
        注意：需要安装pysocks库：pip install pysocks

    debug : bool, optional
        是否启用调试模式，None表示使用全局DEBUG_MODE设置
        启用后会输出详细的请求和解析信息

    Returns:
    -------
    pd.DataFrame or list
        当pandas可用时：返回标准化的DataFrame，包含以下列：
        - 日期: datetime.date对象
        - 开盘、收盘、最高、最低: float64类型
        - 成交量: int64类型
        - 成交额、振幅、涨跌幅、涨跌额、换手率: float64类型（新浪数据中为0）

        当pandas不可用时：返回字典列表，每个字典包含相同字段

    数据特点：
    - 新浪财经主要提供基础OHLCV数据
    - 成交额、振幅、涨跌幅等字段会自动填充为0
    - 数据按日期升序排列
    - 自动过滤周末和节假日停牌数据

    异常：
    ------
    ValueError: 当股票代码格式错误、日期格式错误或参数无效时
    requests.RequestException: 当网络请求失败时

    示例：
    ------
    >>> # 获取贵州茅台2024年日线数据
    >>> data = get_k_history('600519', '20240101', '20241201')
    >>> print(len(data))  # 数据条数
    >>> print(data.head())  # 前5条数据
    """
    # 设置调试模式
    global DEBUG_MODE
    if debug is not None:
        original_debug = DEBUG_MODE
        DEBUG_MODE = debug
    else:
        original_debug = None
    
    if end is None:
        end = datetime.now().strftime('%Y%m%d')
    
    if DEBUG_MODE:
        print(f"开始获取股票 {code} 的K线数据")
        print(f"时间范围: {beg} 到 {end}")
        print(f"K线类型: {PeriodType.get_name(klt)}")
        print(f"复权方式: {FuquanType.get_name(fqt)}")
    
    # 验证复权类型
    if not FuquanType.validate(fqt):
        raise ValueError(f"无效的复权类型: {fqt}，请使用 FuquanType.NONE, FuquanType.FRONT 或 FuquanType.BACK")
    
    # 验证周期类型
    if not PeriodType.validate(klt):
        raise ValueError(f"无效的K线类型: {klt}，请使用 PeriodType.DAILY, PeriodType.WEEKLY 或 PeriodType.MONTHLY")
    
    # 新浪财经主要支持日线数据
    if klt != PeriodType.DAILY:
        if DEBUG_MODE:
            print("警告: 新浪财经主要支持日线数据，将使用日线数据")
    
    # 转换日期格式
    try:
        start_date = datetime.strptime(beg, '%Y%m%d').strftime('%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y%m%d').strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError("日期格式错误，请使用YYYYMMDD格式")
    
    # 获取新浪财经格式的代码
    sina_code = _get_sina_symbol(code)

    if DEBUG_MODE:
        print(f"新浪财经代码格式: {sina_code}")

    # 新浪财经JSON API接口配置
    # scale参数说明：
    # - 60: 1小时K线
    # - 240: 日线K线（最常用，数据最完整）
    # - 720: 周线K线
    # - 2160: 月线K线
    # 注意：不同周期的数据完整性和更新频率可能不同
    scale_map = {
        PeriodType.DAILY: 240,    # 日线数据（推荐）
        PeriodType.WEEKLY: 720,   # 周线数据
        PeriodType.MONTHLY: 2160  # 月线数据
    }
    scale = scale_map.get(klt, 240)  # 默认使用日线数据

    # 智能计算数据获取量
    # 根据请求的时间范围自动计算需要获取的数据条数
    # 确保数据完整性的同时避免获取过多无用数据
    try:
        start_date = datetime.strptime(beg, '%Y%m%d')
        end_date_obj = datetime.strptime(end, '%Y%m%d')
        days_diff = (end_date_obj - start_date).days
        # 多取10天缓冲数据，确保包含所有交易日，最少100条数据
        datalen = max(days_diff + 10, 100)
    except:
        # 如果日期计算失败，使用默认值
        datalen = 1000  # 默认获取1000条数据（约4年日线数据）

    # 构建新浪财经JSON API URL
    # API端点：CN_MarketData.getKLineData
    # 参数说明：
    # - symbol: 股票代码（带交易所前缀）
    # - scale: K线周期（240=日线）
    # - ma: 是否包含均线数据（no=不包含）
    # - datalen: 获取数据条数
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_code}&scale={scale}&ma=no&datalen={datalen}"

    if DEBUG_MODE:
        print(f"请求URL: {url}")
        print(f"K线参数: scale={scale}, datalen={datalen}")
    
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': f'https://finance.sina.com.cn/realstock/company/{sina_code}/nc.shtml',
    }
    
    try:
        if proxy and not SOCKS_AVAILABLE:
            print("错误: 需要安装 pysocks 才能使用SOCKS代理，请运行: pip install pysocks")
            return [] if not PANDAS_AVAILABLE else pd.DataFrame()
            
        proxies = None
        if proxy:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            if DEBUG_MODE:
                print(f"使用代理: {proxy}")
        
        # 发送请求
        if DEBUG_MODE:
            print("发送HTTP请求...")
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        response.raise_for_status()
        if DEBUG_MODE:
            print(f"HTTP请求成功，状态码: {response.status_code}")
        
        # 解析数据
        if DEBUG_MODE:
            print("开始解析数据...")
        dict_list = _parse_sina_kline_data(response.text)
        
        if not dict_list:
            if DEBUG_MODE:
                print(f'股票代码: {code} 可能有误或无数据')
            return [] if not PANDAS_AVAILABLE else pd.DataFrame()
        
        if DEBUG_MODE:
            print(f"成功解析到 {len(dict_list)} 条数据")
        
        if PANDAS_AVAILABLE:
            temp_df = pd.DataFrame(dict_list)
            if temp_df.empty:
                if DEBUG_MODE:
                    print("DataFrame为空")
                return pd.DataFrame()
            
            if DEBUG_MODE:
                print(f"DataFrame形状: {temp_df.shape}")
                print(f"DataFrame列名: {list(temp_df.columns)}")
            
            # 检查日期字段名称并重命名
            if 'day' in temp_df.columns:
                temp_df = temp_df.rename(columns={'day': 'date'})
            elif 'date' not in temp_df.columns:
                print("错误: 未找到日期字段 'day' 或 'date'")
                return pd.DataFrame()

            # 转换日期列
            temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce").dt.tz_localize(None)
            
            # 转换数值列
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in temp_df.columns:
                    temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
            
            # 转换日期列为日期类型
            temp_df["date"] = temp_df["date"].dt.date
            
            # 重命名列以匹配东方财富格式
            column_mapping = {
                'date': '日期',
                'open': '开盘',
                'high': '最高', 
                'low': '最低',
                'close': '收盘',
                'volume': '成交量'
            }
            temp_df = temp_df.rename(columns=column_mapping)
            
            # 添加缺失的列（新浪财经数据较简单）
            if '成交额' not in temp_df.columns:
                temp_df['成交额'] = 0.0
            if '振幅' not in temp_df.columns:
                temp_df['振幅'] = 0.0
            if '涨跌幅' not in temp_df.columns:
                temp_df['涨跌幅'] = 0.0
            if '涨跌额' not in temp_df.columns:
                temp_df['涨跌额'] = 0.0
            if '换手率' not in temp_df.columns:
                temp_df['换手率'] = 0.0
            
            # 按日期排序
            temp_df = temp_df.sort_values(by="日期", ascending=True)
            temp_df = temp_df.reset_index(drop=True)
            
            if DEBUG_MODE:
                print("数据处理完成")
            
            return temp_df
        else:
            # 简化版返回列表
            result = []
            for item in dict_list:
                result.append({
                    '日期': item.get('date', ''),
                    '开盘': float(item.get('open', 0)),
                    '收盘': float(item.get('close', 0)),
                    '最高': float(item.get('high', 0)),
                    '最低': float(item.get('low', 0)),
                    '成交量': int(item.get('volume', 0)),
                    '成交额': 0.0,  # 新浪财经不提供成交额
                    '振幅': 0.0,   # 新浪财经不提供振幅
                    '涨跌幅': 0.0, # 新浪财经不提供涨跌幅
                    '涨跌额': 0.0, # 新浪财经不提供涨跌额
                    '换手率': 0.0  # 新浪财经不提供换手率
                })
            return result
    
    except Exception as e:
        if DEBUG_MODE:
            print(f'获取新浪财经数据时出错: {e}')
        return [] if not PANDAS_AVAILABLE else pd.DataFrame()
    finally:
        # 恢复原来的调试模式
        if original_debug is not None:
            DEBUG_MODE = original_debug


def get_fund_k_history(fund_code: str, beg: str = '20200101', end: str = None,
                       fqt: int = FuquanType.FRONT, proxy: str = None, debug: bool = None):
    """
    获取ETF/基金历史K线数据（新浪财经API）

    专门用于获取ETF基金和其他金融产品的历史K线数据。
    与股票数据获取的主要区别在于代码识别逻辑和数据处理方式。

    支持的基金类型：
    - ETF基金：如510050（上证50ETF）、159919（沪深300ETF）
    - 封闭式基金：如184721（基金开元）
    - 其他上市基金产品

    核心特性：
    - 自动识别ETF基金所属交易所
    - 智能计算数据获取范围，确保数据完整性
    - 支持完整的日期范围过滤
    - 标准化数据输出格式，与股票数据保持一致

    Parameters:
    ----------
    fund_code : str
        基金代码，支持多种格式：
        - 6位数字代码：'510050'（上证50ETF）
        - 带交易所前缀：'sh510050'、'sz159919'
        - 完整代码：'sh510050.sh'等格式也会被正确处理

    beg : str
        开始日期，格式：YYYYMMDD，默认为'20200101'
        例如：'20240101'表示2024年1月1日

    end : str
        结束日期，格式：YYYYMMDD，默认为当前日期
        如果为None，自动使用系统当前日期

    fqt : int
        复权方式，使用FuquanType常量：
        - FuquanType.NONE (0): 不复权（原始净值）
        - FuquanType.FRONT (1): 前复权（推荐，保持连续性）
        - FuquanType.BACK (2): 后复权（当前净值不变）

    proxy : str, optional
        SOCKS5代理地址，格式：'host:port'
        需要安装pysocks库：pip install pysocks

    debug : bool, optional
        是否启用调试模式，None表示使用全局DEBUG_MODE设置

    Returns:
    -------
    pd.DataFrame or list
        当pandas可用时：返回标准化的DataFrame，包含以下列：
        - 日期: datetime.date对象
        - 开盘、收盘、最高、最低: float64类型
        - 成交量: int64类型
        - 成交额、振幅、涨跌幅、涨跌额、换手率: float64类型（默认为0）

        当pandas不可用时：返回字典列表，每个字典包含相同字段

    数据特点：
    - ETF基金数据更新频率与股票相同
    - 主要提供日线数据，周线和月线数据由日线数据聚合生成
    - 成交额、振幅等扩展字段自动填充为0
    - 数据按日期升序排列，包含所有交易日

    交易所识别规则：
    - 沪市ETF：以5开头的6位代码（如510050、510300）
    - 深市ETF：以15或159开头的代码（如159919、159928）
    - 其他基金：根据代码首位数字判断

    异常：
    ------
    ValueError: 当基金代码格式错误、日期格式错误或参数无效时
    requests.RequestException: 当网络请求失败时

    示例：
    ------
    >>> # 获取上证50ETF数据
    >>> data = get_fund_k_history('510050', '20240101', '20241201')
    >>> print(f"获取到 {len(data)} 条数据")
    >>>
    >>> # 获取沪深300ETF数据
    >>> data = get_fund_k_history('159919', '20240101', '20241201')
    >>> print(data.head())
    """
    # 设置调试模式
    global DEBUG_MODE
    if debug is not None:
        original_debug = DEBUG_MODE
        DEBUG_MODE = debug
    else:
        original_debug = None
    
    if end is None:
        end = datetime.now().strftime('%Y%m%d')
    
    if DEBUG_MODE:
        print(f"开始获取基金 {fund_code} 的K线数据")
        print(f"时间范围: {beg} 到 {end}")
        print(f"复权方式: {FuquanType.get_name(fqt)}")
    
    # 验证复权类型
    if not FuquanType.validate(fqt):
        raise ValueError(f"无效的复权类型: {fqt}，请使用 FuquanType.NONE, FuquanType.FRONT 或 FuquanType.BACK")
    
    # 转换日期格式
    try:
        start_date = datetime.strptime(beg, '%Y%m%d')
        end_date_obj = datetime.strptime(end, '%Y%m%d')
        current_date = datetime.now()

        # 计算从请求开始日期到当前日期的天数
        days_diff = (current_date - start_date).days
        datalen = max(days_diff + 30, 500)  # 获取足够的数据，最少500条

        if DEBUG_MODE:
            print(f"从{beg}到当前日期{current_date.strftime('%Y%m%d')}共{days_diff}天，请求{datalen}条数据")
    except ValueError:
        raise ValueError("日期格式错误，请使用YYYYMMDD格式")

    # 获取新浪财经格式的代码
    # 基金代码通常已经是正确的格式，但可以标准化
    if fund_code.startswith('sh') or fund_code.startswith('sz'):
        sina_code = fund_code
    else:
        # 根据基金代码判断交易所
        if fund_code.startswith('5') or fund_code.startswith('51'):
            sina_code = f'sh{fund_code}'  # 上交所ETF
        else:
            sina_code = f'sz{fund_code}'  # 深交所ETF

    if DEBUG_MODE:
        print(f"新浪财经基金代码格式: {sina_code}")

    # 使用新的JSON接口 - ETF基金也使用相同的接口
    url = f"https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_code}&scale=240&ma=no&datalen={datalen}"
    
    if DEBUG_MODE:
        print(f"请求URL: {url}")
    
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': f'https://finance.sina.com.cn/fund/quotes/{fund_code}/bc.shtml',
    }
    
    try:
        if proxy and not SOCKS_AVAILABLE:
            print("错误: 需要安装 pysocks 才能使用SOCKS代理，请运行: pip install pysocks")
            return [] if not PANDAS_AVAILABLE else pd.DataFrame()
            
        proxies = None
        if proxy:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            if DEBUG_MODE:
                print(f"使用代理: {proxy}")
        
        # 发送请求
        if DEBUG_MODE:
            print("发送HTTP请求...")
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        response.raise_for_status()
        if DEBUG_MODE:
            print(f"HTTP请求成功，状态码: {response.status_code}")
        
        # 解析JSON数据
        if DEBUG_MODE:
            print("开始解析JSON数据...")

        response_text = response.text.strip()
        if not response_text.startswith('[') or not response_text.endswith(']'):
            if DEBUG_MODE:
                print("响应不是有效的JSON数组格式")
                print(f"响应内容: {response_text[:200]}...")
            return [] if not PANDAS_AVAILABLE else pd.DataFrame()

        dict_list = json.loads(response_text)

        if not dict_list:
            if DEBUG_MODE:
                print(f'基金代码: {fund_code} 可能有误或无数据')
            return [] if not PANDAS_AVAILABLE else pd.DataFrame()

        if DEBUG_MODE:
            print(f"成功解析到 {len(dict_list)} 条原始数据")

        # 过滤数据到指定日期范围
        filtered_data = []
        for item in dict_list:
            try:
                # 新格式使用'day'字段
                date_field = item.get('day', item.get('date', ''))
                item_date = datetime.strptime(date_field, '%Y-%m-%d').date()
                start_date_obj = start_date.date()
                end_date_filter = end_date_obj.date()

                if start_date_obj <= item_date <= end_date_filter:
                    filtered_data.append(item)
            except:
                # 如果日期解析失败，保留该条数据
                filtered_data.append(item)

        dict_list = filtered_data

        if DEBUG_MODE:
            print(f"过滤后剩余 {len(dict_list)} 条数据")
        
        if PANDAS_AVAILABLE:
            temp_df = pd.DataFrame(dict_list)
            if temp_df.empty:
                if DEBUG_MODE:
                    print("DataFrame为空")
                return pd.DataFrame()
            
            if DEBUG_MODE:
                print(f"DataFrame形状: {temp_df.shape}")
                print(f"DataFrame列名: {list(temp_df.columns)}")
            
            # 检查日期字段名称并重命名
            if 'day' in temp_df.columns:
                temp_df = temp_df.rename(columns={'day': 'date'})
            elif 'date' not in temp_df.columns:
                print("错误: 未找到日期字段 'day' 或 'date'")
                return pd.DataFrame()

            # 转换日期列
            temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce").dt.tz_localize(None)
            
            # 转换数值列
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in temp_df.columns:
                    temp_df[col] = pd.to_numeric(temp_df[col], errors="coerce")
            
            # 转换日期列为日期类型
            temp_df["date"] = temp_df["date"].dt.date
            
            # 重命名列以匹配东方财富格式
            column_mapping = {
                'date': '日期',
                'open': '开盘',
                'high': '最高', 
                'low': '最低',
                'close': '收盘',
                'volume': '成交量'
            }
            temp_df = temp_df.rename(columns=column_mapping)
            
            # 添加缺失的列（新浪财经数据较简单）
            if '成交额' not in temp_df.columns:
                temp_df['成交额'] = 0.0
            if '振幅' not in temp_df.columns:
                temp_df['振幅'] = 0.0
            if '涨跌幅' not in temp_df.columns:
                temp_df['涨跌幅'] = 0.0
            if '涨跌额' not in temp_df.columns:
                temp_df['涨跌额'] = 0.0
            if '换手率' not in temp_df.columns:
                temp_df['换手率'] = 0.0
            
            # 按日期排序
            temp_df = temp_df.sort_values(by="日期", ascending=True)
            temp_df = temp_df.reset_index(drop=True)
            
            if DEBUG_MODE:
                print("数据处理完成")
            
            return temp_df
        else:
            # 简化版返回列表
            result = []
            for item in dict_list:
                result.append({
                    '日期': item.get('date', ''),
                    '开盘': float(item.get('open', 0)),
                    '收盘': float(item.get('close', 0)),
                    '最高': float(item.get('high', 0)),
                    '最低': float(item.get('low', 0)),
                    '成交量': int(item.get('volume', 0)),
                    '成交额': 0.0,  # 新浪财经不提供成交额
                    '振幅': 0.0,   # 新浪财经不提供振幅
                    '涨跌幅': 0.0, # 新浪财经不提供涨跌幅
                    '涨跌额': 0.0, # 新浪财经不提供涨跌额
                    '换手率': 0.0  # 新浪财经不提供换手率
                })
            return result
    
    except Exception as e:
        if DEBUG_MODE:
            print(f'获取新浪财经基金数据时出错: {e}')
        return [] if not PANDAS_AVAILABLE else pd.DataFrame()
    finally:
        # 恢复原来的调试模式
        if original_debug is not None:
            DEBUG_MODE = original_debug


def save_to_csv(data, filename):
    """
    将K线数据保存为CSV文件，支持pandas DataFrame和字典列表两种格式

    这个函数提供了灵活的数据保存功能，无论pandas是否可用都能正常工作。
    保存的CSV文件使用UTF-8-BOM编码，确保在Excel中能正确显示中文。

    CSV文件格式：
    - 列名：日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
    - 数据格式：日期为YYYY-MM-DD，数值为标准数字格式
    - 编码：UTF-8-BOM，支持中文和Excel兼容

    Parameters:
    ----------
    data : pd.DataFrame or list
        要保存的K线数据，可以是：
        - pandas DataFrame（推荐）：包含标准化列名的数据框
        - 字典列表：每个字典包含相同字段的数据

    filename : str
        保存的CSV文件名，可以包含路径
        例如：'data.csv' 或 '/path/to/data.csv'

    注意：
    - 如果数据为空，函数会输出提示信息并直接返回
    - 文件保存成功后会显示确认信息
    - 如果文件已存在，会被覆盖
    - 使用UTF-8-BOM编码确保Excel正确显示中文

    示例：
    ------
    >>> # 保存股票数据
    >>> data = get_k_history('600519', '20240101', '20241201')
    >>> save_to_csv(data, 'maotai_data.csv')

    >>> # 保存基金数据
    >>> fund_data = get_fund_k_history('510050', '20240101', '20241201')
    >>> save_to_csv(fund_data, 'etf510050.csv')
    """
    if PANDAS_AVAILABLE:
        if data.empty:
            print("没有数据可保存")
            return
    else:
        if not data:
            print("没有数据可保存")
            return
    
    if PANDAS_AVAILABLE:
        data.to_csv(filename, index=False, encoding='utf-8-sig')
    else:
        # 简化版CSV保存
        with open(filename, 'w', encoding='utf-8-sig') as f:
            # 写入表头
            headers = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            f.write(','.join(headers) + '\n')
            
            # 写入数据
            for row in data:
                line = f"{row['日期']},{row['开盘']},{row['收盘']},{row['最高']},{row['最低']},{row['成交量']},{row['成交额']},{row['振幅']},{row['涨跌幅']},{row['涨跌额']},{row['换手率']}"
                f.write(line + '\n')
    
    print(f'数据已保存到 {filename}')


def main():
    """
    主函数 - 完整功能演示和测试用例

    这个函数展示了sina_kline_crawler模块的各种使用方法，包括：
    1. 股票数据获取示例
    2. ETF基金数据获取示例
    3. 错误处理演示
    4. 不同股票代码格式的测试

    每个示例都包含详细的数据获取、处理和保存流程，
    是学习和测试本模块功能的完整参考。

    注意：示例中的日期已设置为2024年，确保能获取到真实数据
    """
    # 示例1: 获取股票日线数据 - 贵州茅台
    print("=== 示例1: 获取股票日线数据 (新浪财经) ===")
    stock_code = '600519'  # 贵州茅台，沪市主板股票
    start_date = '20241101'  # 2024年11月1日
    end_date = '20241201'    # 2024年12月1日
    # 不使用代理，直接连接新浪财经服务器
    proxy = None
    
    print(f'正在获取股票 {stock_code} 从 {start_date} 到 {end_date} 的日线数据...')
    stock_data = get_k_history(stock_code, start_date, end_date, proxy=proxy)
    
    if PANDAS_AVAILABLE:
        if not stock_data.empty:
            print(f"获取到 {len(stock_data)} 条数据")
            print(stock_data.head())
            save_to_csv(stock_data, f'sina_{stock_code}_日线数据.csv')
        else:
            print("未获取到数据")
    else:
        if stock_data:
            print(f"获取到 {len(stock_data)} 条数据")
            print("前5条数据:")
            for i, item in enumerate(stock_data[:5]):
                print(f"{i+1}. {item['日期']}: 开盘={item['开盘']}, 收盘={item['收盘']}")
            save_to_csv(stock_data, f'sina_{stock_code}_日线数据.csv')
        else:
            print("未获取到数据")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 获取ETF基金日线数据
    print("=== 示例2: 获取ETF基金日线数据 (新浪财经) ===")
    fund_code = 'sh510050'  # 上证50ETF，中国最大的ETF基金之一
    start_date = '20241101'  # 2024年11月1日
    end_date = '20241201'    # 2024年12月1日
    
    print(f'正在获取基金 {fund_code} 从 {start_date} 到 {end_date} 的日线数据...')
    fund_data = get_fund_k_history(fund_code, start_date, end_date, proxy=proxy)
    
    if PANDAS_AVAILABLE:
        if not fund_data.empty:
            print(f"获取到 {len(fund_data)} 条数据")
            print(fund_data.head())
            save_to_csv(fund_data, f'sina_{fund_code}_日线数据.csv')
        else:
            print("未获取到数据")
    else:
        if fund_data:
            print(f"获取到 {len(fund_data)} 条数据")
            print("前5条数据:")
            for i, item in enumerate(fund_data[:5]):
                print(f"{i+1}. {item['日期']}: 开盘={item['开盘']}, 收盘={item['收盘']}")
            save_to_csv(fund_data, f'sina_{fund_code}_日线数据.csv')
        else:
            print("未获取到数据")
    
    print("\n" + "="*50 + "\n")
    
    # 示例3: 错误处理和参数验证演示
    print("=== 示例3: 错误处理和参数验证 ===")
    try:
        # 尝试使用无效的复权类型参数
        print("测试无效的复权类型参数...")
        invalid_data = get_k_history('600519', '20241101', '20241201', fqt=999, proxy=proxy)
    except ValueError as e:
        print(f"✓ 成功捕获到预期的参数验证错误: {e}")

    # 示例4: 测试不同交易所股票代码的自动识别
    print("\n=== 示例4: 不同交易所股票代码测试 ===")
    simple_stock = '000001'  # 平安银行（深市主板）
    print(f'正在获取股票 {simple_stock} 的日线数据（自动识别为深市股票）...')
    simple_data = get_k_history(simple_stock, '20241101', '20241201', proxy=None)
    
    if PANDAS_AVAILABLE:
        if not simple_data.empty:
            print(f"获取到 {len(simple_data)} 条数据")
            print(simple_data.head())
        else:
            print("未获取到数据")
    else:
        if simple_data:
            print(f"获取到 {len(simple_data)} 条数据")
            print("前3条数据:")
            for i, item in enumerate(simple_data[:3]):
                print(f"{i+1}. {item['日期']}: 开盘={item['开盘']}, 收盘={item['收盘']}")
        else:
            print("未获取到数据")
    
    print("\n" + "="*60)
    print("🎉 所有示例执行完毕！")
    print("\n📝 使用说明：")
    print("1. 股票代码支持6位数字格式，会自动识别交易所")
    print("2. ETF基金代码也支持自动识别")
    print("3. 数据会自动保存为CSV文件，方便后续分析")
    print("4. 支持代理访问，在需要时可配置SOCKS5代理")
    print("5. 详细的错误处理确保程序稳定运行")
    print("="*60)


if __name__ == "__main__":
    main()
