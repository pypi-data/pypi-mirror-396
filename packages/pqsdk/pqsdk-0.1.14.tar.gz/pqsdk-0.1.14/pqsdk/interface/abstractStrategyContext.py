from six import with_metaclass
import abc
from typing import Callable, Union, List
from .abstractPosition import AbstractPosition
from .abstractInstrument import AbstractInstrument
import datetime
import pandas as pd


class AbstractStrategyContext(with_metaclass(abc.ABCMeta)):
    """
    策略上下文的抽象接口类。
    """

    @abc.abstractmethod
    def plot_line(self, sec_code: str, name: str, value: float, desc=None):
        """
        画曲线
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def plot_bar(self, sec_code: str, name: str, value: float, desc=None):
        """
        画柱状图
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_monthly(self, func: Callable, monthday: int, time_str: str) -> None:
        """
        按月运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param monthday: 每月的第几个交易日, day (1-31)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_weekly(self, func: Callable, weekday: int, time_str: str) -> None:
        """
        按周运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param weekday: 每周的第几个交易日, 1 = monday, ... 7 = sunday
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_periodically(self,
                         func: Callable,
                         days: int,
                         time_str: str,
                         start_date: str = None,
                         end_date: str = None) -> None:
        """
        按调仓周期运行，如果遇到调仓日为非交易日，则顺延到下一个交易日。

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param days : 间隔天数执行，start_date为第一次执行日期
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        :param start_date: 开始日期，默认为回测开始日期
        :param end_date: 结束日期, 默认为回测结束日期
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_daily(self, func: Callable, time_str: str) -> None:
        """
        每天内何时运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_minutely(self, func: Callable, time_str: str, minutes: int = 1) -> None:
        """
        每天内何时开始，间隔n分钟执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param minutes: 间隔执行的分钟数
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run_secondly(self, func: Callable, time_str: str, seconds: int = 1) -> None:
        """
        每天内何时开始，间隔n秒执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param seconds: 间隔执行的秒数
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cancel(self, order, force: bool = False):
        """
        取消订单委托
        :param force: 强制交易
        :param order: 回测中为order对象，实盘中为order_id
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def close(self, stock_code: str, force: bool = False):
        """
        以最新价平仓股票代码, 默认平仓数量为可用数量
        :param force: 强制交易
        :param stock_code: 需要平仓的股票代码
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_current_data(self):
        """
        获取当前单位时间（当天/当前分钟）的涨跌停价, 是否停牌，当天的开盘价等

        :return: 一个dict, 其中 key 是股票代码, value 是拥有如下属性的对象, 返回的结果只在当天有效:
                last_price : 最新价
                high_limit: 涨停价
                low_limit: 跌停价
                paused: 是否停止或者暂停了交易, 当停牌、未上市或者退市后返回 True
                is_st: 是否是 ST(包括ST, *ST)，是则返回 True，否则返回 False
                day_open: 当天开盘价
                name: 股票现在的名称, 可以用这个来判断股票当天是否是 ST, *ST, 是否快要退市
                industry_code: 股票现在所属行业代码
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_position(self, stock_code) -> AbstractPosition:
        """
        获取已经登录账号的股票持仓，返回个股持仓字典

        :param stock_code:
        :return: {'volume': 72000, 'can_use_volume': 0, 'open_price': 10.8, 'market_value': 1020240.0}
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_value(self,
                           stock_code: str,
                           target: float = 0.0,
                           price: float = None,
                           force: bool = False):
        """
        Place an order to rebalance a position to have final value of
        ``target``

        The current ``value`` is taken into account as the start point to
        achieve ``target``

          - If no ``target`` then close postion on data
          - If ``target`` > ``value`` then buy on data
          - If ``target`` < ``value`` then sell on data

        It returns either:

          - The generated order

          or

          - ``None`` if no order has been issued

        :param force: 强制交易
        :param stock_code: 目标持仓股票
        :param target: 目标持仓市值
        :param price:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_percent(self,
                             stock_code: str,
                             target: float = 0.0,
                             force: bool = False):
        """
        基于order_target_value（），按照总资产的百分比委托下单

        :param force: 强制交易
        :param stock_code:目标持仓股票
        :param target: 目标持仓比例
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_volume(self,
                            stock_code: str,
                            target: float = 0.0,
                            force: bool = False):
        """
        基于order_target_value()，按照个股的数量目标数量下单。注意，可能存在账户资金不足的情况。

        :param force: 强制交易
        :param stock_code: 目标持仓股票
        :param target: 目标持仓数量
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def constant(self):
        """
        上下文的系统常量
        :return:
        """
        raise NotImplementedError

    # @property
    # @abc.abstractmethod
    # def planned_trade_dates(self) -> list:
    #     """
    #     获取调仓交易日列表。
    #     :return:
    #     """
    #     raise NotImplementedError

    @property
    @abc.abstractmethod
    def previous_trade_date(self) -> datetime.date:
        """
        当前bar对应的前一个交易日
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parameters(self) -> dict:
        """
        执行策略的参数字典
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def stock_pool(self):
        """
        股票池
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def commission(self):
        """
        佣金费率
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def strategy_name(self):
        """
        策略名称
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def unit(self):
        """
        unit: 单位时间长度，支持1d、1m，默认为1d
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def dividend_type(self):
        """
        dividend_type: 复权选项(对股票/基金的价格字段、成交量字段及factor字段生效)
                'front'
                : 前复权, 默认是前复权
                none
                : 不复权, 返回实际价格
                'back'
                : 后复权
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def current_dt(self) -> datetime.datetime:
        """
        当前bar对应的日期/时间, format: %Y-%m-%d %H:%M:%S
        :return:
        """
        raise NotImplementedError

    # @property
    # @abc.abstractmethod
    # def next_trade_datetime(self):
    #     """
    #     当前bar对应的下一个日期/时间, format: %Y-%m-%d %H:%M:%S
    #     :return:
    #     """
    #     raise NotImplementedError

    @abc.abstractmethod
    def buy(self,
            stock_code: str,
            volume: int,
            price_type: int,
            price: float,
            force: bool = False):
        """
        证券买入委托
        Returns:
          - 委托的order_id
        """
        raise NotImplementedError

    @abc.abstractmethod
    def sell(self,
             stock_code: str,
             volume: int,
             price_type: int,
             price: float,
             force: bool = False):
        """
        证券卖出委托
        Returns:
          - 委托的order_id
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def portfolio(self):
        """
        策略投资组合，可通过该对象获取当前策略账户、持仓等信息
        """
        raise NotImplementedError

    @abc.abstractmethod
    def inout_cash(self, cash: float):
        """
        投资组合转入或转出资金，当日的出入金从当日开始记入成本，用于计算收益，即当日结束计算收益时的本金是包含当日出入金金额的
        :param cash: 可正可负，正为入金，负为出金。
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def run_info(self):
        """
        策略运行信息，包括回测过程中的所有参数。
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_orders(self, trade_date: str = None, is_buy: bool = None, include_canceled: bool = True):
        """
        获取交易日的委托单，返回DataFrame

        :param include_canceled: 是否包括已撤的委托
        :param trade_date:
        :param is_buy:
        :return: DataFrame,
            字段：['order_code', 委托编号
                'sec_code',  股票代码
                'order_time', 委托时间
                'is_buy', 委托买卖方向：买单=1， 卖单=0
                'order_volume',  委托数量
                'order_price']  委托价格
        """
        raise NotImplementedError
