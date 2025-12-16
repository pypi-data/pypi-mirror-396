from six import with_metaclass
import abc
from pqsdk.enums.orderStatus import OrderStatus
import datetime


class AbstractOrder(with_metaclass(abc.ABCMeta)):
    """
    买卖订单
    """

    @property
    @abc.abstractmethod
    def status(self) -> OrderStatus:
        """
        状态, 一个OrderStatus值
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def add_time(self) -> datetime.datetime:
        """
        订单添加时间, [datetime.datetime]对象
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_buy(self) -> bool:
        """
        bool值, 买还是卖。对于期货: (1) 开多/平空 -> 买; （2）开空/平多 -> 卖
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def volume(self):
        """
        下单数量, 不管是买还是卖, 都是正数
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def filled(self):
        """
        已经成交的股票数量, 正数
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def security(self):
        """
        股票代码
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def order_id(self):
        """
        订单ID
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def price(self):
        """
        平均成交价格, 已经成交的股票的平均成交价格(一个订单可能分多次成交)
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def avg_cost(self):
        """
        卖出时表示下卖单前的此股票的持仓成本, 用来计算此次卖出的收益. 买入时表示此次买入的均价(等同于price).
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def commission(self):
        """
        交易费用（佣金、税费等）
        :return:
        """
        raise NotImplementedError
