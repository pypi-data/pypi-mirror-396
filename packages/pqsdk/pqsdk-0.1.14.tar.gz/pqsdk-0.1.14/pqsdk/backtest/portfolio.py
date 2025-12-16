from pqsdk.interface import AbstractPortfolio
from pqsdk.api import get_factor


class Portfolio(AbstractPortfolio):

    def __init__(self, context):
        """
        策略的投资组合

        """

        self._positions = {}
        self._cash = 0.0
        self.context = context

    @property
    def positions(self) -> dict:
        """
        [dict] 持仓字典
        {
        "510300.SH": Position(stock_code, Position)}
        其中，Position包含如下属性：
        {
          "volume": 2600,
          "can_use_volume": 1400,
          "open_price": 20.206,
          "market_value": 10701.599999999999
        }
        """
        # # 清除已经被平仓的头寸
        # for sec_code, position in self._positions.items():
        #     if position.volume == 0:
        #         del self._positions[sec_code]

        return self._positions

    @property
    def total_value(self):
        return self.positions_value + self.available_cash

    @property
    def positions_value(self):
        # TODO 获取当时的持仓价值
        if self.context.unit in ['1d']:
            trade_date = self.context.current_dt.strftime('%Y-%m-%d')
            trade_datetime = None
        else:
            trade_date = None
            trade_datetime = self.context.current_dt.strftime('%Y-%m-%d %H:%M:%S')

        sec_code_lst = list(self.positions.keys())
        if len(sec_code_lst) == 0:
            # 策略无持仓
            return 0
        # count=1, 意思是：截止trade_date的最新价格，如果trade_date停牌，将提取最近的价格
        # price_df = get_history(count=1,
        #                        end_date=trade_date,
        #                        end_datetime=trade_datetime,
        #                        unit=self.context.unit,
        #                        field='close',
        #                        security_list=sec_code_lst,
        #                        dividend_type=self.context.dividend_type,
        #                        expect_df=True)

        # limit=1, 意思是：截止trade_date的最新价格，如果trade_date停牌，将提取最近的价格
        price_df = get_factor(trade_date=trade_date,
                              start_datetime=trade_datetime,
                              end_datetime=trade_datetime,
                              timeframe=self.context.unit,
                              factor='close',
                              symbol=sec_code_lst,
                              dividend_type=self.context.dividend_type,
                              expect_df=True)

        # 或通过层级位置删除（symbol是第0层, trade_date或者datetime是第1层）
        price_df = price_df.droplevel(1)

        price_dict = price_df.iloc[:, 0].to_dict()

        total_value = 0.0
        for sec_code, position in self.positions.items():
            price = price_dict.get(sec_code, 0.0)
            volume = position.volume
            total_value += volume * price

        return total_value

    @property
    def available_cash(self):
        return self._cash

    def add_cash(self, cash: float):
        """
        添加/减少可用金额
        :param cash:
        :return:
        """
        self._cash = self._cash + cash

    def get_frozen_cash(self, sec_code: str = None):
        """
        获取冻结现金
        冻结现金 = sum（（买入委托数量 - 买入成交数量） * 委托价格）

        在回测过程中，买入委托即刻成交，所以冻结现金默认为0

        :param sec_code: 获取指定股票的冻结现金, 如果为None，则获取投资组合的冻结现金
        :return:
        """
        return 0
