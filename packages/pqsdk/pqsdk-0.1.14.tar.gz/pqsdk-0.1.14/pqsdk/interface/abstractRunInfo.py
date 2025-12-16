from six import with_metaclass
import abc


class AbstractRunInfo(with_metaclass(abc.ABCMeta)):
    """
    策略运行信息，包括回测过程中的所有参数。
    """

    @property
    @abc.abstractmethod
    def tenant_id(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def portfolio_id(self):
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parameters(self):
        """
        策略中自定义参数字典
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def start_date(self):
        """
        策略的开始日期
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def end_date(self):
        """
        策略的结束日期
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def stock_starting_cash(self):
        """
        股票账户初始资金
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def strategy_id(self):
        """
        策略id
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def release_id(self):
        """
        策略版本id
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
    def strategy_remark(self):
        """
        策略备注
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_queued_order(self):
        """
        策略是支持委托队列，如果False，则直接通过交易终端进行交易
        如果是回测，直接返回False，直接交易。
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def benchmark(self):
        """
        基准指数代码，比如沪深300
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def stock_pool(self) -> list:
        """
        股票池，指数列表
        :return:
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def stock_pool_members(self) -> list:
        """
        当日的股票池成员
        :return:
        """
        raise NotImplementedError
