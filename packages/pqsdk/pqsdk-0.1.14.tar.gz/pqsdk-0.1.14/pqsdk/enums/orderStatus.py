from enum import Enum
from pqsdk import pqconstant


class OrderStatus(Enum):
    # 排队的委托：代办
    queue_pending = pqconstant.QUEUED_ORDER_STATUS_PENDING
    # 排队的委托：已报，委托到券商
    queue_reported = pqconstant.QUEUED_ORDER_STATUS_REPORTED
    # 排队的委托：已撤，从队列中撤销
    queue_canceled = pqconstant.QUEUED_ORDER_STATUS_CANCELED

    # 订单新创建未委托，用于盘前/隔夜单，订单在开盘时变为 open 状态开始撮合
    new = 8

    # 订单未完成, 无任何成交
    open = 0

    # 订单未完成, 部分成交
    filled = 1

    # 订单完成, 已撤销, 可能有成交, 需要看 Order.filled 字段
    canceled = 2

    # 订单完成, 交易所已拒绝, 可能有成交, 需要看 Order.filled 字段
    rejected = 3

    # 订单完成, 全部成交, Order.filled 等于 Order.amount
    held = 4

    # 订单取消中，只有实盘会出现，回测/模拟不会出现这个状态
    pending_cancel = 9
