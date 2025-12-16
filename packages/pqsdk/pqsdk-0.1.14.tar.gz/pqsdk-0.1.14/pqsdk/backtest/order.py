import datetime
from pqsdk.interface import AbstractOrder
from pqsdk.enums.orderStatus import OrderStatus


class Order(AbstractOrder):

    def __init__(self,
                 order_id: int,
                 stock_code: str,
                 direction: str,
                 order_volume: int,
                 order_price: float,  # 委托价格
                 avg_cost: float,  # 平均成本
                 context):
        self._order_id = order_id
        self.stock_code = stock_code
        self.direction = direction
        self.order_volume = order_volume
        self.order_price = order_price  # 委托价格
        # 平均成本：卖出时表示下卖单前的此股票的持仓成本, 用来计算此次卖出的收益. 买入时表示此次买入的均价(等同于price).
        self._avg_cost = avg_cost
        self.context = context

    @property
    def status(self) -> OrderStatus:
        return OrderStatus.held

    @property
    def add_time(self) -> datetime.datetime:
        return self.context.current_dt

    @property
    def is_buy(self) -> bool:
        return True if self.direction == 'buy' else False

    @property
    def volume(self):
        """
        下单数量, 不管是买还是卖, 都是正数
        :return:
        """
        return self.order_volume

    @property
    def filled(self):
        """
        已经成交的股票数量, 正数
        :return:
        """
        return self.order_volume

    @property
    def security(self):
        return self.stock_code

    @property
    def order_id(self):
        return self._order_id

    @property
    def price(self):
        """
        平均成交价格, 已经成交的股票的平均成交价格(一个订单可能分多次成交)
        :return:
        """
        return self.order_price

    @property
    def avg_cost(self):
        """
        卖出时表示下卖单前的此股票的持仓成本, 用来计算此次卖出的收益. 买入时表示此次买入的均价(等同于price).
        :return:
        """
        return self._avg_cost

    @classmethod
    def trade_fee_calculation(cls, exchange, price, volume, commission_rate, trade_type):
        """
        计算股票交易手续费
        :param exchange: 交易所，SH 代表上海A股；SZ 代表深圳A股
        :param price: 股票成交价格
        :param volume: 股票成交量
        :param commission_rate: 佣金比率
        :param trade_type: 交易类型，B代表买入，S代表卖出
        :return: total_fee 费用总计
        """
        stamp_duty, transfer_fee, exchange_fee, manage_fee, commission = 0, 0, 0, 0, 0
        if trade_type == 'S':
            # 印花税
            stamp_duty = price * volume * 0.001
        if exchange == 'SH':
            # 过户费 最低1元
            transfer_fee = max(price * volume * 0.00001, 1)
        # 经手费
        exchange_fee = price * volume * 0.0000487
        # 证管费
        manage_fee = price * volume * 0.00002
        # 佣金 最低5元
        commission = max(price * volume * commission_rate, 5)
        total_fee = stamp_duty + transfer_fee + exchange_fee + manage_fee + commission
        return total_fee

    @property
    def commission(self):
        """
        交易费用（佣金、税费等）
        :return:
        """
        ex = self.security[-2:]
        return self.trade_fee_calculation(exchange=ex,
                                          price=self.price,
                                          volume=self.filled,
                                          commission_rate=self.context.commission,
                                          trade_type='B' if self.is_buy else 'S')
