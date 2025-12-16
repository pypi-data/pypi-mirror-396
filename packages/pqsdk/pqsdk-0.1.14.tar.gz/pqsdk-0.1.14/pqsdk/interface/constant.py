from pqsdk import pqconstant
from pqsdk.enums.orderStatus import OrderStatus


class Constant(object):
    """
    常量实例，用于存储策略中用的的系统指定的常量
    """

    @property
    def OrderStatus(self):
        return OrderStatus

    @property
    def LATEST_PRICE(self):
        """
        # 最新价
        :return:
        """
        return pqconstant.LATEST_PRICE

    @property
    def FIX_PRICE(self):
        """
        # 指定价/限价
        :return:
        """
        return pqconstant.FIX_PRICE

    @property
    def MARKET_SH_CONVERT_5_CANCEL(self):
        """
        最优五档即时成交剩余撤销[上交所][股票]
        :return:
        """
        return pqconstant.MARKET_SH_CONVERT_5_CANCEL

    @property
    def MARKET_SH_CONVERT_5_LIMIT(self):
        """
        最优五档即时成交剩转限价[上交所][股票]
        :return:
        """
        return pqconstant.MARKET_SH_CONVERT_5_LIMIT

    @property
    def MARKET_PEER_PRICE_FIRST(self):
        """
        对手方最优价格委托[上交所[股票]][深交所[股票][期权]]
        :return:
        """
        return pqconstant.MARKET_PEER_PRICE_FIRST

    @property
    def MARKET_MINE_PRICE_FIRST(self):
        """
        本方最优价格委托[上交所[股票]][深交所[股票][期权]]
        :return:
        """
        return pqconstant.MARKET_MINE_PRICE_FIRST

    @property
    def MARKET_SZ_INSTBUSI_RESTCANCEL(self):
        """
        即时成交剩余撤销委托[深交所][股票][期权]
        :return:
        """
        return pqconstant.MARKET_SZ_INSTBUSI_RESTCANCEL

    @property
    def MARKET_SZ_CONVERT_5_CANCEL(self):
        """
        最优五档即时成交剩余撤销[深交所][股票][期权]
        :return:
        """
        return pqconstant.MARKET_SZ_CONVERT_5_CANCEL

    @property
    def MARKET_SZ_FULL_OR_CANCEL(self):
        """
        全额成交或撤销委托[深交所][股票][期权]
        :return:
        """
        return pqconstant.MARKET_SZ_FULL_OR_CANCEL
