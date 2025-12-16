import datetime
from typing import Callable
from pqsdk.api import is_open_trade_date, get_next_trading_date
from pqsdk import log


class TimerFactory:
    def __init__(self, unit: str):
        """
        行情周期单位： 1d, 1m, 5m
        :param unit:
        """
        self.unit = unit      # 回测运行中基准行情的单位
        self.timer_list = []  # 定时器字典列表
        self.carry_dict = {}  # 顺延下一个交易日运行的timer {index: timer}
        self.timer_index = 0  # 给每个定时器一个编号

    @classmethod
    def format_time_str(cls, time_str):
        """
        字符串time_str作为输入，并返回格式化为HH:MM:SS的字符串，如果输入为HH:MM格式，则自动补充为HH:MM:00
        :param time_str:
        :return:
        """
        parts = time_str.split(':')
        if len(parts) == 2:
            # 如果是'HH:MM'格式，则自动补充为'HH:MM:00'
            return f"{parts[0]}:{parts[1]}:00"
            # 如果不是'HH:MM'格式，则检查是否是'HH:MM:SS'格式
        elif len(parts) == 3:
            # 如果是'HH:MM:SS'格式，则直接返回原字符串
            return time_str
        else:
            # 如果不是期望的格式，则返回错误或空字符串
            raise Exception(f"字符串格式不符合: {time_str}, 必须为HH:MM格式，或者HH:MM:SS的格式")

    @classmethod
    def is_valid_time(cls, start_time, t, interval: int, unit: str = 'm'):
        """
        判断给定时间t是否大于或等于开始时间start_time，并且t是以n个unit做为间隔的

        :param start_time: 检查的起始时间，datetime.datetime类型
        :param t: 被检查的时间，datetime.datetime类型
        :param interval: 单位间隔
        :param unit: 单位
        :return: bool
        """

        if unit not in ['m', 's']:
            raise Exception("unit is wrong, must be 'm' for minutes, or 's' for second.")
        # 确保t不小于start_time
        if t < start_time:
            return False

            # 计算t和start_time之间的时间差
        time_diff = t - start_time

        # 将时间差转换为分钟，并检查是否为n分钟的整数倍
        if unit == 'm':
            minutes_diff = time_diff.total_seconds() // 60  # 转换为分钟
        else:
            minutes_diff = time_diff.total_seconds()
        return minutes_diff % interval == 0

    def add_timer(self,
                  callback: Callable,
                  kwargs,
                  when='00:00:00',
                  weekdays=None,
                  weekcarry=False,
                  monthdays=None,
                  monthcarry=True,
                  dates=None,
                  minutes=None,
                  seconds=None,
                  datecarry=True):
        """
        添加计时器

        :param callback: 回调函数
        :param kwargs: 回调函数的参数
        :param when: 运行时间, format: '%H:%M:%S'
        :param weekdays: 每星期的第几天运行, Monday is 1, Sunday is 7
        :param weekcarry: weekday为非交易日，是否顺延下一个交易日
        :param monthdays: 每月的第几天运行
        :param monthcarry: 为非交易日，是否顺延下一个交易日
        :param dates: 间隔天数执行的日期列表，start_date为第一次执行日期
        :param minutes: 以when作为时间起点, 间隔的分神数执行
        :param seconds: 以when作为时间起点, 间隔的秒数执行
        :param datecarry: 为非交易日，是否顺延下一个交易日
        :return:
        """
        # 格式化为HH:MM:SS的字符串
        when = self.format_time_str(when)

        if monthdays is None:
            monthdays = []
        if weekdays is None:
            weekdays = []
        if dates is None:
            dates = []

        self.timer_index += 1
        timer = dict(index=self.timer_index,
                     callback=callback,
                     kwargs=kwargs,
                     when=when,
                     weekdays=weekdays,
                     weekcarry=weekcarry,
                     monthdays=monthdays,
                     monthcarry=monthcarry,
                     dates=dates,
                     minutes=minutes,
                     seconds=seconds,
                     datecarry=datecarry
                     )
        self.timer_list.append(timer)

    def carry_on(self, index, date, callback, kwargs):
        """
        顺延到下一个交易日执行的回调函数
        :param index: 定时器编号
        :param date:
        :param callback: 回调函数
        :param kwargs: 回调函数的参数字典
        :return:
        """
        self.carry_dict[index] = dict(date=date, callback=callback, kwargs=kwargs)

    def notify_timer(self, current_dt: datetime.datetime):
        """
        在回测中，此函数根据主图的Bar被触发，根据参数日期时间，遍历timer_list, 对符合条件的timer执行callback回调函数
        :param current_dt: 日期时间，datetime类型
        :return:
        """
        for timer in self.timer_list:
            index = timer['index']
            callback = timer['callback']
            kwargs = timer['kwargs']
            weekdays = timer['weekdays']
            weekcarry = timer['weekcarry']
            monthdays = timer['monthdays']
            monthcarry = timer['monthcarry']
            dates = timer['dates']
            datecarry = timer['datecarry']

            current_date = current_dt.strftime('%Y-%m-%d')

            # 1、先执行顺延的任务
            if index in self.carry_dict:
                carry_timer = self.carry_dict[index]
                # 检查是否顺延执行
                if current_date == carry_timer['date']:
                    # print(f"carry On: index={index}, date={carry_timer['date']}")
                    carry_timer['callback'](**carry_timer['kwargs'])
                    del self.carry_dict[index]  # 删除已经执行的顺延timer
                    # 碰巧当日也是顺延执行timer的执行日期, callback不需要重复执行
                    continue

            # 2、执行计划任务
            if not is_open_trade_date(current_date):  # 非交易日
                # 下一个交易日
                next_trade_date = get_next_trading_date(current_date)

                # 每周
                if len(weekdays) > 0 and current_dt.weekday() + 1 in weekdays and weekcarry:
                    log.warning(f"{current_dt} 非交易日, 顺延{callback.__name__}()函数执行日期: {next_trade_date} {timer['when']}")
                    self.carry_on(index, next_trade_date, callback, kwargs)  # 顺延下一个交易日执行

                # 每月
                if len(monthdays) > 0 and current_dt.day in monthdays and monthcarry:
                    log.warning(f"{current_dt} 非交易日, 顺延{callback.__name__}()函数执行日期: {next_trade_date} {timer['when']}")
                    self.carry_on(index, next_trade_date, callback, kwargs)  # 顺延下一个交易日执行

                # 每周期
                if len(dates) > 0 and current_date in dates and datecarry:
                    log.warning(f"{current_dt} 非交易日, 顺延{callback.__name__}()函数执行日期: {next_trade_date} {timer['when']}")
                    self.carry_on(index, next_trade_date, callback, kwargs)  # 顺延下一个交易日执行

                continue

            # 每周运行判断
            if len(weekdays) > 0 and current_dt.weekday() + 1 not in weekdays:
                continue

            # 每月运行判断
            if len(monthdays) > 0 and current_dt.day not in monthdays:
                continue

            # 每周期运行判断
            if len(dates) > 0 and current_date not in dates:
                continue

            # 执行回调函数的时机
            if self.unit in ['1d']:  # 日行情，每日执行
                # 如果是基准周期(self.unit)是1d则直接放行
                callback(**kwargs)
            elif self.unit in ['1m', '5m'] and timer['minutes'] is not None:  # 每间隔n分钟执行
                # 如果基准周期(self.unit)是1m或者5m, 间隔n分钟后执行
                start_time_str = f"{current_dt.strftime('%Y-%m-%d')} {timer['when']}"
                start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                if self.is_valid_time(start_time=start_time, t=current_dt, interval=timer['minutes'], unit='m'):
                    callback(**kwargs)
            elif self.unit in ['1m', '5m'] and timer['seconds'] is not None:  # 每间隔n秒执行
                # 如果基准周期(self.unit)是1m或者5m, 间隔n秒后执行

                # TODO 因为还没有秒级的行情数据，当秒级间隔时直接放行，否则使用下方注释掉的逻辑
                callback(**kwargs)

                # TODO 临时注释掉的逻辑，直到有秒级的数据
                # start_time_str = f"{current_dt.strftime('%Y-%m-%d')} {timer['when']}"
                # start_time = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                # if self.is_valid_time(start_time=start_time, t=current_dt, interval=timer['seconds'], unit='s'):
                #     callback(**kwargs)

            elif self.unit in ['1m', '5m'] and current_dt.strftime('%H:%M:%S') == timer['when']:  # 分钟行情，指定时间执行
                # 如果基准周期(self.unit)是1m或者5m，则时间到达后执行
                callback(**kwargs)
