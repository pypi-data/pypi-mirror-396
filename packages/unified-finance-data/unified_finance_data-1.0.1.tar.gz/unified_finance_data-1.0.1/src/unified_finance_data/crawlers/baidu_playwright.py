"""
百度股市通ETF爬虫 - Playwright版本
自动管理浏览器驱动，无需手动配置ChromeDriver
遵循Golang设计哲学：简单、显式、专注
"""

import sys
import io
import logging

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..constants import FuquanType, PeriodType

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# 尝试导入pandas
PANDAS_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger(__name__)


class BaiduETFPlaywrightSpider:
    """
    使用Playwright获取百度股市通ETF数据
    优势：自动管理驱动，更稳定，更现代的API
    """

    BASE_URL = "https://gushitong.baidu.com/etf/ab-{code}"

    def __init__(self, headless: bool = True):
        """
        显式初始化

        Args:
            headless: 是否无头模式（True=后台运行，False=显示浏览器）
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright未安装，请先执行: pip install playwright")

        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._init_browser()

    def _init_browser(self):
        """初始化浏览器"""
        try:
            logger.info("初始化Playwright浏览器...")
            self.playwright = sync_playwright().start()

            # 启动浏览器 - 增强反检测
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-infobars',
                    '--start-maximized',
                    '--disable-extensions',
                ]
            )

            # 创建上下文（带完整的浏览器指纹）
            self.context = self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
            )

            # 创建页面
            self.page = self.context.new_page()

            # 注入脚本绕过检测
            self.page.add_init_script("""
                // 隐藏 webdriver 标志
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });

                // 模拟正常的 plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });

                // 模拟正常的 languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh', 'en']
                });

                // 修改 chrome 对象
                window.chrome = {
                    runtime: {}
                };

                // 修改权限查询
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
            """)

            logger.info("Playwright浏览器初始化成功")

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise

    def get_etf_data(self, code: str, wait_time: int = 5) -> Optional[Dict[str, Any]]:
        """
        获取ETF完整数据（最推荐的方法）

        Args:
            code: ETF代码，如 "159941"
            wait_time: 等待页面加载时间（秒）

        Returns:
            包含所有ETF数据的字典
        """
        url = self.BASE_URL.format(code=code)

        try:
            logger.debug(f"正在访问: {url}")
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

            logger.debug(f"等待 {wait_time} 秒确保数据加载完成...")
            self.page.wait_for_timeout(wait_time * 1000)

            # 提取数据
            data = {
                "code": code,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "basic_info": self._extract_basic_info(),
                "market_data": self._extract_market_data(),
                "order_book": self._extract_order_book(),
                "page_info": self._get_page_info()
            }

            return data

        except Exception as e:
            logger.error(f"获取数据失败: {e}")
            return None

    def _extract_basic_info(self) -> Dict[str, Any]:
        """提取ETF基本信息"""
        info = {}

        try:
            # 提取页面标题（包含ETF名称）
            info["page_title"] = self.page.title()

            # 等待一小段时间让页面渲染
            self.page.wait_for_timeout(2000)

            # 提取所有可见文本
            elements = self.page.locator("div, span, p").all()
            texts = []

            for elem in elements[:200]:  # 限制数量避免太慢
                try:
                    text = elem.inner_text().strip()
                    if text and 2 <= len(text) <= 100:
                        texts.append(text)
                except:
                    continue

            info["visible_texts"] = list(set(texts))  # 去重

            return info

        except Exception as e:
            logger.warning(f"提取基本信息失败: {e}")
            return {"page_title": self.page.title()}

    def _extract_market_data(self) -> Dict[str, Any]:
        """提取市场数据"""
        data = {}

        try:
            # 滚动到页面中部
            self.page.evaluate("window.scrollTo(0, window.innerHeight / 2)")
            self.page.wait_for_timeout(1000)

            # 尝试提取关键数据点
            # 查找价格相关元素
            price_selectors = [
                "text=/\\d+\\.\\d+/",
                "[class*='price']",
                "[class*='value']",
                "text=/涨跌幅|成交量|成交额/"
            ]

            market_texts = []
            for selector in price_selectors:
                try:
                    elements = self.page.locator(selector).all()
                    for elem in elements[:20]:  # 只取前20个
                        text = elem.inner_text().strip()
                        if text and len(text) < 50:
                            market_texts.append(text)
                except:
                    continue

            data["market_texts"] = list(set(market_texts))

            return data

        except Exception as e:
            logger.warning(f"提取市场数据失败: {e}")
            return {}

    def _extract_order_book(self) -> Dict[str, List[Dict]]:
        """提取买卖盘数据"""
        order_book = {"asks": [], "bids": []}

        try:
            # 滚动到页面底部（买卖盘通常在下方）
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.7)")
            self.page.wait_for_timeout(1000)

            # 尝试查找买卖盘元素
            # 查找包含"卖"、"买"文本的元素
            try:
                sell_elements = self.page.locator("text=/卖/").all()
                buy_elements = self.page.locator("text=/买/").all()

                for elem in sell_elements[:10]:
                    text = elem.inner_text().strip()
                    order_book["asks"].append({"text": text})

                for elem in buy_elements[:10]:
                    text = elem.inner_text().strip()
                    order_book["bids"].append({"text": text})

            except:
                pass

            return order_book

        except Exception as e:
            logger.warning(f"提取买卖盘失败: {e}")
            return order_book

    def _get_page_info(self) -> Dict[str, Any]:
        """获取页面信息"""
        try:
            return {
                "url": self.page.url,
                "viewport_size": self.page.viewport_size,
                "content_size": self.page.evaluate("""
                    () => ({
                        width: document.documentElement.scrollWidth,
                        height: document.documentElement.scrollHeight
                    })
                """)
            }
        except Exception as e:
            logger.warning(f"获取页面信息失败: {e}")
            return {}

    def get_kline_data(self, code: str, kline_type: str = "日K", wait_time: int = 5) -> Optional[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            code: ETF代码，如 "159941"
            kline_type: K线类型，可选 "日K", "周K", "月K", "年K"
            wait_time: 等待数据加载时间（秒）

        Returns:
            K线数据字典
        """
        url = self.BASE_URL.format(code=code)

        try:
            # 重置捕获的请求
            self.captured_requests = []

            # 启用网络监控
            self.page.on("response", lambda response: self._capture_kline_response(response))

            logger.debug(f"正在访问: {url}")
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

            # 等待页面加载
            self.page.wait_for_timeout(3000)

            # 点击对应的K线按钮
            logger.debug(f"正在点击 {kline_type} 按钮...")
            try:
                # 尝试点击K线类型按钮
                kline_button = self.page.locator(f"text={kline_type}").first
                kline_button.click()
                logger.debug(f"已点击 {kline_type}")
            except Exception as e:
                logger.debug(f"点击 {kline_type} 按钮失败: {e}")
                # 尝试其他方式
                try:
                    self.page.click(f"text={kline_type}")
                except:
                    pass

            # 等待数据加载
            logger.debug(f"等待 {wait_time} 秒加载K线数据...")
            self.page.wait_for_timeout(wait_time * 1000)

            # 从捕获的请求中提取K线数据
            kline_data = self._extract_kline_from_responses()

            return {
                "code": code,
                "kline_type": kline_type,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": kline_data
            }

        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            return None

    def _capture_kline_response(self, response):
        """捕获K线相关的响应"""
        if not hasattr(self, 'captured_requests'):
            self.captured_requests = []

        url = response.url
        # 捕获所有finance相关的API响应
        if 'finance.pae.baidu.com' in url:
            try:
                body = response.body()
                body_str = body.decode('utf-8', errors='ignore')

                # 检查是否包含K线相关数据
                if 'kline' in url.lower() or 'kline' in body_str.lower() or 'marketData' in body_str:
                    self.captured_requests.append({
                        "url": url,
                        "status": response.status,
                        "body": body_str
                    })
            except:
                pass

    def _extract_kline_from_responses(self) -> List[Dict]:
        """从捕获的响应中提取K线数据"""
        kline_list = []

        for req in self.captured_requests:
            body = req.get('body', '')
            if not body:
                continue

            try:
                data = json.loads(body)
                result = data.get('Result', {})

                # 查找newMarketData中的K线数据
                if 'newMarketData' in result:
                    market_data = result['newMarketData']
                    keys = market_data.get('keys', [])
                    raw_data = market_data.get('marketData', '')

                    # marketData是字符串格式，用;分隔每条记录
                    if isinstance(raw_data, str) and raw_data:
                        kline_list = self._parse_kline_string_with_keys(raw_data, keys)
                        if kline_list:
                            return kline_list

            except json.JSONDecodeError:
                continue
            except Exception as e:
                logger.warning(f"解析K线数据出错: {e}")
                continue

        return kline_list

    def _parse_kline_string_with_keys(self, kline_str: str, keys: List[str]) -> List[Dict]:
        """解析K线字符串格式数据（带字段名）"""
        kline_list = []

        if not kline_str:
            return kline_list

        # K线数据格式: 用;分隔每条记录，用,分隔字段
        # keys: ['timestamp', 'time', 'open', 'close', 'volume', 'high', 'low', 'amount', 'range', 'ratio', ...]
        lines = kline_str.strip().split(';')

        for line in lines:
            if not line.strip():
                continue

            parts = line.split(',')
            if len(parts) >= 7:  # 至少需要基本字段
                try:
                    kline = {}
                    for i, key in enumerate(keys):
                        if i < len(parts):
                            value = parts[i]
                            # 尝试转换为数值
                            if key in ['timestamp']:
                                kline[key] = int(value) if value and value != '--' else 0
                            elif key in ['time']:
                                kline[key] = value
                            elif value and value != '--':
                                try:
                                    # 去除+号
                                    kline[key] = float(value.replace('+', ''))
                                except:
                                    kline[key] = value
                            else:
                                kline[key] = None

                    # 确保有日期字段
                    if kline.get('time'):
                        kline_list.append(kline)

                except (ValueError, IndexError) as e:
                    continue

        return kline_list

    def capture_api_requests(self, code: str, wait_time: int = 10) -> Optional[Dict[str, Any]]:
        """
        捕获页面发出的API请求（最可靠的方法）

        Args:
            code: ETF代码
            wait_time: 等待收集请求的时间（秒）

        Returns:
            捕获的API请求数据
        """
        url = self.BASE_URL.format(code=code)

        try:
            # 重置捕获的请求
            self.captured_requests = []

            # 启用网络监控（必须在导航前注册）
            self.page.on("request", lambda request: self._log_request(request))
            self.page.on("response", lambda response: self._log_response(response))

            logger.debug(f"正在访问: {url}")
            self.page.goto(url, wait_until='domcontentloaded', timeout=60000)

            logger.debug(f"等待 {wait_time} 秒收集网络请求...")
            self.page.wait_for_timeout(wait_time * 1000)

            return {
                "code": code,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "requests": self.captured_requests
            }

        except Exception as e:
            logger.error(f"捕获API请求失败: {e}")
            return None

    def _log_request(self, request):
        """记录请求"""
        if not hasattr(self, 'captured_requests'):
            self.captured_requests = []

        url = request.url
        # 捕获所有finance相关的请求
        if 'finance.pae.baidu.com' in url or 'gushitong' in url:
            self.captured_requests.append({
                "type": "request",
                "url": url,
                "method": request.method,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

    def _log_response(self, response):
        """记录响应"""
        if not hasattr(self, 'captured_requests'):
            self.captured_requests = []

        url = response.url
        # 捕获K线、行情等数据接口
        if 'finance.pae.baidu.com' in url:
            entry = {
                "type": "response",
                "url": url,
                "status": response.status,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }

            # 尝试获取响应体
            try:
                body = response.body()
                entry["has_body"] = True
                entry["body_size"] = len(body)
                entry["body"] = body.decode('utf-8', errors='ignore')
            except:
                entry["has_body"] = False

            self.captured_requests.append(entry)

    def close(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.warning(f"关闭浏览器时出错: {e}")


def print_data_summary(data: Dict[str, Any]):
    """打印数据摘要"""
    if not data:
        print("[FAIL] 没有获取到数据")
        return

    print("=" * 70)
    print(f"ETF: {data['code']}")
    print(f"时间: {data['timestamp']}")
    print("=" * 70)

    # 基本信息
    basic = data.get('basic_info', {})
    if basic.get('page_title'):
        print(f"\n【页面标题】")
        print(f"  {basic['page_title']}")

    if basic.get('visible_texts'):
        print(f"\n【提取的关键数据】")
        texts = basic['visible_texts']

        # 提取价格信息
        price_info = []
        for text in texts:
            # 查找价格、涨跌幅、成交量等关键数据
            if any(kw in text for kw in ['ETF', '元', '%', '万手', '亿', '今开', '昨收', '最高', '最低', '成交', '量比']):
                if 3 <= len(text) <= 50:
                    price_info.append(text)

        # 去重并排序显示
        seen = set()
        for text in price_info:
            clean_text = text.strip()
            if clean_text not in seen and clean_text:
                seen.add(clean_text)
                print(f"  - {clean_text}")

    # 买卖盘
    orders = data.get('order_book', {})
    if orders.get('asks') or orders.get('bids'):
        print(f"\n【买卖盘数据】")
        print(f"  卖盘: {len(orders['asks'])} 条记录")
        print(f"  买盘: {len(orders['bids'])} 条记录")

    print("\n" + "=" * 70)


def install_playwright():
    """安装Playwright"""
    print("正在安装Playwright...")
    import subprocess
    import sys

    try:
        # 安装playwright库
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)

        # 安装浏览器
        print("正在安装Chromium浏览器...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

        print("[OK] Playwright安装完成")
        return True

    except Exception as e:
        print(f"安装失败: {e}")
        return False


def main():
    """主函数：演示如何使用"""
    import sys

    if not PLAYWRIGHT_AVAILABLE:
        print("=" * 70)
        print("Playwright 未安装")
        print("=" * 70)
        print("\n请运行以下命令安装 Playwright:")
        print("\n  1. 安装 Playwright 库:")
        print("     pip install playwright")
        print("\n  2. 安装 Chromium 浏览器:")
        print("     playwright install chromium")
        print("\n  3. 安装完成后，重新运行此脚本")
        print("\n" + "-" * 70)
        print("  或使用自动安装（需要管理员权限）:")
        print("     python baidu_etf_playwright.py install")
        print("=" * 70)

        if len(sys.argv) > 1 and sys.argv[1] == 'install':
            print("\n正在进行自动安装...")
            if install_playwright():
                print("\n[OK] 安装完成，请重新运行脚本")
                sys.exit(0)
            else:
                print("\n[FAIL] 自动安装失败，请手动安装")
                sys.exit(1)
        else:
            print("\n提示：可以运行 'python baidu_etf_playwright.py install' 自动安装")
        return

    # 解析命令行参数
    headless = '--headless' in sys.argv

    spider = None

    try:
        print("=" * 70)
        print("百度股市通ETF爬虫 - Playwright版本")
        print("=" * 70)
        print(f"\n运行模式: {'无头模式' if headless else '显示浏览器'}")
        print()

        # 创建爬虫
        spider = BaiduETFPlaywrightSpider(headless=headless)

        # 测试ETF列表
        test_etfs = [
            {"code": "159941", "name": "纳指ETF"},
        ]

        for etf in test_etfs:
            print(f"\n【正在获取 {etf['name']} ({etf['code']}) 日线数据】")
            print("-" * 70)

            # 获取日线K线数据
            kline_result = spider.get_kline_data(etf['code'], kline_type="日K", wait_time=5)

            if kline_result and kline_result.get('data'):
                kline_data = kline_result['data']
                print(f"[OK] 获取到 {len(kline_data)} 条K线数据")

                # 显示最近10条数据
                print("\n【最近10条日线数据】")
                print("-" * 85)
                print(f"{'日期':<12} {'开盘':>8} {'收盘':>8} {'最高':>8} {'最低':>8} {'成交量':>14} {'涨跌幅':>8}")
                print("-" * 85)

                for item in kline_data[-10:]:
                    date = item.get('time', 'N/A')
                    open_p = item.get('open', 0) or 0
                    close_p = item.get('close', 0) or 0
                    high_p = item.get('high', 0) or 0
                    low_p = item.get('low', 0) or 0
                    volume = item.get('volume', 0) or 0
                    ratio = item.get('ratio', 0) or 0

                    print(f"{str(date):<12} {float(open_p):>8.3f} {float(close_p):>8.3f} {float(high_p):>8.3f} {float(low_p):>8.3f} {float(volume):>14,.0f} {float(ratio):>7.2f}%")

                # 导出到CSV
                csv_file = f"etf_{etf['code']}_daily.csv"
                export_to_csv(kline_data, csv_file)
                print(f"\n[OK] 数据已导出到 {csv_file}")

            else:
                print("[FAIL] 未能获取K线数据")

            print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n运行出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if spider:
            spider.close()


# ============================================================================
# 简化接口函数 - 与 sina_kline_crawler.py 保持一致的API风格
# ============================================================================

# 全局爬虫实例（惰性初始化）
_global_spider = None


def _get_spider(headless: bool = True) -> BaiduETFPlaywrightSpider:
    """获取或创建全局爬虫实例"""
    global _global_spider
    if _global_spider is None:
        _global_spider = BaiduETFPlaywrightSpider(headless=headless)
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
            '换手率': 0.0,  # 百度数据中没有此字段
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
        是否使用无头模式，默认 True

    debug : bool
        是否启用调试模式

    Returns:
    -------
    pd.DataFrame 或 list
        标准化的K线数据，包含列：日期、开盘、收盘、最高、最低、成交量、成交额、振幅、涨跌幅、涨跌额、换手率
    """
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
        if DEBUG_MODE:
            print(f"获取K线数据失败: {e}")
        if PANDAS_AVAILABLE:
            return pd.DataFrame()
        return []
    finally:
        if original_debug is not None:
            DEBUG_MODE = original_debug


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
        是否使用无头模式，默认 True

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
                print("没有数据可保存")
                return
            data.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f'数据已保存到 {filename}')
            return

    # 字典列表格式
    if not data:
        print("没有数据可保存")
        return

    import csv
    headers = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in data:
            line = [row.get(h, '') for h in headers]
            writer.writerow(line)

    print(f'数据已保存到 {filename}')


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


if __name__ == "__main__":
    main()
