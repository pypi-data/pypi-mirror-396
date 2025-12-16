# coding=utf-8
import datetime
import time
import pqsdk.api as api
from pqsdk.utils.dynamic_import import check_module, import_module_from_spec, import_module_from_code
from pqsdk.utils.import_global_modules import import_modules
from pqsdk import log
from .context import StrategyContext
from pqsdk.utils.timer_factory import TimerFactory
import pandas as pd
from .analyzer import TimeReturn
from typing import Callable
import pqsdk.utils.file_util as fu
from tqdm import tqdm

# 初始化策略前，导入sdk中的所有对象、函数、属性到全局变量中，以支持在策略中调用
import_modules(api)


class BacktestExecutor:
    def __init__(self, kwargs: dict, task=None):
        """

        :param kwargs:
        :param task: celery task
        """

        self.task = task

        # 策略参数, 从list转换为dict， 根据数据推断，把value转换为正确的数据类型
        # self.strategy_params = {param['key']: convert_to_type(param['value']) for param in kwargs.get('parameters')}
        self.strategy_params = kwargs.get('parameters')

        # # 检查必须的输入参数
        must_have_params = {'benchmark': "行情基准",
                            'unit': "行情周期",
                            "cash": "回测初始资金",
                            'start_date': "回测开始日期",
                            'end_date': "回测结束日期",
                            }
        for param, desc in must_have_params.items():
            if param not in self.strategy_params:
                content = f"输入参数中缺少必须的参数：{param}: {desc}"
                raise Exception(content)

        # 默认回测参数
        self.params = dict(
            # 指数 [000300.SH,000905.SH,000852.SH]
            index=self.strategy_params.get('index', []),
            # 股票池
            stock_pool=self.strategy_params.get('stock_pool', []),
            # 行情基准-运行周期，支持1d，1m，5m，即根据行情基准-证券代码的k线图，按照1d,1m执行handle_bar()函数
            unit=self.strategy_params.get('unit', '1d'),
            # 除权方式，, 支持none：不复权，front：前复权，back：后复权
            dividend_type=self.strategy_params.get('dividend_type', 'front'),  # 默认前复权
            strategy_file=kwargs.get('strategy_file', None),  # 策略代码文件
            strategy_script=kwargs.get('script', None),  # 策略代码
            parameters=self.strategy_params,  # dict类型，策略中可以访问到到自定义参数列表
            adjust_period=self.strategy_params.get('adjust_period', 5),  # 调仓周期，结合start_date和end_date计算调仓日列表
            hold_maxsize=self.strategy_params.get('hold_maxsize', 10),  # 最大持仓股票数量
            start_date=self.strategy_params.get('start_date'),  # 回测开始日期
            end_date=self.strategy_params.get('end_date'),  # 回测结束日期
            excluded_dates=None,  # 排除不交易的日期
            benchmark=self.strategy_params.get('benchmark', '000300.SH'),  # 回测基准
            init_investment=self.strategy_params.get('cash', 1000000),  # 初始回测资金
            commission=0.0,  # 交易佣金费率
            slip_type="perc",
            slip_perc=0.0,
            slip_fixed=0.0,
            print_dev=True,  # 是否打印开发日志
            save_result=True,  # 是否保存回测结果
            save_path="storage",
            save_tearsheet=True,  # 保存Tear sheet
            save_db=False,
        )

        # 初始化策略程序
        if self.params['strategy_file']:
            module_spec = check_module(self.params['strategy_file'])
            if module_spec:
                self.strategy = import_module_from_spec(module_spec)
                log.debug(f"从文件获取策略对象：strat_path = {self.params['strategy_file']}")
        elif self.params['strategy_script']:
            self.strategy = import_module_from_code(code=self.params['strategy_script'])
            log.info(f"从代码获取策略程序")
        else:
            raise Exception("未找到策略代码，中止回测程序")

        # 自定义定时器工厂
        self.timer_factory = TimerFactory(unit=self.params['unit'])

        # 初始化策略执行的上下文
        self.context = StrategyContext(kwargs=self.params, timer_factory=self.timer_factory)

        # Analyzer dict, key=name, value=analyzer
        self.analyzers = {}

        # 创建文件日志
        file_path = f"{self.params.get('save_path', 'storage')}/logs/"
        fu.create_dir(path=file_path)
        file_name = f'run_backtest_'
        strat_run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_name += "__time=" + strat_run_time.replace("-", "").replace(":", "").replace(" ", "_") + ".log"
        log_path = file_path + file_name
        # 配置log输出到文件
        log.add_file_handler(file_name=log_path, level=log.DEBUG)

    def add_analyzer(self, name: str, analyzer: Callable):
        self.analyzers[name] = analyzer().set_context(self.context)

    def initialize(self, context):
        """
        初始化方法，在整个回测、模拟实盘中最开始执行一次，用于初始一些全局变量，全局变量会被持久化。重启策略不会再次执行。
        :param context:
        :return:
        """
        if hasattr(self.strategy, 'initialize'):
            self.strategy.initialize(context=context)
        else:
            raise Exception(f"{context.current_dt} 策略中缺少initialize()初始化函数")

    def process_initialize(self, context):
        """
        每次启动策略都会执行的初始化函数，一般用来初始化一些不能持久化保存的内容. , 比如以__开头的全局变量属性，或者计划任务，在 initialize 后执行.
        :param context:
        :return:
        """
        if hasattr(self.strategy, 'process_initialize'):
            self.strategy.process_initialize(context=context)

    def before_trading_start(self, context):
        """
        开盘前运行(可选)
        该函数会在每天开始交易前被调用一次, 可以在这里添加一些每天都要初始化的动作。
        该函数依据的时间是股票的交易时间，即该函数启动时间为'09:00'.
        :param context:
        :return:
        """
        if hasattr(self.strategy, 'before_trading_start'):
            self.strategy.before_trading_start(context=context)

    def after_trading_end(self, context):
        """
        收盘后运行(可选)
        每天结束交易后被调用一次, 您可以在这里添加一些每天收盘后要执行的内容
        :param context:
        :return:
        """
        if hasattr(self.strategy, 'after_trading_end'):
            self.strategy.after_trading_end(context=context)

    def handle_bar(self, context):
        """
        K线处理函数
        :param context:
        :return:
        """
        if hasattr(self.strategy, 'handle_bar'):
            self.strategy.handle_bar(context=context)

    def on_strategy_end(self, context):
        """
        策略结束后执行
        :param context:
        :return:
        """
        if hasattr(self.strategy, 'on_strategy_end'):
            self.strategy.on_strategy_end(context=context)

    @classmethod
    def on_reset(cls, context):
        """
        每日重置的callback函数，必须在before_trading_start()之前执行, 在实盘中，每日早上9:10重置
        :return:
        """
        # --------------------------------------------------------------
        # 重置当日的股票数据字典，包括当日最新价、涨停价、跌停价、是否停牌、是否ST等
        # --------------------------------------------------------------
        log.debug(f"{context.current_dt} 策略每日重置完成")

    @classmethod
    def generate_time_range(cls, start_date, end_date, unit, datetime_format='%Y-%m-%d'):
        """
        获取回测的播放时间范围
        :param start_date:
        :param end_date:
        :param unit:
        :param datetime_format:
        :return:
        """
        # 获取当前系统时间
        current_system_time = datetime.datetime.now()

        # 将字符串日期时间转换为datetime对象
        start_datetime = datetime.datetime.strptime(start_date, datetime_format)
        end_datetime = datetime.datetime.strptime(end_date, datetime_format)

        # 设置开始日期时间为开盘时间9:30:00
        start_datetime = start_datetime.replace(hour=9, minute=30, second=0)
        # 设置结束日期时间为收盘时间15:00:00
        end_datetime = end_datetime.replace(hour=15, minute=0, second=0)

        # 如果结束时间超过当前系统时间，则使用当前系统时间作为结束时间
        if end_datetime > current_system_time:
            end_datetime = current_system_time

        # 初始化时间列表
        time_list = []

        # 确定时间间隔
        if unit == '1d':
            interval = datetime.timedelta(days=1)
        elif unit == '1m':
            interval = datetime.timedelta(minutes=1)
        elif unit == '5m':
            interval = datetime.timedelta(minutes=5)
        elif unit == '15m':
            interval = datetime.timedelta(minutes=15)
        elif unit == '30m':
            interval = datetime.timedelta(minutes=30)
        elif unit == '1h':
            interval = datetime.timedelta(hours=1)
        else:
            raise ValueError(f"Invalid unit: {unit}. Must be '1d', '1m', '5m', '15m', '30m', or '1h'.")

        # 使用循环来递增时间，直到超过结束日期时间或当前系统时间
        current_datetime = start_datetime
        while current_datetime <= end_datetime:
            # 检查是否超过当前系统时间
            if current_datetime > current_system_time:
                break

            # 对于分钟级别的unit，需要处理交易时间和跨天
            if unit in ['1m', '5m', '15m', '30m', '1h']:
                time_str = current_datetime.strftime('%H%M%S')

                # 如果时间在11:30之后、13:00之前，直接跳到13:00（中午休市）
                if '113000' < time_str < '130000':
                    current_datetime = current_datetime.replace(hour=13, minute=0, second=0)
                    if current_datetime > end_datetime or current_datetime > current_system_time:
                        break
                    time_str = current_datetime.strftime('%H%M%S')

                # 检查是否在交易时间内
                if not ('093000' <= time_str <= '113000' or '130000' <= time_str <= '150000'):
                    # 不在交易时间内，判断是跨天还是其他情况
                    if time_str > '150000' or time_str < '093000':
                        # 跨天了，跳到下一天的9:30
                        next_day = current_datetime.date() + datetime.timedelta(days=1)
                        current_datetime = datetime.datetime.combine(next_day, datetime.time(9, 30, 0))
                        if current_datetime > end_datetime or current_datetime > current_system_time:
                            break
                        continue
                    else:
                        # 其他情况，继续递增
                        current_datetime += interval
                        continue

            # 再次检查是否超过当前系统时间（在添加到列表之前）
            if current_datetime > current_system_time:
                break

            time_list.append(current_datetime)
            current_datetime += interval

            # 对于分钟级别的unit，检查递增后的时间，如果跨天了，跳到下一天的9:30
            if unit in ['1m', '5m', '15m', '30m', '1h']:
                time_str = current_datetime.strftime('%H%M%S')
                # 如果时间不在交易时间内（可能是跨天了）
                if not ('093000' <= time_str <= '113000' or '130000' <= time_str <= '150000'):
                    # 判断是跨天还是中午休市
                    if time_str > '150000' or time_str < '093000':
                        # 跨天了，跳到下一天的9:30
                        next_day = current_datetime.date() + datetime.timedelta(days=1)
                        current_datetime = datetime.datetime.combine(next_day, datetime.time(9, 30, 0))
                        if current_datetime > end_datetime or current_datetime > current_system_time:
                            break
                    elif '113000' < time_str < '130000':
                        # 中午休市，跳到13:00
                        current_datetime = current_datetime.replace(hour=13, minute=0, second=0)
                        if current_datetime > end_datetime or current_datetime > current_system_time:
                            break

        return time_list

    def run(self):
        """
        执行回测
        :return:
        """
        start_time = time.time()

        # 执行结果
        results = {"benchmark": self.params['benchmark']}

        # 获取行情数据范围
        log.info(f"回测时间范围：start_date={self.params['start_date']}, end_date={self.params['end_date']}")

        # 获取Benchmark Kline: 最新价格，昨日收盘价，用于计算benchmark的收益率
        # df = api.get_attribute_history(security=self.params['benchmark'],
        #                                fields=['close', 'pre_close'],
        #                                unit=self.params['unit'],
        #                                start_date=self.params['start_date'],
        #                                end_date=self.params['end_date'],
        #                                dividend_type=self.params['dividend_type'])

        df = api.get_factor(symbol=self.params['benchmark'],
                            factor=['close', 'pre_close'],
                            timeframe=self.params['unit'],
                            start_date=self.params['start_date'],
                            end_date=self.params['end_date'],
                            dividend_type=self.params['dividend_type'])

        if df.empty:
            log.warning(f"回测时间范围没有行情数据，请检查参数: 回测基准 {self.params['benchmark']} "
                        f"开始日期 {self.params['start_date']} 结束日期 {self.params['end_date']}")
            return

        # 通过层级名称删除symbol
        df = df.droplevel('symbol')

        # 计算收益率
        df['return_rate'] = df['close'] / df['pre_close'] - 1

        df.index = pd.to_datetime(df.index)

        # 回测时间范围
        time_range = self.generate_time_range(start_date=self.params['start_date'],
                                              end_date=self.params['end_date'],
                                              unit=self.params['unit'])

        # 按照回测的时间序列向后补充数据，如果有缺失的话
        df = df.reindex(time_range, method='ffill')

        # 设置context.dt为默认的第一天，因为initialize()或者process_initialize()可能会用到
        self.context.set_dt(time_range[0])

        # 初始化现金: 初始化出入金在第一天为回测的初始化资金
        self.context.inout_cash(self.params.get('init_investment', 0.0))

        # 添加默认的analyzer
        self.add_analyzer(name="time_return", analyzer=TimeReturn)

        # 初始化策略, 仅第一次启动策略时执行
        self.initialize(context=self.context)

        # 每次启动策略时执行
        self.process_initialize(context=self.context)

        # 执行Analyzers.start()
        for name, analyzer in self.analyzers.items():
            analyzer.start()

        # 按照回测时间范围的交易日播放进行回测
        trade_date = None  # 当前的日期
        is_open_trade_date = False  # 是否为交易日
        total = len(time_range)
        run_start_dt = datetime.datetime.now()  # 用于估算回测还剩余多少时间
        # 使用 enumerate() 和 tqdm()
        for index, trade_time in enumerate(tqdm(time_range, total=len(time_range))):
            # 在这里你可以使用 index 和 trade_time
            # 注意：由于 tqdm 是基于迭代器工作的，它实际上并不需要 total 参数来正确工作，
            # 但提供 total 可以让进度条更准确地显示。
            # 如果不知道长度，可以省略 total 参数，但进度条可能不会非常准确。
            # 这里的 trade_time 实际上是枚举的值（即 range 中的数字）

            # task打点进度
            if self.task is not None:
                run_current_dt = datetime.datetime.now()
                run_delta = (run_current_dt - run_start_dt).seconds
                self.task.update_state(meta={"current": index + 1,
                                             "estimate_left_time": int(run_delta / (index + 1) * (total - index - 1)),
                                             "total": total})

            # new trade date, 每天执行一次after_trading_end()，最后一次在for循环结束后执行
            if trade_date is not None and trade_time.strftime('%Y-%m-%d') != trade_date:
                # 每日收盘后执行，必须在更新设置context之前执行
                self.after_trading_end(context=self.context)

            # new trade date，每天执行一次，检查是否为交易日
            if trade_date is None or trade_time.strftime('%Y-%m-%d') != trade_date:
                is_open_trade_date = api.is_open_trade_date(trade_time.strftime('%Y-%m-%d'))

            # 记录benchmark的收盘价，每个bar执行一次, 在unit=‘1d’，需要设置在context.set_dt()之前
            if is_open_trade_date:
                # 设置benchmark的收益率
                self.context.set_benchmark_value(df.loc[trade_time]['return_rate'])

            # 设置context.dt，每个bar执行一次，必须在on_reset()和before_trading_start()之前，因context.dt会在这些函数内被访问
            if self.context.unit in ['1d']:
                # 如果行情周期unit为天，则回测的当前时间(context.current_dt)指向开票时间9:30
                open_09_30 = datetime.datetime(trade_time.year, trade_time.month, trade_time.day, 9, 30, 0)
                self.context.set_dt(open_09_30)
            else:
                self.context.set_dt(trade_time)

            # new trade date，每天执行一次，每日重置on_reset，看盘前运行before_trading_start的函数
            if trade_date is None or trade_time.strftime('%Y-%m-%d') != trade_date:
                trade_date = trade_time.strftime('%Y-%m-%d')
                # 每日重置
                if is_open_trade_date:
                    self.on_reset(context=self.context)

                # 每日开盘前，必须执行在定时器任务之前
                if is_open_trade_date:
                    self.before_trading_start(context=self.context)

            # 如果主图按照1d的数据回测，默认在收盘时执行当天的任务
            if self.context.unit in ['1d']:
                # 如果行情周期unit为天，则回测的当前时间(context.current_dt)指向收盘时间15:00
                close_15_00 = datetime.datetime(trade_time.year, trade_time.month, trade_time.day, 15, 0, 0)
                self.context.set_dt(close_15_00)

            # 执行定时器任务:run_daily, run_weekly, run_monthly, run_periodically
            self.timer_factory.notify_timer(self.context.current_dt)

            # 按K线图执行
            if is_open_trade_date:
                self.handle_bar(context=self.context)

            # 执行Analyzers.next()
            if is_open_trade_date:
                for name, analyzer in self.analyzers.items():
                    analyzer.next()
        else:
            # 最后一个Bar收盘后执行
            if is_open_trade_date:
                self.after_trading_end(context=self.context)

        # 策略结束
        self.on_strategy_end(context=self.context)

        # 执行Analyzers.stop()
        for name, analyzer in self.analyzers.items():
            analyzer.stop()

        # 获取Analyzers结果
        analysis = {}
        for name, analyzer in self.analyzers.items():
            analysis[name] = analyzer.get_analysis()

        results['analysis'] = analysis

        # 画图数据
        results['plot_data'] = self.context.plot_data

        # 所有委托明细
        orders_df = pd.DataFrame(self.context.orders)
        results['orders'] = orders_df

        # 所有出入金历史
        results['inout_cash'] = pd.DataFrame(self.context.inout_cash_his)

        # 总回测时长
        end_time = time.time()
        # 返回累计收益结果
        strat_returns = results['analysis']['time_return']['strat_return']
        bchmk_returns = results['analysis']['time_return']['bchmk_return']
        cum_strat_returns = (1 + strat_returns).cumprod() - 1
        cum_bchmk_returns = (1 + bchmk_returns).cumprod() - 1
        log.info(f"时长(m)={(end_time - start_time) / 60:.2f}, "
                 f"策略收益={cum_strat_returns.values.tolist()[-1]} "
                 f"基准收益={cum_bchmk_returns.values.tolist()[-1]} "
                 )

        return results


# ---------------------------------------------------------
# 外部可以访问的列表
# ---------------------------------------------------------
__all__ = ["BacktestExecutor"]
__all__.extend([name for name in globals().keys() if name.startswith("get")])
