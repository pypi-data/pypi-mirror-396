from collections.abc import MutableMapping
from collections import OrderedDict
from pqsdk.interface import AbstractRunInfo
from .instrument import Instrument
from pqsdk.api import get_index_members_lst


class CurrentDataCacheDict(MutableMapping):
    """
    实现字典里的数据按需获取的功能，即当读取字典里的数据的时候，再去数据库中读取数据,
    并且考虑添加缓存机制来提升性能，考虑限制缓存的大小、使用LRU算法等方式进行优化.
    """

    def __init__(self, context, run_info: AbstractRunInfo, max_size=1000):
        self.context = context
        self.run_info = run_info
        self.max_size = max_size
        self._cache = OrderedDict()

    def __getitem__(self, key):
        """
        根据股票代码的key获取股票详细信息
        :param key:
        :return:
        """
        if key in self._cache:
            # 如果key在缓存中，则将其移到最前面
            value = self._cache.pop(key)
            self._cache[key] = value
        else:
            # 如果key不在缓存中，则从数据库中读取值，并将其添加到缓存中
            value = Instrument(stock_code=key, run_info=self.run_info, context=self.context)

            if value.name is None:
                # 如果查询结果为空，则抛出KeyError异常
                raise KeyError(key)
            else:
                # 将查询结果添加到缓存中
                self._cache[key] = value
                self._enforce_max_size()

        return value

    def __setitem__(self, key, value):
        """
        将键值对添加到缓存
        :param key:
        :param value:
        :return:
        """
        if key in self._cache:
            # 如果key在缓存中，则将其移到最前面
            self._cache.pop(key)
        self._cache[key] = value

        self._enforce_max_size()

    def __delitem__(self, key):
        """
        从缓存中删除键值对
        :param key:
        :return:
        """
        del self._cache[key]

    def __iter__(self):
        """
        遍历所有键
        :return:
        """
        # 从回测的股票池的成分股获取股票列表
        stock_lst = get_index_members_lst(self.context.stock_pool,
                                          trade_date=self.context.current_dt.strftime('%Y-%m-%d'))

        for stock_code in stock_lst:
            yield Instrument(stock_code=stock_code, run_info=self.run_info, context=self.context)

    def __len__(self):
        """
        获取键的总数
        :return:
        """
        # 从回测的股票池的成分股获取股票列表
        stock_lst = get_index_members_lst(self.context.stock_pool,
                                          trade_date=self.context.current_dt.strftime('%Y-%m-%d'))

        return len(stock_lst)

    def _enforce_max_size(self):
        """
        如果缓存大小超过了max_size，则删除最旧的元素
        :return:
        """
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
