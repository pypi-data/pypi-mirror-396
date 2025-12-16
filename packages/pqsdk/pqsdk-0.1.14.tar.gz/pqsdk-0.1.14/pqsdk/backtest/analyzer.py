from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from pqsdk.api import get_history


class AbstractAnalyzer(ABC):
    """
    分析器抽象函数
    """
    context = None

    def set_context(self, context):
        """
        设置回测的上下文对象
        :param context:
        :return:
        """
        self.context = context
        return self

    @abstractmethod
    def start(self):
        """
        在回测开始之前调用,对应第0根bar
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def next(self):
        """
        策略正常运行阶段, 每个Bar执行一次
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        """
        策略结束时执行
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_analysis(self):
        """
        获取分析器结果
        :return:
        """
        raise NotImplementedError


class TimeReturn(AbstractAnalyzer):
    """
    获取Portfolio的收益情况
    """

    def __init__(self):
        # datetimes
        self.datetimes = []
        # 持仓成本
        self.cost = []
        # 持仓市值
        self.market_values = []
        # 盈亏：profit and loss
        self.pnls = []
        # 本金
        self.principal = []
        # 现金
        self.cash = []
        # 总资产
        self.assets = []
        # 仓位
        self.position_size = []
        # 净值
        self.navs = []
        # 收益率
        self.strat_returns = []

        # benchmark returns
        self.bchmk_returns = []

    def start(self):
        pass

    def get_metrics(self):
        """
        根据投资的的委托数据，出入金数据和最新的价格数据，计算投资组合的重要Metrics，比如：
            1. cost：持仓交易成本，截止当前的持仓成本余额
            2. market_value：持仓市值，截止当前的持仓市值，由最新的持仓标的价格计算所得。如果投资组合已经被全部平仓，则持仓市值为0，此时持仓成本为正数为亏损，持仓成本为负数为盈利。
            3. pnl：盈亏(profit and loss)，等于持仓市值 - 持仓成本 = market_value - cost。
            4. principal：本金，截止目前为止的投资组合出入金汇总。
            5. cash：现金，即截止今日剩余现金，等于本金 - 成本 = principal - cost
            6. asset：资产，等于现金 + 持仓市值 = cash + market_value
            7. position_size：仓位，等于持仓市值/资产 = market_value / asset
            8. nav：净值(Net Asset Value)，等于资产/本金 = asset / principal
            9. 累计收益率：Cumulative Return = NAV - 1
        :return:
        """
        # 获取委托明细数据
        df = pd.DataFrame(self.context.orders)
        if df.empty:
            metrics_dict = {'cost': 0, 'market_value': 0, 'pnl': 0}
        else:
            df['cost'] = df['volume'] * df['price']
            df = df[["sec_code", "trade_date", "is_buy", "volume", "cost"]]

            # volume, amount: 买单为正数，卖单为负数
            df['volume'] = np.where(df['is_buy'], df['volume'], df['volume'] * -1)
            df['cost'] = np.where(df['is_buy'], df['cost'], df['cost'] * -1)

            # 计算每个股票的目前持仓sum(volume)、成本sum(cost)
            stock_df = df.groupby(['sec_code'])[['volume', 'cost']].sum()
            stock_df = stock_df.reset_index()

            # 获取目前持仓的最新股票价格
            sec_code_lst = stock_df['sec_code'].unique().tolist()
            if self.context.unit == '1d':
                price_df = get_history(limit=1,
                                       end_date=self.context.current_dt.strftime('%Y-%m-%d'),
                                       timeframe=self.context.unit,
                                       field='close',
                                       symbol=sec_code_lst,
                                       dividend_type=self.context.dividend_type).T

                # price_df = get_factor(trade_date=self.context.current_dt.strftime('%Y-%m-%d'),
                #                       timeframe=self.context.unit,
                #                       factor='close',
                #                       symbol=sec_code_lst,
                #                       dividend_type=self.context.dividend_type,
                #                       expect_df=True)

            else:  # unit in ['1m', '5m']
                price_df = get_history(limit=1,  # 防止数据库中的准确的分钟级别数据丢失的时候，获取前一分钟
                                       end_date=self.context.current_dt.strftime('%Y-%m-%d'),
                                       end_datetime=self.context.current_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                       timeframe=self.context.unit,
                                       field='close',
                                       symbol=sec_code_lst,
                                       dividend_type=self.context.dividend_type).T

                # price_df = get_factor(trade_date=self.context.current_dt.strftime('%Y-%m-%d'),
                #                       start_datetime=self.context.current_dt.strftime('%Y-%m-%d %H:%M:%S'),
                #                       end_datetime=self.context.current_dt.strftime('%Y-%m-%d %H:%M:%S'),
                #                       timeframe=self.context.unit,
                #                       factor='close',
                #                       symbol=sec_code_lst,
                #                       dividend_type=self.context.dividend_type,
                #                       expect_df=True)

            # 或通过层级位置删除（symbol是第0层, trade_date或者datetime是第1层）
            # price_df = price_df.droplevel(1)

            price_df = price_df.reset_index()
            price_df.columns = ["sec_code", "last_price"]
            stock_df = pd.merge(stock_df, price_df, on='sec_code')

            # 计算最新的持仓市值，盈亏
            stock_df['market_value'] = stock_df['volume'] * stock_df['last_price']
            stock_df['pnl'] = stock_df['market_value'] - stock_df['cost']

            # 统计投资组合基本的Metrics
            metrics_dict = stock_df[['cost', 'market_value', 'pnl']].sum().to_dict()

        # 本金: 出入金汇总
        cash_df = pd.DataFrame(self.context.inout_cash_his)
        metrics_dict['principal'] = cash_df['cash'].sum()

        # 截止今日剩余现金: 本金汇总 - 成本汇总
        metrics_dict['cash'] = metrics_dict['principal'] - metrics_dict['cost']
        # 资产：
        metrics_dict['asset'] = metrics_dict['cash'] + metrics_dict['market_value']
        # 仓位
        metrics_dict['position_size'] = metrics_dict['market_value'] / metrics_dict['asset']
        # 净值: Net Asset Value
        metrics_dict['nav'] = metrics_dict['asset'] / metrics_dict['principal']

        return metrics_dict

    def next(self):
        if self.context.unit in ['1d']:
            self.datetimes.append(self.context.current_dt.strftime('%Y-%m-%d'))
        else:
            self.datetimes.append(self.context.current_dt.strftime('%Y-%m-%d %H:%M:%S'))

        # 获取Metrics
        metrics_dict = self.get_metrics()

        # 根据净值的变化计算收益率。如果算累计收益率：Cumulative Return = NAV - 1
        if len(self.navs) > 0:
            start_return = metrics_dict['nav'] / self.navs[-1] - 1

        else:
            start_return = 0.0

        self.cost.append(metrics_dict['cost'])
        self.market_values.append(metrics_dict['market_value'])
        self.pnls.append(metrics_dict['pnl'])
        self.principal.append(metrics_dict['principal'])
        self.cash.append(metrics_dict['cash'])
        self.assets.append(metrics_dict['asset'])
        self.position_size.append(metrics_dict['position_size'])
        self.navs.append(metrics_dict['nav'])
        self.strat_returns.append(start_return)
        self.bchmk_returns.append(self.context.benchmark_value)

    def stop(self):
        pass

    def get_analysis(self):
        return {"cost": pd.Series(self.cost, index=self.datetimes, name='returns'),
                "market_value": pd.Series(self.market_values, self.datetimes, name='total_values'),
                "pnl": pd.Series(self.pnls, self.datetimes, name='market_values'),
                "principal": pd.Series(self.principal, self.datetimes, name='cash'),
                "cash": pd.Series(self.cash, self.datetimes, name='pnls'),
                "asset": pd.Series(self.assets, self.datetimes, name='bchmk_returns'),
                "position_size": pd.Series(self.position_size, self.datetimes, name='bchmk_returns'),
                "nav": pd.Series(self.navs, self.datetimes, name='bchmk_returns'),
                "strat_return": pd.Series(self.strat_returns, self.datetimes, name='bchmk_returns'),
                "bchmk_return": pd.Series(self.bchmk_returns, self.datetimes, name='bchmk_returns'),
                }
