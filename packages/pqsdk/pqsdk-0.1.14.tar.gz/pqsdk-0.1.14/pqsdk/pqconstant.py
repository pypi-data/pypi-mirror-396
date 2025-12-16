# coding=utf-8


# --------------------------------------
# 常量定义模块
# 命名规范： 模块_功能_描述 = 值
# --------------------------------------

"""
市场类型
"""
# 上海市场
MARKET_SH = 0
# 深圳市场
MARKET_SZ = 1

"""
报价类型
"""
# 最新价
LATEST_PRICE = 5
# 指定价/限价
FIX_PRICE = 11
# 最优五档即时成交剩余撤销[上交所][股票]
MARKET_SH_CONVERT_5_CANCEL = 42
# 最优五档即时成交剩转限价[上交所][股票]
MARKET_SH_CONVERT_5_LIMIT = 43
# 对手方最优价格委托[上交所[股票]][深交所[股票][期权]]
MARKET_PEER_PRICE_FIRST = 44
# 本方最优价格委托[上交所[股票]][深交所[股票][期权]]
MARKET_MINE_PRICE_FIRST = 45
# 即时成交剩余撤销委托[深交所][股票][期权]
MARKET_SZ_INSTBUSI_RESTCANCEL = 46
# 最优五档即时成交剩余撤销[深交所][股票][期权]
MARKET_SZ_CONVERT_5_CANCEL = 47
# 全额成交或撤销委托[深交所][股票][期权]
MARKET_SZ_FULL_OR_CANCEL = 48

price_type = {
    LATEST_PRICE: "最新价",
    FIX_PRICE: "限价",
    MARKET_SH_CONVERT_5_CANCEL: "最优五档即时成交剩余撤销[上交所][股票]",
    MARKET_SH_CONVERT_5_LIMIT: "最优五档即时成交剩转限价[上交所][股票]",
    MARKET_PEER_PRICE_FIRST: "对手方最优价格委托[上交所[股票]][深交所[股票][期权]]",
    MARKET_MINE_PRICE_FIRST: "本方最优价格委托[上交所[股票]][深交所[股票][期权]]",
    MARKET_SZ_INSTBUSI_RESTCANCEL: "即时成交剩余撤销委托[深交所][股票][期权]",
    MARKET_SZ_CONVERT_5_CANCEL: "最优五档即时成交剩余撤销[深交所][股票][期权]",
    MARKET_SZ_FULL_OR_CANCEL: "全额成交或撤销委托[深交所][股票][期权]",
}

"""
请求结果错误码
"""
RESULT_OK_CODE_200 = 200
# 400报错
# 1、有可能是前端请求时参数拼接有问题
# 2、有可能时前端传给后端的参数类型与后端接收的参数类型不匹配，比如前端传String，后端用Integer接收,
# 3、有可能是后端的实体类没有配置无参构造方法
RESULT_ERROR_CODE_400 = 400

# 403错误
# 服务端理解你的请求，但是没有权限访问
RESULT_ERROR_CODE_403 = 403
# 404错误
# 找不到网页地址，即网页的地址不正确，还有一种可能就是后端配置不当，导致请求被拦截
RESULT_ERROR_CODE_404 = 404
# 500错误
# 明显的后端错误，可能需要前后端配合来修复
RESULT_ERROR_CODE_500 = 500
# 502错误
# 网关错误，服务器作为网关或代理，无法从上游服务器收到正确的响应
RESULT_ERROR_CODE_502 = 502

"""
请求结果状态
"""
RESULT_STATUS_OK = 'OK'
RESULT_STATUS_ERROR = 'ERROR'

"""
委托状态
"""
# 未报
ORDER_UNREPORTED: int = 48
# 待报
ORDER_WAIT_REPORTING: int = 49
# 已报
ORDER_REPORTED: int = 50
# 已报待撤
ORDER_REPORTED_CANCEL: int = 51
# 部成待撤
ORDER_PARTSUCC_CANCEL: int = 52
# 部撤
ORDER_PART_CANCEL: int = 53
# 已撤
ORDER_CANCELED: int = 54
# 部成
ORDER_PART_SUCC: int = 55
# 已成
ORDER_SUCCEEDED: int = 56
# 废单
ORDER_JUNK: int = 57
# 未知
ORDER_UNKNOWN: int = 255
# 异常
ORDER_ERROR: int = 244

