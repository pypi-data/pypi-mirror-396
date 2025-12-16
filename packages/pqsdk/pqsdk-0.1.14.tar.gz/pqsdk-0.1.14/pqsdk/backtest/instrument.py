from pqsdk.interface import AbstractInstrument, AbstractRunInfo
import datetime
from pqsdk import log
from pqsdk.api import get_history, get_factor, get_stock_info, get_suspend_info, get_stock_name_his


class Instrument(AbstractInstrument):

    def __init__(self, stock_code: str, run_info: AbstractRunInfo, context):
        self.stock_code = stock_code
        self.context = context
        self.run_info = run_info

        # 获取股票基础信息
        bsc_info_df = get_stock_info(fields=['list_date', 'fullname', 'name', 'industry'],
                                     stock_lst=[stock_code])
        bsc_info_df = bsc_info_df.set_index(['sec_code'])
        self.bsc_info_dict = bsc_info_df.T.to_dict()

    @property
    def last_price(self) -> float:
        # 获取当前收盘价
        # TODO 没有缓存作用，每次访问查询数据库
        # trade_date = self.context.current_dt.strftime('%Y-%m-%d')
        if self.context.unit in ['1d']:
            trade_date = self.context.current_dt.strftime('%Y-%m-%d')
            trade_datetime = None
        else:
            trade_date = None
            trade_datetime = self.context.current_dt.strftime('%Y-%m-%d %H:%M:%S')

        price_df = get_history(count=1,
                               end_date=trade_date,
                               end_datetime=trade_datetime,
                               unit=self.context.unit,
                               field='close',
                               security_list=[self.stock_code],
                               dividend_type=self.context.dividend_type,
                               expect_df=True)
        if price_df.empty:
            log.warning(f"股票停牌，无法获取收盘价: stock_code={self.stock_code}, trade_date={trade_date}")
            price = 0.0
        else:
            price = price_df.iloc[0, 0]

        return price

    @property
    def high_limit(self) -> float:
        # 获取当前交易时间
        # TODO 没有缓存作用，每次访问查询数据库
        trade_date = self.context.current_dt.strftime('%Y-%m-%d')
        df = get_factor(self.stock_code, 'up_limit', trade_date=trade_date, dividend_type=self.context.dividend_type)
        if not df.empty:
            price = df.iloc[0, 0]
        else:
            log.warning(f"无法获取涨停价：sec_code={self.stock_code}, trade_date={trade_date}")
            price = 0.0
        return price

        # # 获取基础行情数据
        # fields = ['up_limit', 'down_limit']
        # # stk_d = crud.get_mkt_stk_d(trade_date=trade_date, fields=fields, stock_lst=[self.stock_code])
        # stk_d = crud.get_mkt_stk_d(trade_date=trade_date, fields=fields, sec_code=self.stock_code)
        # return stk_d[self.stock_code]['up_limit']

    @property
    def low_limit(self) -> float:
        # 获取当前交易时间
        # TODO 没有缓存作用，每次访问查询数据库
        trade_date = self.context.current_dt.strftime('%Y-%m-%d')
        df = get_factor(self.stock_code, 'down_limit', trade_date=trade_date, dividend_type=self.context.dividend_type)
        if not df.empty:
            price = df.iloc[0, 0]
        else:
            log.warning(f"无法获取跌停价：sec_code={self.stock_code}, trade_date={trade_date}")
            price = 0.0
        return price

        # # 获取当前交易时间
        # current_dt = pd.Timestamp(self.data.datetime.datetime())
        # trade_date = current_dt.strftime('%Y-%m-%d')
        #
        # # 获取基础行情数据
        # fields = ['up_limit', 'down_limit']
        # # stk_d = crud.get_mkt_stk_d(trade_date=trade_date, fields=fields, stock_lst=[self.stock_code])
        # stk_d = crud.get_mkt_stk_d(trade_date=trade_date, fields=fields, sec_code=self.stock_code)
        # return stk_d[self.stock_code]['down_limit']

    @property
    def paused(self) -> bool:
        # suspend
        # 获取当前交易时间
        # TODO 没有缓存作用，每次访问查询数据库
        trade_date = self.context.current_dt.strftime('%Y-%m-%d')

        # 获取停复牌信息, 默认返回停牌股票的dict，key为股票代码
        suspend_dict = get_suspend_info(trade_date=trade_date, stock_lst=[self.stock_code])
        return True if self.stock_code in suspend_dict else False

    @property
    def is_st(self) -> bool:
        # 获取当前交易时间
        # TODO 没有缓存作用，每次访问查询数据库
        trade_date = self.context.current_dt.strftime('%Y-%m-%d')

        # 获取股票的历史名称
        stock_name = get_stock_name_his(sec_code=self.stock_code, trade_date=trade_date)
        is_st = True if 'ST' in stock_name or '*' in stock_name else False
        # log.debug(f"is_ST: sec_code: {self.stock_code}, trade_date = {trade_date}, name: {stock_name}, ST: {is_st}")
        return is_st

    @property
    def day_open(self) -> float:
        # 获取当前交易时间
        # TODO 没有缓存作用，每次访问查询数据库
        trade_date = self.context.current_dt.strftime('%Y-%m-%d')
        df = get_factor(self.stock_code, 'open', trade_date=trade_date, dividend_type=self.context.dividend_type)
        price = df.iloc[0, 0]
        return price

    @property
    def display_name(self):
        return self.bsc_info_dict[self.stock_code]['fullname']

    @property
    def name(self) -> str:
        # 获取当前交易时间
        trade_date = self.context.current_dt.strftime('%Y-%m-%d')

        # 获取股票的历史名称
        # TODO 没有缓存作用，每次访问查询数据库
        stock_name_dict = get_stock_name_his(sec_code=self.stock_code, trade_date=trade_date)
        return stock_name_dict['name']

    @property
    def industry_name(self) -> str:
        return self.bsc_info_dict[self.stock_code]['industry']

    @property
    def industry_code(self) -> str:
        return self.bsc_info_dict[self.stock_code]['industry']

    @property
    def start_date(self) -> datetime.date:
        # 2007-04-30
        return datetime.datetime.strptime(self.bsc_info_dict[self.stock_code]['list_date'], '%Y-%m-%d').date()

    @property
    def end_date(self):
        end_date = datetime.datetime.strptime('22000101', '%Y%m%d')
        return end_date

    @property
    def type(self):
        # TODO 默认instrument类型为股票
        return 'stock'
