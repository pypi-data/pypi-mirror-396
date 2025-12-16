from .logger import log
from .api import GlobalObject
from .utils.threading_utils import async_run

# 创建全局可以访问且可序列化的对象
g = GlobalObject()

__all__ = [
    "log",
    "g",
    "GlobalObject",
    "async_run"
]