order_status = {
    ORDER_UNREPORTED: '未报',
    ORDER_WAIT_REPORTING: '待报',
    ORDER_REPORTED: '已报',
    ORDER_REPORTED_CANCEL: '已报待撤',
    ORDER_PARTSUCC_CANCEL: '部成待撤',
    ORDER_PART_CANCEL: '部撤',
    ORDER_CANCELED: '已撤',
    ORDER_PART_SUCC: '部成',
    ORDER_SUCCEEDED: '已成',
    ORDER_JUNK: '废单',
    ORDER_UNKNOWN: '未知',
    ORDER_ERROR: '异常'
}

"""
账号类型
"""
# 期货
FUTURE_ACCOUNT = 1
# 股票
SECURITY_ACCOUNT = 2
# 信用
CREDIT_ACCOUNT = 3
# 期货期权
FUTURE_OPTION_ACCOUNT = 5
# 股票期权
STOCK_OPTION_ACCOUNT = 6
# 沪港通
HUGANGTONG_ACCOUNT = 7
# 深港通
SHENGANGTONG_ACCOUNT = 11

account_type = {
    FUTURE_ACCOUNT: '期货',
    SECURITY_ACCOUNT: '股票',
    CREDIT_ACCOUNT: '信用',
    FUTURE_OPTION_ACCOUNT: '期货期权',
    STOCK_OPTION_ACCOUNT: '股票期权',
    HUGANGTONG_ACCOUNT: '沪港通',
    SHENGANGTONG_ACCOUNT: '深港通'
}

"""
账号状态
"""
"""
账号状态
"""
# 无效
ACCOUNT_STATUS_INVALID = -1
# 正常
ACCOUNT_STATUS_OK = 0
# 连接中
ACCOUNT_STATUS_WAITING_LOGIN = 1
# 登陆中
ACCOUNT_STATUSING = 2
# 失败
ACCOUNT_STATUS_FAIL = 3
# 初始化中
ACCOUNT_STATUS_INITING = 4
# 数据刷新校正中
ACCOUNT_STATUS_CORRECTING = 5
# 收盘后
ACCOUNT_STATUS_CLOSED = 6
# 穿透副链接断开
ACCOUNT_STATUS_ASSIS_FAIL = 7
# 系统停用（总线使用-密码错误超限）
ACCOUNT_STATUS_DISABLEBYSYS = 8
# 用户停用（总线使用）
ACCOUNT_STATUS_DISABLEBYUSER = 9

account_status = {
    ACCOUNT_STATUS_INVALID: '无效',
    ACCOUNT_STATUS_OK: '正常',
    ACCOUNT_STATUS_WAITING_LOGIN: '连接中',
    ACCOUNT_STATUSING: '登陆中',
    ACCOUNT_STATUS_FAIL: '失败',
    ACCOUNT_STATUS_INITING: '初始化中',
    ACCOUNT_STATUS_CORRECTING: '数据刷新校正中',
    ACCOUNT_STATUS_CLOSED: '收盘后',
    ACCOUNT_STATUS_ASSIS_FAIL: '穿透副链接断开',
    ACCOUNT_STATUS_DISABLEBYSYS: '系统停用（总线使用-密码错误超限）',
    ACCOUNT_STATUS_DISABLEBYUSER: '用户停用（总线使用）'
}

"""
委托类型
"""
"""
ORDER TYPE
"""
STOCK_BUY = 23
STOCK_SELL = 24
CREDIT_BUY = 23  # 担保品买入
CREDIT_SELL = 24  # 担保品卖出
CREDIT_FIN_BUY = 27  # 融资买入
CREDIT_SLO_SELL = 28  # 融券卖出
CREDIT_BUY_SECU_REPAY = 29  # 买券还券
CREDIT_DIRECT_SECU_REPAY = 30  # 直接还券
CREDIT_SELL_SECU_REPAY = 31  # 卖券还款
CREDIT_DIRECT_CASH_REPAY = 32  # 直接还款
CREDIT_FIN_BUY_SPECIAL = 40  # 专项融资买入
CREDIT_SLO_SELL_SPECIAL = 41  # 专项融券卖出
CREDIT_BUY_SECU_REPAY_SPECIAL = 42  # 专项买券还券
CREDIT_DIRECT_SECU_REPAY_SPECIAL = 43  # 专项直接还券
CREDIT_SELL_SECU_REPAY_SPECIAL = 44  # 专项卖券还款
CREDIT_DIRECT_CASH_REPAY_SPECIAL = 45  # 专项直接还款

