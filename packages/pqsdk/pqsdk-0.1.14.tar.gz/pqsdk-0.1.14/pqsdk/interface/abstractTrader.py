from six import with_metaclass
import abc
from .abstractOrder import AbstractOrder


class AbstractTrader(with_metaclass(abc.ABCMeta)):

    @abc.abstractmethod
    def buy(self, stock_code: str, volume: int, price_type: int, price: float, force: bool = False) -> AbstractOrder:
        """
        证券买入委托
        Returns:
          - 委托的order_id
        """
        raise NotImplementedError

    @abc.abstractmethod
    def sell(self, stock_code: str, volume: int, price_type: int, price: float, force: bool = False) -> AbstractOrder:
        """
        证券卖出委托
        Returns:
          - 委托的order_id
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_percent(self, stock_code: str, target: float = 0.0, force: bool = False) -> AbstractOrder:
        """
        基于order_target_value（），按照总资产的百分比委托下单

        :param force: 是否强制交易
        :param stock_code:目标持仓股票
        :param target: 目标持仓比例
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_value(self, stock_code: str, target: float = 0.0, price: float = None,
                           force: bool = False) -> AbstractOrder:
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

        :param force: 是否强制交易
        :param stock_code: 目标持仓股票
        :param target: 目标持仓市值
        :param price:
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def order_target_volume(self, stock_code: str, target: int = 0.0, force: bool = False) -> AbstractOrder:
        """
        基于order_target_value()，按照个股的数量目标数量下单。注意，可能存在账户资金不足的情况。

        :param force: 是否强制交易
        :param stock_code: 目标持仓股票
        :param target: 目标持仓数量
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def close(self, stock_code: str, force: bool = False) -> AbstractOrder:
        """
        以最新价平仓股票代码, 默认平仓数量为可用数量
        :param force: 是否强制交易
        :param stock_code: 需要平仓的股票代码
        :return:
        """
        raise NotImplementedError
