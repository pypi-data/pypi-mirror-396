from six import with_metaclass
import abc


class AbstractPortfolio(with_metaclass(abc.ABCMeta)):
    """
    策略账户持仓信息
    """

    # @property
    # @abc.abstractmethod
    # def asset(self) -> dict:
    #     """
    #     账号资金
    #     {'total_asset': 10204239.17, 'cash': 9136261.17, 'market_value': 1067978.0, 'frozen_cash': 0.0}
    #     :return:
    #     """
    #     raise NotImplementedError

    @property
    @abc.abstractmethod
    def positions(self) -> dict:
        """
        [dict] 持仓字典
        {
        "510300.SH": {
          "volume": 2600,
          "can_use_volume": 1400,
          "open_price": 20.206,
          "market_value": 10701.599999999999
        }}
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def total_value(self):
        """
        [float]总的权益, 包括现金, 仓位的总价值, 可用来计算收益
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def positions_value(self):
        """
        [float] 持仓价值
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def available_cash(self):
        """
        [float] 可用资金
        """
        raise NotImplementedError

    @abc.abstractmethod
    def add_cash(self, cash: float):
        """
        添加/减少可用金额
        :param cash:
        :return:
        """
        raise NotImplementedError

    def get_frozen_cash(self, sec_code: str = None):
        """
        获取冻结现金
        冻结现金 = sum（（买入委托数量 - 买入成交数量） * 委托价格）

        在回测过程中，买入委托即刻成交，所以冻结现金默认为0

        :param sec_code: 获取指定股票的冻结现金, 如果为None，则获取投资组合的冻结现金
        :return:
        """
        raise NotImplementedError