order_type = {
    STOCK_BUY: '买入',
    STOCK_SELL: '卖出',
    # CREDIT_BUY: '担保品买入',
    # CREDIT_SELL: '担保品卖出',
    # CREDIT_FIN_BUY: '融资买入',
    # CREDIT_SLO_SELL: '融券卖出',
    # CREDIT_BUY_SECU_REPAY: '买券还券',
    # CREDIT_DIRECT_SECU_REPAY: '直接还券',
    # CREDIT_SELL_SECU_REPAY: '卖券还款',
    # CREDIT_DIRECT_CASH_REPAY: '直接还款',
    # CREDIT_FIN_BUY_SPECIAL: '专项融资买入',
    # CREDIT_SLO_SELL_SPECIAL: '专项融券卖出',
    # CREDIT_BUY_SECU_REPAY_SPECIAL: '专项买券还券',
    # CREDIT_DIRECT_SECU_REPAY_SPECIAL: '专项直接还券',
    # CREDIT_SELL_SECU_REPAY_SPECIAL: '专项卖券还款',
    # CREDIT_DIRECT_CASH_REPAY_SPECIAL: '专项直接还款',
}

"""
Celery Task Status
"""
CELERY_TASK_STATUS_PROCESSING = 'processing'
CELERY_TASK_STATUS_FINISHED = 'finished'
CELERY_TASK_STATUS_FAILED = 'failed'
CELERY_TASK_STATUS_TERMINATED = 'terminated'

celery_task_status = {
    CELERY_TASK_STATUS_PROCESSING: '运行中',
    CELERY_TASK_STATUS_FINISHED: '已完成',
    CELERY_TASK_STATUS_FAILED: '已失败',
    CELERY_TASK_STATUS_TERMINATED: '被中止'
}

"""
Service Key
"""
SERVICE_KEY_TICK_SUBSCRIBE = "SYS:SERVICE:TICK:SUBSCRIBE"  # 订阅Tick
SERVICE_KEY_TICK_PROCESS = "SYS:SERVICE:TICK:PROCESS"  # 处理Tick
SERVICE_KEY_CALLBACK_PROCESS = "SYS:SERVICE:CALLBACK:PROCESS"  # 处理交易


"""
Service Status
"""
SERVICE_STATUS_STARTUP = 1  # 已启动
SERVICE_STATUS_CLOSED = 2  # 已关闭
SERVICE_STATUS_ABNORMAL = 3  # 有异常

service_status = {
    SERVICE_STATUS_STARTUP: "已启动",
    SERVICE_STATUS_CLOSED: "已关闭",
    SERVICE_STATUS_ABNORMAL: "有异常"
}

"""
委托队列状态
"""
QUEUED_ORDER_STATUS_PENDING = 10
QUEUED_ORDER_STATUS_REPORTED = 11
QUEUED_ORDER_STATUS_CANCELED = 12
QUEUED_ORDER_STATUS_EXPIRED = 13

queued_order = {
    QUEUED_ORDER_STATUS_PENDING: "待处理",
    QUEUED_ORDER_STATUS_REPORTED: "已委托",
    QUEUED_ORDER_STATUS_CANCELED: "已取消",
    QUEUED_ORDER_STATUS_EXPIRED: "已过期"
}

"""
交易终端代理角色
"""
BROKER_ROLE_TYPE_TRADER = 1  # 交易终端
BROKER_ROLE_TYPE_TICKER = 2  # 数据终端

broker_role_type = {
    BROKER_ROLE_TYPE_TRADER: "交易终端",
    BROKER_ROLE_TYPE_TICKER: "数据终端"
}


"""
默认的交易策略
"""
DEFAULT_STRATEGY_ID = -1

default_strategy = {
    DEFAULT_STRATEGY_ID: "默认交易策略"
}
