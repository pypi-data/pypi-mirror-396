# pqsdk

#### 介绍
品宽量化交易平台提供的本地化SDK，支持使用熟悉的工具进行量化程序开发与回测

### 安装方法
```shell
# 首次安装, 在项目的根目录下添加requirements.txt文件，增加内容如下：
Cython==3.0.11
plotly-express==0.4.1
msgpack>=0.4.7
pandas==1.5.2
requests==2.31.0
six==1.16.0
thriftpy2==0.5.2
colorlog==4.8.0
QuantStats==0.0.62
ipython==8.12.2
numpy==1.24.4
tqdm==4.65.0
pqsdk

# 在命令行执行：
pip install -r requirements.txt
# 如果安装失败，请指定PIP官方镜像源
pip install -r requirements.txt -i https://pypi.org/simple

# 安装指定的版本： pip install pqsdk==<version>
pip install pqsdk==0.0.42

# 升级版本
pip install -U pqsdk
# 如果安装失败，请指定官方镜像源
pip install -U pqsdk -i https://pypi.org/simple
```


### 使用方法
```python
from pqsdk.api import *

"""账号认证, 以品宽量化交易平台www.pinkquant.com的用户名/密码登录"""
username = 'vivian'
password = 'mypassword'
auth(username, password)

"""使用 token 认证账号"""
auth_by_token(token="")

# 获取因子数据
factor_list = ['float_share', 'pe', 'pe_ttm', 'ma_5', 'ema_5', 'dv_ratio']
df = get_factor(stock_pool=['000300.SH'], trade_date='2023-03-29', factor_list=factor_list)
print(df)
```

```shell
                            open        high  ...      volume       amount
sec_code  trade_date                          ...                         
000001.SZ 2023-03-29       12.73       12.74  ...   596064.33   750687.551
000002.SZ 2023-03-29       15.41       15.62  ...   654848.26  1012734.687
000063.SZ 2023-03-29   34.435106   34.553575  ...   782218.36  2685933.703
000069.SZ 2023-03-29         4.7        4.75  ...   324836.19   152639.669
000100.SZ 2023-03-29    3.989899    4.044431  ...  1604844.15   707678.236
...                          ...         ...  ...         ...          ...
688363.SH 2023-03-29  111.999999  113.159999  ...    30500.33   341085.693
688396.SH 2023-03-29   59.307833   61.559399  ...    75640.44   458018.471
688561.SH 2023-03-29   72.570005   72.570005  ...    87323.24   605371.703
688599.SH 2023-03-29   51.750011   52.490011  ...    149553.3   768914.461
688981.SH 2023-03-29   49.189988   50.319988  ...   708926.22  3496451.834

[300 rows x 6 columns]
                                    open   high  ...  volume      amount
sec_code  datetime                               ...                    
000001.SZ 2023-03-29 14:56:00  12.529999  12.54  ...  3274.0   4103280.0
          2023-03-29 14:57:00      12.54  12.54  ...  5943.0   7450969.0
          2023-03-29 14:58:00      12.54  12.54  ...   122.0    152976.0
          2023-03-29 14:59:00      12.54  12.54  ...     0.0         0.0
          2023-03-29 15:00:00      12.54  12.54  ...  9497.0  11900655.0

[5 rows x 6 columns]

```

## 从命令行进行回测
从Terminal命令行启动的格式：

`pqsdk backtest -f <策略程序文件> -p <key=value> --plot --save_results  --save_orders`

**系统预设了如下关于-p <key=value>的参数：**

| **参数** | **默认值** | **说明** |
| --- | --- | --- |
| cash | 1000000 | 回测初始资金 |
| start_date | 2024-03-01 | 回测开始日期 |
| end_date | 2024-03-20 | 回测结束日期 |
| benchmark | 000300.SH | 回测基准 |
| stock_pool | 000300.SH,000905.SH | 股票池，即指数代码，多个指数代码用逗号分隔 |
| unit | 1d | 基准单位，支持1d，1m |
| adjust_period | 5 | 调仓周期 |
| hold_maxsize | 10 | 最大持仓股数 |


-plot参数为布尔值，是否要生成累计收益率的Tearsheet，不指定时为False。

