# coding=utf-8
from thriftpy2.transport import TTransportException

from .client import PQDataClient
from .utils import *
from typing import Union, List, Optional, Dict, Any
import time
import datetime
from ..logger import log
import pandas as pd
# 使用LRU缓存减少数据库查询
from functools import lru_cache


class GlobalObject(object):
    """
    全局变量对象
    如果g中的某个变量不想被序列化, 可以让变量以 '__' 开头, 在序列化时会被忽略

    要在Python中通过pickle序列化自定义类，需要满足以下两个条件：

    1. 自定义类必须实现__getstate__()和__setstate__()方法。
        1) getstate() 方法应该返回一个包含对象状态的字典。这个字典将是 pickle 用于序列化对象的内容。
        2) setstate() 方法接收一个字典作为参数，并使用它来恢复对象状态。
    2. 自定义类必须是全局可访问的。

    """

    def __getstate__(self):
        return {name: getattr(self, name) for name in dir(self) if not name.startswith("__")}

    def __setstate__(self, state):
        # reset g
        for k, v in state.items():
            setattr(self, k, v)


@assert_auth
def get_factor(symbol: Union[None, str, List[str]] = None,
               factor: Union[None, str, List[str]] = None,
               expr: str = None,
               timeframe: str = '1d',
               trade_date: str = None,
               start_date: str = None,
               end_date: str = None,
               datetime: str = None,
               start_datetime: str = None,
               end_datetime: str = None,
               index: Union[None, str, List[str]] = None,
               size: int = None,
               limit: Optional[int] = None,
               dividend_type: str = 'none',
               expect_df: bool = True):
    """
    查询因子数据.

    :param symbol: 股票代码，支持字符串或者字符串数组.
    :param factor: 因子名称, 支持字符串或者字符串数组.
    :param expr: 表达式字符串，根据表达式缩小筛选范围，例如："chg >= 8 AND (open > 10 AND close <= 20)"
    :param timeframe: 时间窗口，支持1d（日线）、1m（1分钟）、5m（5分钟）、15m（15分钟）、1h（1小时），默认为1d
    :param trade_date: 限定交易日
    :param start_date: 开始交易日
    :param end_date: 结束交易日
    :param datetime: 限定日期时间，格式：YYYY-MM-DD HH:mm:ss，例如：'2025-11-21 14:30:00'
    :param start_datetime: 开始日期时间，格式：YYYY-MM-DD HH:mm:ss
    :param end_datetime: 结束日期时间，格式：YYYY-MM-DD HH:mm:ss
    :param index: 指数列表，仅加载指数成分股。
    :param dividend_type: 复权选项(对股票/基金的价格字段生效)
                'front'
                : 前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param size: 数量, 返回的结果集的行数. 等价于返回分页的第一页，page_size = size
    :param limit: 分组限制数量，在排序后按照symbol字段进行分组，每个分组最多返回limit条记录
    :param expect_df: 是否以DataFrame返回
    :return:
    """
    return PQDataClient.instance().get_factor(**locals())


