from pqsdk.interface import AbstractPosition
from pqsdk import log
from pqsdk.api import get_factor
import datetime
import pandas as pd


class Position(AbstractPosition):

    def __init__(self,
                 stock_code: str,
                 volume: int,
                 price: float,
                 init_time: datetime.datetime,
                 context):
        self._stock_code = stock_code
        self._open_price = price  # 初始化持仓，开仓价
        self._avg_price = price  # 初始化的持仓，平均成本价等于买入价
        self._can_use_volume = 0  # 初始建仓，可用数量为0
        self._volume = volume  # 初始建仓
        self.context = context
        self._init_time = init_time  # 建仓时间
        self._transact_time = init_time  # 最后交易时间
        # 记录买入历史，用于在can_use_volume中剔除当日买入的数量
        self._buy_volumes = [{"trade_date": context.current_dt.strftime("%Y-%m-%d"), "volume": volume}]

    @property
    def stock_code(self) -> str:
        return self._stock_code

    @property
    def open_price(self):
        return self._open_price

    @property
    def avg_price(self):
        """
        平均成本价格
        :return:
        """
        return self._avg_price

    def update_position(self, volume: int, price: float = None, transact_time: datetime.datetime = None) -> bool:
        """
        更新持仓
        :param transact_time: 最新交易时间
        :param volume: 新买入或者卖出数量, volume > 0 为买入， volume < 0为卖出
        :param price: 买入价格，卖出时忽略
        :return: 是否更新成功
        """
        # 买入：仅买入时需要更新持仓平均成本价格
        if volume > 0:
            # 平均价格 = (原来持仓成本 + 买入成本) / (原来持仓数量 + 新买入数量)
            self._avg_price = (self.volume * self.avg_price + volume * price) / (self.volume + volume)
            # 记录买入数量，一天内可能买入多次
            self._buy_volumes.append({"trade_date": self.context.current_dt.strftime("%Y-%m-%d"), "volume": volume})

        # 卖出：卖出时判断持仓数量是否充足
        if volume < 0 and self.can_use_volume + volume < 0:
            log.error(f"可用持仓数量不足，取消卖出: stock_code={self.stock_code}, "
                      f"can_use_volume={self.can_use_volume} ,sel_volume={volume}")
            return False

        self._volume = self.volume + volume
        self._transact_time = transact_time

        return True

    @property
    def can_use_volume(self):
        """
        可用数量
        :return:
        """
        # 从今天order中计算买入数量
        buy_volumes_df = pd.DataFrame(self._buy_volumes)
        buy_volumes_df = buy_volumes_df[buy_volumes_df['trade_date'] == self.context.current_dt.strftime("%Y-%m-%d")]
        today_buy_volume = buy_volumes_df['volume'].sum()
        self._can_use_volume = self.volume - today_buy_volume
        return self._can_use_volume

    @property
    def volume(self):
        """
        总持仓数量
        :return:
        """
        return self._volume

    @property
    def price(self):
        if self.context.unit in ['1d']:
            trade_date = self.context.current_dt.strftime('%Y-%m-%d')
            trade_datetime = None
        else:
            trade_date = None
            trade_datetime = self.context.current_dt.strftime('%Y-%m-%d %H:%M:%S')
        # price_df = get_history(count=1,
        #                        end_date=trade_date,
        #                        end_datetime=trade_datetime,
        #                        unit=self.context.unit,
        #                        field='close',
        #                        security_list=[self.stock_code],
        #                        dividend_type=self.context.dividend_type,
        #                        expect_df=True)

        price_df = get_factor(trade_date=trade_date,
                              start_datetime=trade_datetime,
                              end_datetime=trade_datetime,
                              timeframe=self.context.unit,
                              factor='close',
                              symbol=self.stock_code,
                              dividend_type=self.context.dividend_type,
                              expect_df=True)

        if price_df.empty:
            log.warning(f"截止 trade_date={trade_date}, stock_code={self.stock_code}, 未查到历史数据, 默认price=0")
            return 0.0
        else:
            price = price_df.iloc[0, 0]
            return price

    @property
    def value(self):
        """
        总持仓市值
        :return:
        """
        return self.volume * self.price

    @property
    def init_time(self):
        """
        建仓时间
        :return:
        """
        return self._init_time

    @property
    def init_date(self):
        return self.init_time.strftime('%Y-%m-%d')

    @property
    def transact_time(self):
        """
        最后交易时间
        :return:
        """
        return self._transact_time

    @property
    def transact_date(self):
        return self.transact_time.strftime('%Y-%m-%d')