案例：

```powershell
pqsdk backtest -f tests/buy_and_hold.py -p cash=1000000 -p start_date=2024-03-01 -p end_date=2024-03-20 -p benchmark=000300.SH -p stock_pool=000300.SH,000905.SH -p unit=1d -p adjust_period=5 -p hold_maxsize=10  -plot
pqsdk backtest -f tests/buy_and_hold.py -p start_date=2024-03-01 -p end_date=2024-03-20 -p benchmark=000300.SH -p stock_pool=000300.SH,000905.SH
pqsdk backtest -f stop_loss_strategy.py -p cash=1000000 -p start_date=2024-03-01 -p end_date=2024-03-17 -p benchmark=000300.SH -p stock_pool=000300.SH,000905.SH -p unit=1d -p adjust_period=5 -p hold_maxsize=10  -plot
```


-save_metrics  是否保存结果到csv文件

-save_orders  是否保存委托到csv文件

## 从代码进行回测

代码案例：

```python
from pqsdk.backtest import execute, tearsheet, save_metrics, save_orders, save_inout_cash
from pqsdk import log
from pqsdk.api import *


# 回测参数
params = {
    "cash": 1000000,
    "start_date": "2024-08-20",
    "end_date": "2024-09-03",
    "benchmark": "000300.SH",
    "stock_pool": "000300.SH".split(","),
    "unit": '1d',
    "adjust_period": 5,
    "hold_maxsize": 10,
}

#
strategy_file = "buy_and_hold.py"

# 执行回测
results = execute(parameters=params, strategy_file=strategy_file)

# print(results)
tearsheet(results)
save_metrics(results)
save_orders(results)
save_inout_cash(results)


```

## 回测结果
回测结果是一个字典，包含以下内容的案例：

```python
results = {
    'benchmark': '000300.SH', 
    'analysis': {'time_return': {...}}, 
    'plot_data': {}, 
    'orders':    
    order_id   sec_code  volume     price  is_buy  avg_cost        comm            add_time  trade_date
0         1  000533.SZ   62800  4.769999    True  4.769999   25.579494 2024-01-03 15:00:00  2024-01-03
1         2  000533.SZ   62800  4.599999   False  4.769999  313.726004 2024-01-08 15:00:00  2024-01-08
2         3  000417.SZ   59600  4.973573    True  4.973573   25.364394 2024-01-10 15:00:00  2024-01-10
3         4  000417.SZ   59600  4.769180   False  4.973573  308.770614 2024-01-17 15:00:00  2024-01-17, 
'inout_cash':     
datetime     cash
0 2024-01-01  1000000}

其中: 
- results['analysis']['time_return']['strat_return'] 为策略每日收益率。
- results['analysis']['time_return']['bchmk_return'] Benchmark的收益率，与策略收益率strat_return进行对比.


'strat_return'为pd.Series，样例: 
2024-01-02    0.000000e+00
2024-01-03    0.000000e+00
2024-01-04    0.000000e+00
2024-01-05   -5.651995e-03
2024-01-08   -5.052566e-03
2024-01-09    0.000000e+00
2024-01-10    2.220446e-16
2024-01-11    4.104443e-03
2024-01-12   -5.839526e-03
2024-01-15    7.635953e-03
2024-01-16   -4.663432e-03
2024-01-17   -1.347019e-02
2024-01-18    0.000000e+00
2024-01-19    0.000000e+00
2024-01-22    0.000000e+00
2024-01-23    0.000000e+00
2024-01-24    0.000000e+00


'bchmk_return'为pd.Series，样例: 
2024-01-02   -0.013045
2024-01-03   -0.002379
2024-01-04   -0.009249
2024-01-05   -0.005360
2024-01-08   -0.012933
2024-01-09    0.001961
2024-01-10   -0.004668
2024-01-11    0.005658
2024-01-12   -0.003491
2024-01-15   -0.000989
2024-01-16    0.006083
2024-01-17   -0.021750
2024-01-18    0.014136
2024-01-19   -0.001512
2024-01-22   -0.015559
2024-01-23    0.004048
2024-01-24    0.013978

```
