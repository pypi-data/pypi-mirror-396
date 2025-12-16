import datetime
from abc import ABC
from typing import Callable, Union, List
import pandas as pd
from pqsdk.interface import AbstractStrategyContext, AbstractInstrument, AbstractPosition, Constant
from pqsdk.utils.timer_factory import TimerFactory
from .portfolio import Portfolio
from .position import Position
from .order import Order
from pqsdk import log, pqconstant
from pqsdk.api import get_previous_trading_date, get_factor, get_stock_info
from .run_info import RunInfo


class StrategyContext(AbstractStrategyContext, ABC):

    def __init__(self, kwargs: dict, timer_factory: TimerFactory):
        # 自定义定时器
        self.__tf = timer_factory
        self.__constant = Constant()  # 初始化常量
        # 策略执行信息
        self.__run_info = RunInfo(kwargs=kwargs, context=self)
        # 回测的当前日期，每日set_dt重置
        self.__dt = None
        # 回测当前日期的Benchmark收益率
        self.__benchmark_value = None
        self.__unit = kwargs.get('unit', '1d')  # 行情周期
        self.__parameters = kwargs.get('parameters')
        self.__dividend_type = kwargs.get('dividend_type', 'back')
        self.__strategy_name = kwargs.get('strategy_name', None)
        self.__commission = kwargs.get('commission', 0.0)  # 佣金费率
        self.__index = kwargs.get('index', [])
        self.__stock_pool = kwargs.get('stock_pool', [])

        # 初始化Portfolio
        self._portfolio = Portfolio(self)

        # 初始化委托编号
        self.order_id = 0

        # 历史委托列表, 从notify_order()函数收集委托数据，回测结束后写入数据库
        self.orders = []

        """
        回测过程中画出曲线
        self.plot_data = {"000001.SZ": {"startExitPrice": {"type": "line", "xAxis": [], "yAxis": [], "desc": ""}}}
        """
        self.plot_data = dict()

        """
        记录投资组合的转入或转出资金历史
        self.inout_cash_his = [{"datetime": self.current_dt: "cash": cash}]
        """
        self.inout_cash_his = []

    def notify_order(self, order):
        """
        新创建委托的通知
        :param order: 委托的对象
        :return:
        """
        order_dict = {"order_id": order.order_id,
                      "sec_code": order.security,
                      "volume": order.volume,
                      "price": order.price,
                      "is_buy": order.is_buy,
                      "avg_cost": order.avg_cost,
                      "comm": order.commission,
                      "add_time": order.add_time,
                      "trade_date": order.add_time.strftime('%Y-%m-%d')}
        self.orders.append(order_dict)
        # log.debug(f"order: {order_dict}")

    def plot_line(self, sec_code: str, name: str, value: float, desc=None):
        """
        画曲线
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        self.__plot_chart(chart_type='line', sec_code=sec_code, name=name, value=value, desc=desc)

    def plot_bar(self, sec_code: str, name: str, value: float, desc=None):
        """
        画柱状图
        :param sec_code:
        :param name:
        :param value:
        :param desc:
        :return:
        """
        self.__plot_chart(chart_type='bar', sec_code=sec_code, name=name, value=value, desc=desc)

    def __plot_chart(self, chart_type: str, sec_code: str, name: str, value: float, desc=None):
        """
        画图表
        :param chart_type: chart类型：line， bar
        :param sec_code: 股票代码
        :param name: 曲线名称
        :param value: 曲线yAxis的值
        :param desc: value的描述
        :return:
        """
        if self.unit in ['1d']:
            dt = self.current_dt.strftime('%Y-%m-%d')
        else:
            dt = self.current_dt.strftime('%Y-%m-%d %H:%M')
        if sec_code not in self.plot_data:
            self.plot_data[sec_code] = {name: {"type": chart_type,
                                               "xAxis": [dt],
                                               "yAxis": [round(value, 2)],
                                               "desc": [desc]}}
        elif name not in self.plot_data[sec_code]:
            self.plot_data[sec_code][name] = {"type": chart_type,
                                              "xAxis": [dt],
                                              "yAxis": [round(value, 2)],
                                              "desc": [desc]}
        else:
            self.plot_data[sec_code][name]["xAxis"].append(dt)
            self.plot_data[sec_code][name]["yAxis"].append(round(value, 2))
            self.plot_data[sec_code][name]["desc"].append(desc)

    def run_monthly(self, func: Callable, monthday: int, time_str: str) -> None:
        """
        按月运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param monthday: 每月的第几个交易日
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        """

        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, monthdays=[monthday],
                            monthcarry=True)

    def run_weekly(self, func: Callable, weekday: int, time_str: str) -> None:
        """
        按周运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param weekday: 每周的第几个交易日, 1 = monday, ... 7 = sunday
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, weekdays=[weekday], weekcarry=True)

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
        if start_date is None:
            start_date = self.run_info.start_date
        if end_date is None:
            end_date = self.run_info.end_date

        # 将字符串日期转换为datetime对象
        start_date_ = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date_ = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        # 初始化日期列表
        dates = []
        # 当当前日期小于或等于结束日期时，将其添加到列表中，并向前移动interval_days天
        current_date = start_date_
        while current_date <= end_date_:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=days)

        self.__tf.add_timer(callback=func,
                            kwargs={"context": self},
                            when=time_str,
                            dates=dates,
                            datecarry=True)

    def run_daily(self, func: Callable, time_str: str) -> None:
        """
        每天内何时运行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；在实盘中才生效
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str)

    def run_minutely(self, func: Callable, time_str: str, minutes: int = 1) -> None:
        """
        每天内何时开始，间隔n分钟执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param minutes: 间隔执行的分钟数
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, minutes=minutes)

    def run_secondly(self, func: Callable, time_str: str, seconds: int = 1) -> None:
        """
        每天内何时开始，间隔n秒执行

        :param func: 一个自定义的函数, 此函数必须接受context参数;例如自定义函数名market_open(context)
        :param time_str: 具体执行时间,一个字符串格式的时间, 24小时内的任意时间，例如"10:00", "01:00"；
        :param seconds: 间隔执行的秒数
        """
        self.__tf.add_timer(callback=func, kwargs={"context": self}, when=time_str, seconds=seconds)

    def cancel(self, order, force: bool = False):
        pass

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
        return self.current_data_dict

    def get_position(self, stock_code) -> AbstractPosition:
        positions = self.portfolio.positions
        if stock_code in positions:
            return positions[stock_code]
        else:
            # 返回一个空的持仓对象
            return Position(stock_code=stock_code, volume=0, price=0, init_time=datetime.datetime.now(), context=self)

    @property
    def constant(self):
        return self.__constant

    @property
    def commission(self):
        """
        佣金费率
        :return:
        """
        return self.__commission

    @property
    def previous_trade_date(self) -> datetime.date:
        pre_trade_date_str = get_previous_trading_date(self.current_dt.strftime('%Y-%m-%d'))
        return datetime.datetime.strptime(pre_trade_date_str, '%Y-%m-%d').date()

    @property
    def run_info(self):
        return self.__run_info

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
        df = pd.DataFrame(self.orders)
        df.rename(columns={"order_id": "order_code",
                           "add_time": "order_time",
                           "volume": "order_volume",
                           "price": "order_price"}, inplace=True)

        if not df.empty and trade_date is not None:
            df = df[df['trade_date'] == trade_date]

        if not df.empty:
            if is_buy is not None:
                df = df[df['is_buy'] == is_buy]

            df['is_buy'] = df['is_buy'].apply(lambda x: 1 if True else 0)

            # 与实盘保持输出一致
            df = df[['order_code', 'sec_code', 'order_time', 'is_buy', 'order_volume', 'order_price']]
        return df

    def set_benchmark_value(self, value: float):
        """
        设置回测过程中当前日期的benchmark的收益率
        :param value:
        :return:
        """
        self.__benchmark_value = value

    @property
    def benchmark_value(self):
        """
        当前日期的benchmark close价格
        :return:
        """
        return self.__benchmark_value

    def set_dt(self, dt):
        self.__dt = dt

    @classmethod
    def __calculate_size(cls, price, cash):
        """
        返回指定价格和现金的股数，需要考虑一手为100股的情况。

        :param price:
        :param cash:
        :return:
        """
        return int(cash // price // 100) * 100

    def order_target_value(self, stock_code: str, target: float = 0.0, price: float = None, force: bool = False):
        # 获取价格
        if price is None:
            # trade_date = self.current_dt.strftime('%Y-%m-%d')
            if self.unit in ['1d']:
                trade_date = self.current_dt.strftime('%Y-%m-%d')
                trade_datetime = None
            else:
                trade_date = None
                trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
            # price_df = get_history(count=1,
            #                        end_date=trade_date,
            #                        end_datetime=trade_datetime,
            #                        unit=self.unit,
            #                        field='close',
            #                        security_list=[stock_code],
            #                        dividend_type=self.dividend_type,
            #                        expect_df=True)

            price_df = get_factor(trade_date=trade_date,
                                  start_datetime=trade_datetime,
                                  end_datetime=trade_datetime,
                                  timeframe=self.unit,
                                  factor='close',
                                  symbol=stock_code,
                                  dividend_type=self.dividend_type,
                                  expect_df=True)

            if price_df.empty:
                log.warning(f"股票停牌，取消买入: stock_code={stock_code}, trade_date={trade_date}")
                return
            else:
                price = price_df.iloc[0, 0]

        position: Position = self.portfolio.positions.get(stock_code, None)
        if position is None:
            market_value = 0.0
        else:
            market_value = position.volume * price

        if target > market_value:  # Buy
            size = self.__calculate_size(price=price, cash=target - market_value)
            if size < 100:
                content = f"策略名称={self.strategy_name}, 类型=Buy, 股票代码={stock_code}, " \
                          f"目标市值={target}, 持仓市值={market_value}, " \
                          f"委托价格={round(price, 2)},交易股数不足100股，放弃交易"
                log.warning(content)
                return None  # 未满足交易条件
            else:
                return self.buy(stock_code=stock_code,
                                volume=size,
                                price_type=pqconstant.FIX_PRICE,
                                price=price,
                                force=force)

        elif target < market_value:  # Sell
            # 计算可交易股数
            if int(target) == 0:  # 平仓
                size = position.can_use_volume
            else:
                size = self.__calculate_size(price=price, cash=market_value - target)

            if size < 100:
                content = f"策略名称={self.strategy_name}, 类型=Sell, 股票代码={stock_code}, " \
                          f"目标市值={target}, 持仓市值={market_value}, 持仓可用数量={position.can_use_volume}，" \
                          f"委托价格={round(price, 2)},委托数量={size}, 交易股数不足100股，放弃交易"
                log.warning(content)
                return None  # 未满足交易条件
            else:
                if position.can_use_volume >= size >= 100:
                    content = f"策略名称={self.strategy_name}, 类型=Sell, 股票代码={stock_code}, " \
                              f"目标市值={target}, 持仓市值={market_value}, " \
                              f"委托价格={round(price, 2)}, 持仓可用数量={position.can_use_volume}， 委托数量={size}"
                    log.debug(content)
                    return self.sell(stock_code=stock_code,
                                     volume=size,
                                     price_type=pqconstant.FIX_PRICE,
                                     price=price,
                                     force=force)
                else:
                    content = f"策略名称={self.strategy_name}, 类型=Sell, 股票代码={stock_code}, " \
                              f"目标市值={target}, 持仓市值={market_value}, " \
                              f"委托价格={round(price, 2)},持仓数量={position.volume}, 委托数量={size}, " \
                              f"可用数量（{position.can_use_volume}）不足，放弃交易"
                    log.warning(content)
                    return None  # 未满足交易条件
        else:  # target = market_value
            log.warning(f"调仓目标等于持仓数量，放弃交易")
            return None

    def order_target_percent(self, stock_code: str, target: float = 0.0, force: bool = False):
        total_value = self.portfolio.total_value
        target *= total_value
        return self.order_target_value(stock_code=stock_code, target=target, force=force)

    def order_target_volume(self, stock_code: str, target: float = 0.0, force: bool = False):
        # 获取价格
        # trade_date = self.current_dt.strftime('%Y-%m-%d')
        if self.unit in ['1d']:
            trade_date = self.current_dt.strftime('%Y-%m-%d')
            trade_datetime = None
        else:
            trade_date = None
            trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')

        # price_df = get_history(count=1,
        #                        end_date=trade_date,
        #                        end_datetime=trade_datetime,
        #                        unit=self.unit,
        #                        field='close',
        #                        security_list=[stock_code],
        #                        dividend_type=self.dividend_type,
        #                        expect_df=True)

        price_df = get_factor(trade_date=trade_date,
                              start_datetime=trade_datetime,
                              end_datetime=trade_datetime,
                              timeframe=self.unit,
                              factor='close',
                              symbol=[stock_code],
                              dividend_type=self.dividend_type,
                              expect_df=True)

        if price_df.empty:
            log.warning(f"股票停牌，取消买入: stock_code={stock_code}, trade_date={trade_date}")
            return
        else:
            price = price_df.iloc[0, 0]

        estimated_target_value = target * price
        return self.order_target_value(stock_code=stock_code, target=estimated_target_value, force=force)

    def close(self, stock_code: str, force: bool = False):
        """
        以最新价平仓股票代码, 默认平仓数量为可用数量

        :param stock_code:
        :param force:
        :return:
        """
        # 持仓查询
        position: Position = self.portfolio.positions.get(stock_code, None)
        volume = position.can_use_volume

        return self.sell(stock_code=stock_code, volume=volume, force=force)

    @property
    def unit(self):
        """
        unit: 单位时间长度，支持1d、1m，默认为1d
        :return:
        """
        return self.__unit

    @property
    def strategy_name(self):
        return self.__strategy_name

    @property
    def index(self):
        return self.__index

    @property
    def stock_pool(self):
        return self.__stock_pool

    @property
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
        return self.__dividend_type

    @property
    def parameters(self) -> dict:
        """
        执行策略的参数字典
        :return:
        """
        return self.__parameters

    @property
    def current_dt(self) -> datetime.datetime:
        return self.__dt

    def buy(self,
            stock_code: str,
            volume: int,
            price_type: int = pqconstant.FIX_PRICE,
            price: float = None,
            force: bool = False):
        """

        :param stock_code: 股票代码
        :param volume: 数量
        :param price_type: 价格类型
        :param price: 买入价格
        :param force: 如果force == True, 则直接交易，忽略是否进行委托队列。仅在实盘中有效, 在回测中忽略
        :return:
        """
        # 检查股票是否已经停牌
        stock_info = get_stock_info(symbols=[stock_code],
                                    fields=['symbol', 'suspend_status'],
                                    trade_date=self.current_dt.strftime('%Y-%m-%d'))
        if stock_info.empty:
            log.warning(
                f"无法获取股票信息，取消买入: stock_code={stock_code}, trade_date={self.current_dt.strftime('%Y-%m-%d')}")
            return

        # 停复牌状态：<=0 正常，-1 复牌，>0 停牌, >=1 停牌天数
        suspend_status = stock_info.iloc[0, 1]
        if suspend_status > 0:
            log.warning(
                f"股票停牌，取消买入: stock_code={stock_code}, trade_date={self.current_dt.strftime('%Y-%m-%d')}")
            return

        # 获取价格
        if price_type != pqconstant.FIX_PRICE or price is None:
            # trade_date = self.current_dt.strftime('%Y-%m-%d')
            if self.unit in ['1d']:
                trade_date = self.current_dt.strftime('%Y-%m-%d')
                trade_datetime = None
            else:
                trade_date = None
                trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
            # price_df = get_history(count=1,
            #                        end_date=trade_date,
            #                        end_datetime=trade_datetime,
            #                        unit=self.unit,
            #                        field='close',
            #                        security_list=[stock_code],
            #                        dividend_type=self.dividend_type,
            #                        expect_df=True)

            price_df = get_factor(trade_date=trade_date,
                                  start_datetime=trade_datetime,
                                  end_datetime=trade_datetime,
                                  timeframe=self.unit,
                                  factor='close',
                                  symbol=stock_code,
                                  dividend_type=self.dividend_type,
                                  expect_df=True)

            if price_df.empty:
                log.warning(f"无法获取股票价格，取消买入: stock_code={stock_code}, trade_date={trade_date}")
                return
            else:
                price = price_df.iloc[0, 0]

        # 更新Portfolio cash
        cost = volume * price
        if self.portfolio.available_cash < cost:
            log.warning(f"可用现金不足，放弃买入. cash={self.portfolio.available_cash}, cost={cost}")
            return
        else:
            self.portfolio.add_cash(cost * -1)

        # 更新Portfolio Positions
        position: Position = self.portfolio.positions.get(stock_code, None)
        if position:
            # 已经有头寸
            position.update_position(volume=volume, price=price, transact_time=self.current_dt)
        else:
            # 创建新的头寸
            position = Position(stock_code=stock_code,
                                volume=volume,
                                price=price,
                                init_time=self.current_dt,
                                context=self)
            self.portfolio.positions[stock_code] = position

        # 更新委托Id
        self.order_id += 1
        order = Order(order_id=self.order_id, stock_code=stock_code, direction='buy', order_volume=volume,
                      order_price=price, avg_cost=price, context=self)
        self.notify_order(order)
        return order

    def sell(self,
             stock_code: str,
             volume: int,
             price_type: int = pqconstant.FIX_PRICE,
             price: float = None,
             force: bool = False):
        """
        卖出股票
        :param stock_code:
        :param volume:
        :param price_type:
        :param price:
        :param force:
        :return:
        """
        # 检查股票是否已经停牌
        stock_info = get_stock_info(symbols=[stock_code],
                                    fields=['symbol', 'suspend_status'],
                                    trade_date=self.current_dt.strftime('%Y-%m-%d'))
        if stock_info.empty:
            log.warning(
                f"无法获取股票信息，取消买入: stock_code={stock_code}, trade_date={self.current_dt.strftime('%Y-%m-%d')}")
            return

        # 停复牌状态：<=0 正常，-1 复牌，>0 停牌, >=1 停牌天数
        suspend_status = stock_info.iloc[0, 1]
        if suspend_status > 0:
            log.warning(
                f"股票停牌，取消买入: stock_code={stock_code}, trade_date={self.current_dt.strftime('%Y-%m-%d')}")
            return

        # 获取价格
        if price_type != pqconstant.FIX_PRICE or price is None:
            # trade_date = self.current_dt.strftime('%Y-%m-%d')
            if self.unit in ['1d']:
                trade_date = self.current_dt.strftime('%Y-%m-%d')
                trade_datetime = None
            else:
                trade_date = None
                trade_datetime = self.current_dt.strftime('%Y-%m-%d %H:%M:%S')
            # price_df = get_history(count=1,
            #                        end_date=trade_date,
            #                        end_datetime=trade_datetime,
            #                        unit=self.unit,
            #                        field='close',
            #                        security_list=[stock_code],
            #                        dividend_type=self.dividend_type,
            #                        expect_df=True)

            price_df = get_factor(trade_date=trade_date,
                                  start_datetime=trade_datetime,
                                  end_datetime=trade_datetime,
                                  timeframe=self.unit,
                                  factor='close',
                                  symbol=stock_code,
                                  dividend_type=self.dividend_type,
                                  expect_df=True)

            if price_df.empty:
                log.warning(f"无法获取股票价格，取消卖出: stock_code={stock_code}, trade_date={trade_date}")
                return
            else:
                price = price_df.iloc[0, 0]

        position: Position = self.portfolio.positions.get(stock_code, None)
        if position is None:
            log.error(f"stock_code: {stock_code} 无持仓，取消卖出")
            return
        if position.can_use_volume < volume:
            log.error(f"stock_code: {stock_code} 持仓数量 {position.can_use_volume} 不足，取消卖出")
            return

        # 持仓成本
        avg_price = position.avg_price

        # 更新持仓
        update_status = position.update_position(volume=volume * -1, price=price, transact_time=self.current_dt)

        # 检查是否已经平仓, 如是，则删除头寸记录
        position: Position = self.portfolio.positions.get(stock_code, None)
        if position and position.volume == 0:
            del self.portfolio.positions[stock_code]

        # 更新Portfolio cash
        if update_status:
            self.portfolio.add_cash(volume * price)

        # 更新委托Id
        self.order_id += 1
        order = Order(order_id=self.order_id, stock_code=stock_code, direction='sell', order_volume=volume,
                      order_price=price, avg_cost=avg_price, context=self)
        self.notify_order(order)
        return order

    @property
    def portfolio(self):
        """
        策略投资组合，可通过该对象获取当前策略账户、持仓等信息
        """
        return self._portfolio

    def inout_cash(self, cash: float):
        """
        投资组合转入或转出资金，当日的出入金从当日开始记入成本，用于计算收益，即当日结束计算收益时的本金是包含当日出入金金额的
        :param cash: 可正可负，正为入金，负为出金。
        :return:
        """
        # 记录出入金历史
        self.inout_cash_his.append({"datetime": self.current_dt, "cash": cash})
        # 把出入金更新到投资组合的可以资金
        self.portfolio.add_cash(cash=cash)
