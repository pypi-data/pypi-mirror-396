# coding=utf-8
from .main import BacktestExecutor
import pqsdk.utils.file_util as fu
import json
import pqsdk.api as pqdatasdk
from pqsdk import log
from pqsdk.api import PQDataClient
import pandas as pd
import quantstats as qs
from pathlib import Path
import datetime
import os


def execute(parameters: dict, script: str = None, strategy_file: str = None, task=None):
    """
    执行回测
    :param parameters: 回测参数字典
    :param script: 策略脚本
    :param strategy_file: 策略脚本文件
    :param task: celery task
    :return:
    """
    if not PQDataClient.instance() or not PQDataClient.instance().inited:
        log.debug("登录pqsdk服务端点")
        config_file = 'config.sdk.json'
        if not fu.check_path_exists(config_file):
            err_msg = "未找到配置文件. 请先运行命令进行配置: pqsdk config"
            log.error(err_msg)
            raise Exception(err_msg)

        with open(config_file, 'r', encoding='utf-8') as f:
            sdk_config = json.loads(f.read())
        pqdatasdk.auth_by_token(token=sdk_config['token'], host=sdk_config['host'], audience=sdk_config['audience'])

    if strategy_file:
        strategy_file = os.path.splitext(strategy_file)[0]
    kwargs = {"parameters": parameters, "script": script, "strategy_file": strategy_file}
    executor = BacktestExecutor(kwargs=kwargs, task=task)
    results = executor.run()
    return results


def tearsheet(results: dict, save_path="storage/reports"):
    """
    保存回测结果到Tearsheet

    :param save_path: 保存路径
    :param results:
    :return None: .
    """
    log.info("生成Tearsheet, 请稍后...")

    # 策略收益率
    strat_return = results['analysis']['time_return']['strat_return']
    strat_df = pd.DataFrame({'strat_return': strat_return})
    strat_df.index = pd.to_datetime(strat_df.index)
    strat_returns = strat_df['strat_return']

    # benchmark收益率
    bchmk_return = results['analysis']['time_return']['bchmk_return']
    bchmk_df = pd.DataFrame({'bchmk_return': bchmk_return})
    bchmk_df.index = pd.to_datetime(bchmk_df.index)
    # 重命名benchmark的Column名称，用于Tearsheet显示
    bchmk_df = bchmk_df.rename(columns={"bchmk_return": results['benchmark']})
    # bchmk_df = bchmk_df.loc[stats_df.index]  # 以持仓日期列表保留benchmark的记录
    bchmk_returns = bchmk_df[results['benchmark']]

    # tearsheet保存路径
    ts_path = Path(save_path)
    ts_path.mkdir(parents=True, exist_ok=True)
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = (
            "tearsheet"
            + "-"
            + time_str.replace("-", "").replace(":", "").replace(" ", "-")
            + ".html"
    )
    filepath = ts_path / filename

    title = f"回测报告 {time_str}"
    qs.reports.html(
        strat_returns,
        benchmark=bchmk_returns,
        title=title,
        output=filepath,
        download_filename=filepath
    )

    log.info(f"Tearsheet创建完成，路径：{filepath}")


def save_metrics(results: dict, save_path="storage/metrics"):
    """
    保存最终回测结果
    :param results:
    :param save_path: 保存路径
    :return:
    """
    # 计算总市值时间序列
    cost = results['analysis']['time_return']['cost']
    market_values = results['analysis']['time_return']['market_value']
    pnls = results['analysis']['time_return']['pnl']
    principal = results['analysis']['time_return']['principal']
    cash = results['analysis']['time_return']['cash']
    asset = results['analysis']['time_return']['asset']
    position_size = results['analysis']['time_return']['position_size']
    nav = results['analysis']['time_return']['nav']
    strat_return = results['analysis']['time_return']['strat_return']
    bchmk_returns = results['analysis']['time_return']['bchmk_return']
    metrics_df = pd.DataFrame({'cost': cost,  # 交易成本
                               'market_value': market_values,  # 总市值
                               'pnl': pnls,  # 盈亏
                               'principal': principal,  # 本金
                               'cash': cash,  # 现金
                               'asset': asset,  # 总资产
                               'position_size': position_size,  # 仓位
                               'nav': nav,  # 净值
                               'strat_return': strat_return,  # 策略收益率
                               'bchmk_return': bchmk_returns  # 基准收益率
                               })
    metrics_df.index = pd.to_datetime(metrics_df.index)
    metrics_df.index.name = "trade_date"
    metrics_df['cum_return'] = (1 + metrics_df['strat_return']).cumprod() - 1  # 累计收益率

    run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = Path(save_path)
    file_path.mkdir(parents=True, exist_ok=True)
    filename = ("results" + "_" + run_time.replace("-", "").replace(":", "").replace(" ", "_") + ".csv")
    file_path = file_path / filename
    log.info(f"save metrics data: {file_path}")
    metrics_df.to_csv(file_path, index=True)


def save_orders(results: dict, save_path="storage/orders"):
    orders_df: pd.DataFrame = results['orders']
    run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = Path(save_path)
    file_path.mkdir(parents=True, exist_ok=True)
    filename = ("orders" + "_" + run_time.replace("-", "").replace(":", "").replace(" ", "_") + ".csv")
    file_path = file_path / filename
    log.info(f"save orders data: {file_path}")
    orders_df.to_csv(file_path, index=False)


def save_inout_cash(results: dict, save_path="storage/inout_cash"):
    df: pd.DataFrame = results['inout_cash']
    run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_path = Path(save_path)
    file_path.mkdir(parents=True, exist_ok=True)
    filename = ("inout_cash" + "_" + run_time.replace("-", "").replace(":", "").replace(" ", "_") + ".csv")
    file_path = file_path / filename
    log.info(f"save inout_cash data: {file_path}")
    df.to_csv(file_path, index=False)


# ---------------------------------------------------------
# 外部可以访问的列表
# ---------------------------------------------------------
__all__ = ["execute", "tearsheet", "save_metrics", "save_orders", "save_inout_cash"]
