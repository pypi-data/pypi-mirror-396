from six import with_metaclass
import abc
import datetime


class AbstractInstrument(with_metaclass(abc.ABCMeta)):
    """
    获取合约当前的实时基础信息和行情信息
    """

    @property
    @abc.abstractmethod
    def last_price(self) -> float:
        """
        最新价
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def high_limit(self) -> float:
        """
        涨停价
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def low_limit(self) -> float:
        """
        跌停价
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def paused(self) -> bool:
        """
        是否停止或者暂停了交易, 当停牌、未上市或者退市后返回 True
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_st(self) -> bool:
        """
        是否是 ST(包括ST, *ST)，是则返回 True，否则返回 False
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def day_open(self) -> float:
        """
        当天开盘价
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def display_name(self):
        """
        中文名称
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        股票现在的名称, 可以用这个来判断股票当天是否是 ST, *ST, 是否快要退市
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def industry_name(self) -> str:
        """
        股票现在所属行业名称（申万L3）
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def industry_code(self) -> str:
        """
        股票现在所属行业代码（申万L3）
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def start_date(self) -> datetime.date:
        """
        上市日期， [datetime.date] 类型
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def end_date(self):
        """
        退市日期（股票是最后一个交易日，不同于摘牌日期）， [datetime.datetime] 类型, 如果没有退市则为2200-01-01
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def type(self):
        """
        证券类型
         'index'	#指数
         'stock'	#股票
         'fund'	    #基金
         'etf'		#ETF
        :return:
        """
        raise NotImplementedError
