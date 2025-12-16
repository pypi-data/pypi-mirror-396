# coding=utf-8
import pqsdk.backtest as backtest
import pqsdk.utils.file_util as fu
from .logger import log


def run_backtest(file_path: str,
                 parameters: dict,
                 plot: bool,
                 save_metrics: bool,
                 save_orders: bool,
                 save_inout_cash: bool
                 ):
    """
    执行策略回测

    :param file_path: 是回测脚本的路径
    :param parameters: 是一个字典，包含了所有通过 -p 传递的参数
    :param plot: 是一个布尔值，表示是否绘图
    :param save_metrics: 是否保存回测结果
    :param save_orders: 是否保存委托明细信息
    :param save_inout_cash: 是否保存出入金历史
    :return:
    """

    # 回测参数
    params = {
        "cash": parameters.get('cash', 1000000),  # 初始资金
        "start_date": parameters.get("start_date", "2024-03-01"),  # 回测开始日期
        "end_date": parameters.get("end_date", "2024-03-17"),  # 回测介绍日期
        "benchmark": parameters.get("benchmark", "000300.SH"),  # 行情基准
        "stock_pool": parameters.get("stock_pool", "000300.SH").split(","),  # 逗号分隔的股票池
        "unit": parameters.get("unit", '1d'),  # 行情周期
        "adjust_period": parameters.get("adjust_period", 5),  # 调仓周期，默认5个交易日
        "hold_maxsize": parameters.get("hold_maxsize", 10),  # 默认选股个数
    }

    # 添加额外的参数
    for k, v in parameters.items():
        if k not in params:
            params[k] = v

    # 策略代码
    if not fu.check_path_exists(file_path):
        log.error(f"输入的策略文件路径不存在: -f {file_path}")
        exit(-1)
    with open(file_path, 'r', encoding='utf-8') as f:
        script = f.read()

    # 执行回测
    results = backtest.execute(parameters=params, script=script)

    if plot:
        backtest.tearsheet(results)

    if save_metrics:
        backtest.save_metrics(results=results)

    if save_orders:
        backtest.save_orders(results=results)

    if save_inout_cash:
        backtest.save_inout_cash(results=results)