@assert_auth
def get_history(symbol: Union[None, str, List[str]] = None,
                field: str = "close",
                expr: str = None,
                timeframe: str = '1d',
                trade_date: str = None,
                start_date: str = None,
                end_date: str = None,
                datetime: str = None,
                start_datetime: str = None,
                end_datetime: str = None,
                index: Union[None, str, List[str]] = None,
                limit: int = None,
                dividend_type: str = 'none'):
    """
    获取历史数据，可查询多个标的单个数据字段，返回数据格式为 DataFrame
    返回的DataFrame格式：index为时间（trade_date或datetime），columns为每个股票代码

    :param symbol: 股票代码，支持字符串或者字符串数组.
    :param field: 要获取的数据字段
    :param expr: 表达式字符串，根据表达式缩小筛选范围，例如："chg >= 8 AND (open > 10 AND close <= 20)"
    :param timeframe: 时间窗口，支持1d（日线）、1m（1分钟）、5m（5分钟）、15m（15分钟）、1h（1小时），默认为1d
    :param trade_date: 限定交易日
    :param start_date: 开始交易日
    :param end_date: 结束交易日
    :param datetime: 限定日期时间，格式：YYYY-MM-DD HH:mm:ss，例如：'2025-11-21 14:30:00'
    :param start_datetime: 开始日期时间，格式：YYYY-MM-DD HH:mm:ss
    :param end_datetime: 结束日期时间，格式：YYYY-MM-DD HH:mm:ss
    :param index: 指数列表，仅加载指数成分股。
    :param dividend_type: 复权选项(对股票/基金的价格字段生效)
                'front'
                : 前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param limit: 分组限制数量，在排序后按照symbol字段进行分组，每个分组最多返回limit条记录
    :return: DataFrame，index为时间（trade_date或datetime），columns为每个股票代码
    """
    return PQDataClient.instance().get_history(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_trade_cal(start_date: str = '2018-01-01'):
    """
    获取交易日历，默认从2018-01-01开始
    :return:
    """
    return PQDataClient.instance().get_trade_cal(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_previous_trading_date(date: str, lookback_days: int = 1):
    """
    对于给定的日期，返回前第n天
    :param date:
    :param lookback_days: 前第n天，默认前1天
    :return:
    """
    return PQDataClient.instance().get_previous_trading_date(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_next_trading_date(date: str, lookahead_days: int = 1):
    """
    对于给定的日期，返回后第n天
    :param date:
    :param lookahead_days: 后第n天，默认前1天
    :return:
    """
    return PQDataClient.instance().get_next_trading_date(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_near_trade_date(trade_date: str, max_retries=5, retry_delay=2):
    """
    检查trade_date是否为交易日，否则，获取上一个交易日。
    如果返回值不是字符串类型，则重试，最多重试max_retries次，每次间隔retry_delay秒。

    :param trade_date: 输入的交易日期
    :param max_retries: 最大重试次数
    :param retry_delay: 每次重试之间的延迟时间（秒）
    :return: 最近的交易日（字符串类型）
    """
    retries = 0
    while retries < max_retries:
        res = PQDataClient.instance().get_near_trade_date(trade_date=trade_date)
        if isinstance(res, str):
            return res
        else:
            log.warning(f"返回值不是字符串类型，{res}，重试 {retries + 1}/{max_retries}...")
            retries += 1
            time.sleep(retry_delay)

            # 如果达到最大重试次数仍然失败，可以抛出一个异常或返回一个默认值
    raise ValueError("无法获取有效的交易日期，已达到最大重试次数")


@assert_auth
@lru_cache(maxsize=1024)
def get_open_trade_dates(start_date: str, end_date: str = None):
    """
    通过开始日期和结束日期，取得交易日。

    :param start_date:
    :param end_date:
    :return: df, 只有一个Column：trade_date
    """
    return PQDataClient.instance().get_open_trade_dates(**locals())


@assert_auth
def get_index_members_lst(index_lst: list, trade_date: str = None):
    """
    获取指数成分股列表

    :param trade_date: 截止trade_date最新一期的指数成分股，为None则返回历史出现过的所有成分股
    :param index_lst: 指数列表
    :return:
    """
    return PQDataClient.instance().get_index_members_lst(**locals())


@assert_auth
def get_concept_members(code: str = None, code_list: list = None, name: str = None, keyword: str = None):
    """
    获取概念成分股

    :param code: 概念编码
    :param code_list: 概念编码列表
    :param name: 概念名称
    :param keyword: 概念名称关键字
    :return: list 成分股列表
    """
    return PQDataClient.instance().get_concept_members(**locals())


@assert_auth
def get_concept(code: str = None,
                code_list: list = None,
                name: str = None,
                keyword: str = None,
                exchange: str = 'A',
                type: str = 'N') -> dict:
    """
    获取概念列表
    :param code: 概念编码
    :param code_list: 概念编码列表
    :param name: 概念名称
    :param keyword: 概念名称关键字
    :param exchange: 交易所
    :param type: 	N概念指数, S特色指数
    :return: dict {'864006.TI': {'name': '固态电池', 'count': 1}, '886032.TI': {'name': '固态电池', 'count': 62}}
    """
    return PQDataClient.instance().get_concept(**locals())


@assert_auth
def get_hot_concept(count: int,
                    trade_date: str,
                    code: str = None,
                    code_list: list = None,
                    name: str = None,
                    keyword: str = None,
                    exchange: str = 'A',
                    type: str = 'N',
                    order_by: str = 'pct_change desc'):
    """
    获取热门概念编号列表，默认以涨跌幅倒序排列
    :param count:
    :param trade_date:
    :param code:
    :param code_list:
    :param name:
    :param keyword:
    :param exchange:
    :param type:
    :param order_by:
    :return:
    """
    return PQDataClient.instance().get_hot_concept(**locals())


@assert_auth
def get_news_content(start_date: str, end_date: str, sec_code_list: list = None):
    return PQDataClient.instance().get_news_content(**locals())


@assert_auth
def get_stock_info(symbols: list,
                   fields=None,
                   trade_date: str = None,
                   dividend_type: str = "none"):
    """
    获取股票基础信息

    :param symbols: 指定股票列表
    :param fields: 可选，['symbol', 'datetime', 'name', 'pre_close', 'up_limit', 'down_limit', 'suspend_status']
    :param trade_date: 指定交易日, 如果为None，或者为当天，或者为最近一个交易日，总是从StockInfoManager获取最新的值, 否则从数据库获取
    :param dividend_type: 对于历史数据，复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :return: df:
        symbol	股票代码
        datetime 数据时间
        name 	合约名称
        pre_close 	前收盘价格
        up_limit	当日涨停价
        down_limit	当日跌停价
        suspend_status   停复牌状态：<=0 正常，-1 复牌，>0 停牌, >=1 停牌天数
    """
    return PQDataClient.instance().get_stock_info(**locals())


@assert_auth
def get_suspend_info(trade_date: str, fields=None, stock_lst: list = None, suspend_type: str = 'S'):
    """
    获取股票在某日的停复牌状态

    :param trade_date:
    :param fields:
    :param stock_lst:
    :param suspend_type: 停牌：S，复牌：R
    :return:
    """
    return PQDataClient.instance().get_suspend_info(**locals())


@assert_auth
def get_stock_name_his(sec_code: str, trade_date: str):
    """
    获取股票代码的历史名称
    :param trade_date:
    :param sec_code:
    :return: {'sec_code': '000001.SZ', 'name': '平安银行', 'start_date': '2012-08-02', 'end_date': '2099-12-30'}
    """
    return PQDataClient.instance().get_stock_name_his(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def is_open_trade_date(date: str):
    """检查是否为交易日"""
    return PQDataClient.instance().is_open_trade_date(**locals())


@assert_auth
def get_last_ticks(symbols: List[str], fields: Optional[List[str]] = None) -> pd.DataFrame:
    """
    批量获取多个symbols的最新的tick数据

    Args:
        symbols: 股票代码列表，每个元素格式为 "代码.交易所"，如 ["001316.SZ", "000001.SZ"]
        fields: 指定返回的字段列表，默认为None时返回所有字段：
                    ['symbol', 'datetime', 'open', 'high', 'low', 'last_price',
                     'pre_close', 'volume', 'amount', 'asks', 'bids']
                    如果指定了fields，symbol字段会自动包含在内

    Returns:
        pd.DataFrame: 包含所有symbols的tick数据的DataFrame，每行对应一个symbol。列包括：
            - symbol: 股票代码
            - datetime: tick时间字符串，格式为 "%Y-%m-%d %H:%M:%S"
            - open: 当日开盘价
            - high: 当日最高价
            - low: 当日最低价
            - last_price: 当日最新价格
            - pre_close: 昨日收盘价
            - volume: 当日成交量，单位：手
            - amount: 当日成交额
            - asks: 卖盘数据（可选）
            - bids: 买盘数据（可选）

        注意：如果某个symbol的数据不存在，则对应行的值为None。如果symbols为空列表，返回空的DataFrame。
    """
    return PQDataClient.instance().get_last_ticks(**locals())


@assert_auth
def get_plate_data(trade_date: str = None, end_time: str = "15:00", limit: int = 3):
    """
    获取板块列表

    :param trade_date: 指定交易日的板块列表
    :param end_time: 指定板块排名的时间节点，从09:25开始到15:30结束，每个间隔5分钟
    :param limit: 按照板块强度倒序排名的板块数量
    :return:
    """
    return PQDataClient.instance().get_plate_data(**locals())


@assert_auth
def get_hot_plate(trade_date: str = None, n_days: int = 5, top_n: int = 5, hot_n: int = 5, exclude_list: list = None):
    """
    获取最近n天 上榜(每天进入强度前n)天数最多的板块
    :param trade_date: 选股日期, 默认为前一个交易日
    :param n_days: 从最近多少天里筛选热门板块，默认 5
    :param top_n:  每天热度top n，默认top 5
    :param hot_n:  最终选出 最近n_days 天 热门的前n个板块
    :param exclude_list: 排除的板块清单，比如 ST板块，中报增长板块等
    :return: DataFrame
    """
    return PQDataClient.instance().get_hot_plate(**locals())


@assert_auth
def get_plate_members_lst(plate_code_list: list, trade_date: str = None):
    """
    获取板块的成分股
    :param plate_code_list:
    :param trade_date:
    :return:
    """
    return PQDataClient.instance().get_plate_members_lst(**locals())


@assert_auth
def get_member_plates(symbol: str, trade_date: str = None) -> pd.DataFrame:
    """
    获取股票代码所属的板块, 一个股票可能属于多个板块。除了获取板块外，额外提供板块强度，并且按照板块强度倒序排列。
    :param symbol: 股票代码
    :param trade_date: 交易日，不同交易下的板块可能不同
    :return: DataFrame， 字段包括 板块代码，板块名称，板块强度
           plate_code plate_name  intensity
    0      801660         通信       2306
    1      801250       并购重组       1834
    2      801218       华为概念       1610
    3      801328       消费电子        640
    4      801001         芯片        456
    5      801878       端侧AI        296
    6      801408       智能家居        246
    7      801519        汽车类        227
    8      801857      PPP概念        136
    9      801033       国有企业         44
    10     801382     分拆上市预期         38
    """
    return PQDataClient.instance().get_member_plates(**locals())


@assert_auth
def get_stock_name(sec_code: str, trade_date: str = None):
    """
    获取股票代码的最新名称

    :param sec_code:
    :param trade_date:
        None：默认为当天，如果当天不是交易日，则获取上一个交易日。
        'YYYY-mm-dd'：具体日期的最新股票名称
    :return: 股票名称
    """
    return PQDataClient.instance().get_stock_name(**locals())


@assert_auth
def get_stock_price(sec_code: str,
                    trade_date: str = None,
                    end_time: str = None,
                    dividend_type: str = "front"):
    """
    获取最新的股票价格

    :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param trade_date: 指定交易日, 格式: 2024-07-15
    :param end_time: 如果trade_date不是系统日期当日，可以指定历史数据的具体分钟，格式：09:30
    :param sec_code:
    :return:
    """
    return PQDataClient.instance().get_stock_price(**locals())


@assert_auth
def get_price_limit(sec_code: str,
                    trade_date: str = None,
                    dividend_type: str = "front"):
    """
    股票代码涨跌停价格
    假设：
    - 600xxx, 601xxx, 603xxx：上海主板，涨跌停限制10%
    - 000xxx：深圳主板，涨跌停限制10%
    - 002xxx：深圳中小板，涨跌停限制10%
    - 300xxx：深圳创业板，涨跌停限制20%
    - 688xxx：上海科创板，涨跌停限制20%

    :param dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
    :param sec_code:
    :param trade_date: 指定日期的涨跌停价格
    :return: (昨日收盘价格, 今日涨停价, 今日跌停价)
    """
    return PQDataClient.instance().get_price_limit(**locals())


@assert_auth
def get_auction_data(symbol: str,
                     trade_date: str = None,
                     timeframe: str = '1m',
                     fields: list = None,
                     size: int = None):
    """
    # 获取股票的集合竞价数据。集合竞价的规则如下：
    - 开盘竞价时间是9点15分到9点25分
    - 9:15到9:20是自由买卖阶段，可以下单，也可以撤单
    - 9:20到9点25下单后，这段时间可以下单但是禁止撤单


    :param symbol: 股票代码
    :param timeframe: 时间窗口，默认为'1m'（1分钟）
    :param trade_date: 指定单个交易日，与其他日期参数互斥
    :param fields: 获取集合竞价是的数据字段，支持的字段为：
        ['open', # 单位时间的开始价格
         'high', # 单位时间的最高价
         'low',  # 单位时间的最低价
         'close', # 单位时间的最后价格
         'pre_close', # 昨日收盘价
         'volume', # 单位时间的成交数量
         'amount' # 单位时间的成交金额
         ]
    :param size: 限制返回的记录数。当未指定trade_date时，如果limit为None，则默认最多返回100条记录
    :return: DataFrame，包含指定时间范围内每个交易日09:15:00到09:25:00的集合竞价数据
    """
    return PQDataClient.instance().get_auction_data(**locals())


@assert_auth
def get_abnormal_stocks(fields: list = None,
                        symbols: list = None,
                        start_date: str = None,
                        end_date: str = None,
                        abnormal_type: int = None):
    """
    获取严重异动的股票，即其偏离值异动的股票
    :param fields: 获取数据的字段，默认：sec_code, 支持 sec_code, trade_date, abnormal_type
    :param symbols: 指定的股票是否发生过异动
    :param start_date: 异动日期范围, 如果未指定起始日期，默认6个月前
    :param end_date: 异动日期范围
    :param abnormal_type: 股票偏离值异动类型
    :return:
    """
    return PQDataClient.instance().get_abnormal_stocks(**locals())


@assert_auth
def get_suspend_status(sec_code: str, trade_date: str = None):
    """
    合约停牌状态
    :param sec_code:
    :param trade_date:
    :return: int
            <=0 正常，-1 复牌，>0 停牌, >=1 停牌天数
    """
    return PQDataClient.instance().get_suspend_status(**locals())


@assert_auth
def get_prompt_query(query: str,
                     query_type: str = 'stock',
                     page_num: int = None,
                     page_size: int = None,
                     loop: Union[bool, int] = False):
    """
    通过Prompt Query的方式进行选股。
    举例：2024-10-16,DDE大单净量>0.25, 非科创板,非创业板,非北交所,非ST
    将获取相关的股票列表：
        ['002793.SZ', '000838.SZ', '600837.SH', '000972.SZ', '600889.SH', ...]

    :param query: 通过文本的方式进行选股
    :param query_type: 支持: stock: 股票，fund: 基金
    :param page_num: 可选，查询的页号，默认为1
    :param page_size: 可选，每页行数, 最小50， 最大100，默认为100
    :param loop: 是否循环分页，返回多页合并数据。默认值为False，可以设置为True或具体数值. 当为数值的时候，1-n的多页数据一起返回
    :return: list, 股票代码列表
    """
    params_dict = {"query": query,
                   "query_type": query_type,
                   "page_size": page_size,
                   }

    if page_num and loop is False:
        params_dict['page_num'] = page_num
        max_retry = 2  # 最多尝试次数
        result_on_except = []  # 如果尝试失败的返回默认结果
        return PQDataClient.instance().get_prompt_query(*(max_retry, result_on_except), **params_dict)

    elif isinstance(loop, bool) and loop is True:  # 分页查询，最终合并结果
        _page_num = 1
        result = []
        while True:
            params_dict['page_num'] = _page_num
            max_retry = 2  # 最多尝试次数
            result_on_except = []  # 如果尝试失败的返回默认结果
            stock_list = PQDataClient.instance().get_prompt_query(*(max_retry, result_on_except), **params_dict)
            result.extend(stock_list)
            _page_num += 1
            if len(stock_list) == 0:
                break
        return result
    elif isinstance(loop, int):  # 返回前x页
        loop = max(1, loop)
        params_dict['loop'] = loop
        return PQDataClient.instance().get_prompt_query(**params_dict)
    else:
        return PQDataClient.instance().get_prompt_query(**params_dict)


@assert_auth
def get_reduce_holdings(start_date: str, end_date: str):
    """
    获取指定日期范围内发布了减持公告的股票代码列表

    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: list，股票代码列表
    """
    return PQDataClient.instance().get_reduce_holdings(**locals())


@assert_auth
def get_board_members(boards: list,
                      status: str = "L",
                      start_date: str = None,
                      end_date: str = None,
                      is_hs: str = None):
    """
    获取板块的成分股

    :param boards: 板块列表
            [
            "sz.zh", # 深市主板
            "sh.zh", # 沪市主板
            "sz.cy", # 创业板
            "sh.kc", # 科创板
            "sz.zx",  # 中小板
            "bj.bj",  # 北交所
            ]
    :param status: 上市状态 L上市 D退市 P暂停上市
    :param start_date: # 上市日期范围
    :param end_date: # 上市日期范围
    :param is_hs: 是否沪深港通标的，N否 H沪股通 S深股通
    :return: list, 股票列表
    """
    return PQDataClient.instance().get_board_members(**locals())


@assert_auth
def get_up_limit_stocks(symbols: list, trade_date: str, lookback_days: int = 1):
    """
    获取连板涨停的股票列表。

    :param symbols: 候选股票代码列表
    :param trade_date: 指定交易日作为判断的起点日期
    :param lookback_days:
            0：昨日未涨停的股票
            >=1: 连板涨停的股票
    :return: list，股票代码列表
    """
    return PQDataClient.instance().get_up_limit_stocks(**locals())


@assert_auth
def get_leading_stocks(trade_date: str = None,
                       keywords: list = None,
                       src_type: str = None,
                       expect_df: bool = False,
                       lookback_days: int = None):
    """
    获取某个交易日下的行业/概念龙头股票代码列表

    :param src_type: 数据来源，支持 'tencent' 或 'THS'，默认 None（查询所有数据源）
    :param expect_df: 是否返回DataFrame，False返回股票列表，True返回DataFrame，默认 False
    :param trade_date: 指定交易日，格式为 'YYYY-MM-DD'，默认取前一交易日
    :param keywords: 行业/概念的关键字列表（如 ['创新药', '军工', '华为']），默认 None（匹配所有）
    :param lookback_days: 回看天数，如果指定，将查询从 trade_date 往前回看 lookback_days 天的所有龙头股票，默认 None（只查询指定交易日）
    :return: 股票列表（expect_df=False）或 DataFrame（expect_df=True）
    """
    return PQDataClient.instance().get_leading_stocks(**locals())


@assert_auth
def get_ohlcv(symbol: str,
              start_date: str = None,
              end_date: str = None,
              timeframe: str = '1d',
              size: int = 100,
              dividend_type: str = 'none'):
    """
    获取股票的OHLCV（开高低收成交量）数据

    该函数能够获取指定股票的历史OHLCV数据，支持多种时间周期。

    Args:
        symbol (str): 股票代码，格式如 '000001.SZ' 或 '600000.SH'
        start_date: 获取数据的开始日期
        end_date: 获取数据的结束日期
        timeframe (str, optional): 时间周期
        size (int, optional): 获取的K线数量，默认为100根
        dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                    'front'
                    : 前复权, 默认是前复权
                    none
                    : 不复权, 返回实际价格
                    'back'
                    : 后复权

    Returns:
        pandas.DataFrame: 包含OHLCV数据的DataFrame，列结构如下：
            - datetime/trade_date: 时间戳（分钟级为datetime格式，日级为trade_date格式）
            - open: 开盘价
            - high: 最高价
            - low: 最低价
            - close: 收盘价
            - volume: 成交量

    Raises:
        ValueError: 当参数无效时抛出异常
        Exception: 当数据获取失败时抛出异常，函数内部会捕获并记录错误日志
    """
    return PQDataClient.instance().get_ohlcv(**locals())


@assert_auth
def get_last_bar(symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
    """
    获取单个标的在某个周期上的最新 BarData

    Args:
        symbol: 股票代码，如 600000.SH
        timeframe: 周期，如 1m/5m/15m/30m/1h/1d

    Returns:
        字典，包含 Bar 数据字段（symbol, datetime, timeframe, open, high, low, close, pre_close, volume, amount）；
        如果 Redis 中不存在对应 key，则返回 None
    """
    return PQDataClient.instance().get_last_bar(**locals())


@assert_auth
def get_last_bars(symbols: List[str], timeframe: str) -> pd.DataFrame:
    """
    批量获取多个标的在同一周期下的最新 BarData

    Args:
        symbols: 股票代码列表
        timeframe: 周期，如 1m/5m/15m/30m/1h/1d

    Returns:
        DataFrame，包含列：symbol, datetime, timeframe, open, high, low, close, pre_close, volume, amount
        如果某个 symbol 的数据不存在，对应的行会缺失或字段为 None
    """
    return PQDataClient.instance().get_last_bars(**locals())


@assert_auth
def get_order_book(symbol: str, level: int = 5) -> Optional[Dict[str, Any]]:
    """
    从Redis中获取订单簿数据（从tick数据中提取）

    Args:
        symbol: 股票代码，如 000001.SZ
        level: 订单簿档位数，默认为5，最多返回指定档位的买卖盘数据

    Returns:
        订单簿数据字典，格式为：
        {
            "symbol": "000001.SZ",
            "datetime": "2024-01-01 09:30:00",
            "bids": [[price, volume], [price, volume], ...],  # 买盘，按价格从高到低，最多level档
            "asks": [[price, volume], [price, volume], ...],  # 卖盘，按价格从低到高，最多level档
        }
        如果不存在则返回None
    """
    return PQDataClient.instance().get_order_book(**locals())


@assert_auth
def get_order_book_his(symbol: str,
                       timeframe: str = '1m',
                       start_datetime: str = None,
                       end_datetime: str = None,
                       level: int = 5,
                       count: int = None,
                       expect_df: bool = True):
    """
    获取股票的订单簿历史数据（买卖盘口数据）

    订单簿数据包含多档买卖价格和数量信息，用于分析市场深度和流动性。
    使用时间窗口聚合，每个窗口内取最新的订单簿数据。

    :param symbol: 股票代码，如 '000001.SZ'
    :param timeframe: 时间窗口，支持 '1m'（1分钟）、'5m'（5分钟）、'15m'（15分钟）等，默认 '1m'
    :param start_datetime: 开始时间，格式：'YYYY-MM-DD HH:mm:SS'，如 '2024-01-01 09:30:00'
    :param end_datetime: 结束时间，格式：'YYYY-MM-DD HH:mm:SS'，如 '2024-01-01 15:00:00'
    :param level: 限制买卖档数，1-5档，默认5档（level=1只返回买卖1档，level=5返回买卖5档）
    :param count: 限制返回的记录数，可选参数。始终返回最新的数据，当未指定时间区间时默认count为100
    :param expect_df: 返回格式，True返回DataFrame，False返回字典格式
    :return: 当expect_df=True时返回DataFrame，当expect_df=False时返回字典列表

    使用示例：
    # 获取指定时间区间内的数据（5档，5分钟窗口）
    df = get_order_book_his('000001.SZ', '5m', '2024-01-01 09:30:00', '2024-01-01 10:00:00')

    # 只获取买卖1档数据（1分钟窗口）
    df = get_order_book_his('000001.SZ', '1m', '2024-01-01 09:30:00', '2024-01-01 10:00:00', level=1)

    # 限制返回50条最新记录（15分钟窗口）
    df = get_order_book_his('000001.SZ', '15m', '2024-01-01 09:30:00', '2024-01-01 10:00:00', count=50)

    # 获取字典格式的订单簿数据（3档，限制50条最新记录）
    data = get_order_book_his('000001.SZ', '5m', '2024-01-01 09:30:00', '2024-01-01 10:00:00',
                         level=3, count=50, expect_df=False)

    # 未指定时间区间时，默认返回最新的100条记录（按时间升序排列）
    df = get_order_book_his('000001.SZ', '1m')

    # 未指定时间区间时，也可以自定义count，返回最新的数据
    df = get_order_book_his('000001.SZ', '1m', count=200)

    返回的DataFrame包含以下字段：
    - symbol: 股票代码
    - datetime: 时间戳（窗口起始时间）
    - ask1_price~ask{level}_price: 卖1~level价格
    - bid1_price~bid{level}_price: 买1~level价格
    - ask1_volume~ask{level}_volume: 卖1~level数量
    - bid1_volume~bid{level}_volume: 买1~level数量
    - spread: 买卖价差
    - total_bid_volume_5lvl: 5档买盘总量
    - total_ask_volume_5lvl: 5档卖盘总量
    - depth_ratio_5lvl: 5档深度比率

    当expect_df=False时，返回格式：
    [
        {
            'bids': [[price, volume], [price, volume], ...],  # 买盘，按价格从高到低
            'asks': [[price, volume], [price, volume], ...],  # 卖盘，按价格从低到高
            'symbol': '000001.SZ',
            'datetime': '2024-01-01 09:30:00'
        },
        ...
    ]
    """
    return PQDataClient.instance().get_order_book_his(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_support_levels(trade_date: str, symbol: str, lookback: int = 20, sort: str = None) -> list:
    """
    获取支撑位列表

    使用示例：
    # 获取支撑位
    support_levels = get_support_levels(context, "000001.SZ")
    for trade_date, price, strength in support_levels:
        print(f"交易日期: {trade_date}, 价格: {price}, 强度: {strength}")

    参数:
    :param trade_date: 当前日期，以当前日期为起点回看，寻找支撑位和压力位
    :param symbol: 股票代码，如 "000001.SZ"
    :param lookback: 回看的K线数量，默认20根
    :param sort: 排序方式，None(不排序)、'asc'(正序)、'desc'(倒序)，默认None

    返回:
    :return: 支撑位列表，每个元素为(交易日期,价格,强度)的元组，交易日期是支撑位对应的日期
    """
    return PQDataClient.instance().get_support_levels(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def get_resistance_levels(trade_date: str, symbol: str, lookback: int = 20, sort: str = None) -> list:
    """
    获取压力位列表

    使用示例：
    # 获取压力位
    resistance_levels = get_resistance_levels(context, "000001.SZ", sort='desc')
    for trade_date, price, strength in resistance_levels:
        print(f"交易日期: {trade_date}, 价格: {price}, 强度: {strength}")

    参数:
    :param trade_date: 当前日期，以当前日期为起点回看，寻找支撑位和压力位
    :param symbol: 股票代码，如 "000001.SZ"
    :param lookback: 回看的K线数量，默认20根
    :param sort: 排序方式，None(不排序)、'asc'(正序)、'desc'(倒序)，默认None

    返回:
    :return: 压力位列表，每个元素为(交易日期,价格,强度)的元组，交易日期是压力位对应的日期
    """
    return PQDataClient.instance().get_resistance_levels(**locals())


@assert_auth
@lru_cache(maxsize=1024)
def is_trading_volume_up(trade_date: str):
    """
    量能的预测趋势，增量或者缩量
    :param trade_date: 预测量能的交易日
    :return: True 增量，False 缩量
    """
    return PQDataClient.instance().is_trading_volume_up(**locals())


@assert_auth
def get_payload():
    """
    获取当前登录JWT的payload信息
    :return:
    """
    return PQDataClient.instance().get_payload()


@assert_auth
def get_stock_pool(expr: str = None, config: dict = None, id: int = None, ids: list = None) -> list:
    """
    获取股票池成员列表
    :param expr: 表达式字符串，根据表达式获取(最新数据)股票池成员列表，例如："chg >= 8 AND (open > 10 AND close <= 20)"
    :param config: 股票池配置，根据配置获取股票池成员列表
    :param id: 股票池ID，根据股票池ID获取股票池成员列表
    :param ids: 股票池ID列表，根据多个股票池ID获取去重后的股票池成员列表
    :return: 股票池成员列表
    """
    return PQDataClient.instance().get_stock_pool(**locals())


@assert_auth
def get_factor_meta(reverse: bool = False) -> dict:
    """
    获取元数据字典

    Args:
        reverse: 是否返回反向字典，默认为False
            - False: 返回 {factor_id: [factor_field, factor_name, unit]}
            - True: 返回 {factor_field: [factor_id, factor_name, unit]}

    Returns:
        Dict: 元数据字典
            - reverse=False: Dict[int, list]，格式为 {factor_id: [factor_field, factor_name, unit]}
            - reverse=True: Dict[str, list]，格式为 {factor_field: [factor_id, factor_name, unit]}
    """
    return PQDataClient.instance().get_factor_meta(**locals())


@assert_auth
def get_last_tick(symbol: str) -> Optional[Dict[str, Any]]:
    """
    获取单个symbol的最新的tick数据

    Args:
        symbol: 股票代码，格式为 "代码.交易所"，如 "001316.SZ"、"000001.SZ"

    Returns:
        Optional[Dict[str, Any]]: tick数据字典，如果数据不存在则返回None。字典包含以下字段：
            - datetime: tick时间字符串，格式为 "%Y-%m-%d %H:%M:%S"
            - open: 当日开盘价
            - high: 当日最高价
            - low: 当日最低价
            - last_price: 当日最新价格
            - pre_close: 昨日收盘价
            - volume: 当日成交量，单位：手
            - amount: 当日成交额
            - asks: 卖盘数据（可选）
            - bids: 买盘数据（可选）
    """
    return PQDataClient.instance().get_last_tick(**locals())


@assert_auth
def get_last_factor_value(symbol: str, factor_id: int) -> Optional[float]:
    """
    根据symbol和factor_id获取单个因子的值

    Args:
        symbol: 股票代码
        factor_id: 因子ID（整数）

    Returns:
        因子值（float），如果不存在则返回None
    """
    return PQDataClient.instance().get_last_factor_value(**locals())


@assert_auth
def get_last_factor_data(symbols: List[str], factor_ids: List[int]):
    """
    批量从Redis获取因子数据

    Args:
        symbols: 股票代码列表
        factor_ids: 因子ID列表（整数列表）

    Returns:
        DataFrame，列格式为['symbol', 'field_name_1', 'field_name_2', ...]，
        每行对应一个symbol，每列对应一个factor_id，列名为factor_field，值为因子值(val)
        如果某个组合不存在则对应的值为None
    """
    return PQDataClient.instance().get_last_factor_data(**locals())


@assert_auth
def get_dragon_tiger_list(symbols: list = None,
                          fields: list = None,
                          trade_date: str = None,
                          start_date: str = None,
                          end_date: str = None,
                          side: str = None,
                          exalter: str = None):
    """
    获取龙虎榜（Dragon and Tiger List）信息，即机构/营业部买卖金额最大的前5名数据

    :param symbols: 指定的股票代码列表，如 ['000001.SZ', '000002.SZ']
    :param fields: 获取数据的字段列表，默认：['symbol', 'trade_date', 'exalter']
                    支持的字段：trade_date, symbol, exalter, side, buy, buy_rate, sell, sell_rate, net_buy, reason
    :param trade_date: 指定交易日，格式：'YYYY-MM-DD'，与start_date/end_date互斥
    :param start_date: 开始日期，格式：'YYYY-MM-DD'，与trade_date互斥
    :param end_date: 结束日期，格式：'YYYY-MM-DD'，与trade_date互斥
    :param side: 买卖类型，'buy'表示买入席位金额最大的前5名，'sell'表示卖出席位金额最大的前5名
    :param exalter: 营业部名称，支持模糊匹配（使用LIKE查询）
    :return: DataFrame，包含龙虎榜数据
              symbol  trade_date                    exalter
        0  603709.SH  2025-12-11       信达证券股份有限公司温州瓯江路证券营业部
        1  603709.SH  2025-12-11      华鑫证券有限责任公司上海红宝石路证券营业部
        2  603709.SH  2025-12-11            华福证券有限责任公司浙江分公司
        3  603709.SH  2025-12-11       华鑫证券有限责任公司深圳益田路证券营业部
        4  603709.SH  2025-12-11  摩根大通证券(中国)有限公司上海银城中路证券营业部
        5  603709.SH  2025-12-11       华鑫证券有限责任公司上海源深路证券营业部
        6  603709.SH  2025-12-11       华鑫证券有限责任公司西安锦业路证券营业部
    """
    return PQDataClient.instance().get_dragon_tiger_list(**locals())


# ---------------------------------------------------------
# 外部可以访问的列表
# ---------------------------------------------------------
__all__ = ["GlobalObject", "is_open_trade_date", "is_trading_volume_up"]
__all__.extend([name for name in globals().keys() if name.startswith("get")])
