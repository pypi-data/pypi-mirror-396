import logging
import colorlog
import os
import threading
from logging.handlers import RotatingFileHandler


class Logger(logging.Logger):
    # 日志级别：（critical > error > warning > info > debug）
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    # 单例模式实现
    _instances = {}
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, name=None, **kwargs):
        """
        获取Logger实例，如果已存在则返回现有实例，否则创建新实例
        :param name: logger名称
        :param kwargs: 其他参数
        :return: Logger实例
        """
        if name is None:
            name = 'default_pq_logger'

        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = cls(name, **kwargs)
            return cls._instances[name]

    def __init__(self, name=None, file_name=None, console_level=None, file_level=None,
                 max_bytes=10 * 1024 * 1024, backup_count=5, date_format='%Y-%m-%d %H:%M:%S'):
        """
        自定义日志对象
        :param name: logger名称，默认输出日志到控制台
        :param file_name: 输出文件路径，为None则不输出日志到文件
        :param console_level: 控制台日志级别
        :param file_level: 日志文件的日志级别
        :param max_bytes: 单个日志文件的最大大小，默认10MB
        :param backup_count: 保留的日志文件数量，默认5个
        :param date_format: 日期格式，默认'%Y-%m-%d %H:%M:%S'
        """
        if name is None:
            name = 'default_pq_logger'

        # 调用父类初始化
        super().__init__(name)

        # 阻止日志消息从当前Logger向父级Logger传递
        self.propagate = False

        if console_level is None:
            console_level = self.DEBUG

        if file_level is None:
            file_level = self.WARNING  # 默认只有warning及以上级别才会写入日志文件

        # 指定最低日志级别：（critical > error > warning > info > debug）
        self.setLevel(level=self.DEBUG)

        # 控制台输出不同级别日志颜色设置
        self.color_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'purple',
        }

        # 保存配置
        self.date_format = date_format
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # -------------------------
        # 输出到控制台
        # 日志格化字符串
        # -------------------------
        self.add_console_handler(level=console_level)

        # -------------------------
        # 输出到文件
        # -------------------------
        if file_name:
            self.add_file_handler(file_name=file_name, level=file_level)

    def __enter__(self):
        """
        上下文管理器入口
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口，关闭所有处理器
        """
        self.close()

    def close(self):
        """
        关闭所有处理器
        """
        for handler in self.handlers[:]:
            try:
                handler.close()
                self.removeHandler(handler)
            except Exception as e:
                # 记录错误但不抛出异常
                print(f"关闭处理器时出错: {e}")

    def set_name(self, name):
        """
        设置logger的名称，如果此名称的logger不存在，则创建一个新的logger
        如果新建的logger，需要通过：add_console_handler()或者add_file_handler()输出到控制台或者文件
        :param name: logger名称
        :return:
        """
        # 由于Logger类继承自logging.Logger，这里需要重新创建一个新的Logger实例
        # 保存当前的handlers
        handlers = self.handlers[:]
        # 清除当前handlers
        for handler in handlers:
            self.removeHandler(handler)

        # 创建新的Logger实例
        new_logger = Logger(name=name)

        # 将当前实例的属性复制到新实例
        self.__dict__.update(new_logger.__dict__)

        # 重新添加handlers
        for handler in handlers:
            self.addHandler(handler)

    def set_level(self, level=logging.INFO):
        """
        设置日志级别
        :param level: 日志级别
        """
        self.setLevel(level)

    def add_console_handler(self, level=logging.DEBUG, fmt=None):
        """
        输出到控制台
        :param level: 日志级别
        :param fmt: 日志格式，如果为None则使用默认格式
        :return:
        """
        try:
            if fmt is None:
                fmt = '%(log_color)s%(asctime)s: %(levelname)s %(message)s'

            console_formatter = colorlog.ColoredFormatter(
                fmt=fmt,
                log_colors=self.color_config,
                datefmt=self.date_format
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(level)
            self.addHandler(console_handler)
        except Exception as e:
            print(f"添加控制台处理器时出错: {e}")

    def add_file_handler(self,
                         file_name: str,
                         level=logging.WARNING,
                         fmt=None,
                         max_bytes=None,
                         backup_count=None,
                         json: bool = False,
                         verbose: bool = False):
        """
        输出到文件
        :param file_name: 日志文件路径
        :param level: 日志级别
        :param fmt: 日志格式，如果为None则使用默认格式
        :param max_bytes: 单个日志文件的最大大小，如果为None则使用默认值
        :param backup_count: 保留的日志文件数量，如果为None则使用默认值
        :param json: 是否以JSON格式输出日志，默认为False
        :param verbose: 是否使用详细的JSON格式（仅当json=True时有效），默认为False
        :return:
        """
        try:
            # 检查是否已经存在相同文件名的FileHandler
            file_path = os.path.abspath(file_name)
            for handler in self.handlers:
                if isinstance(handler,
                              (logging.FileHandler, RotatingFileHandler)) and handler.baseFilename == file_path:
                    # 如果已存在相同文件名的FileHandler，则更新其日志级别
                    handler.setLevel(level)
                    return

            # 如果不存在相同文件名的FileHandler，则创建新的
            import json_log_formatter

            # 确保日志目录存在
            log_dir = os.path.dirname(file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # 使用RotatingFileHandler替代FileHandler，支持日志轮转
            max_bytes = max_bytes or self.max_bytes
            backup_count = backup_count or self.backup_count

            file_handler = RotatingFileHandler(
                filename=file_name,
                mode='a',
                encoding='utf-8',
                maxBytes=max_bytes,
                backupCount=backup_count
            )

            if fmt is None:
                if json:
                    if verbose:
                        file_formatter = json_log_formatter.VerboseJSONFormatter()
                    else:
                        file_formatter = json_log_formatter.JSONFormatter()
                else:
                    file_formatter = logging.Formatter(
                        fmt='%(asctime)s: %(levelname)s %(message)s',
                        datefmt=self.date_format
                    )
            else:
                file_formatter = logging.Formatter(fmt=fmt, datefmt=self.date_format)

            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(level)
            self.addHandler(file_handler)
        except Exception as e:
            print(f"添加文件处理器时出错: {e}")

    def remove_file_handler(self, file_name: str):
        """
        删除输出到文件的handler
        :param file_name: 日志文件路径
        :return:
        """
        try:
            # 遍历logger的handlers列表
            for handler in list(self.handlers):
                # 检查handler是否是FileHandler或RotatingFileHandler且其文件名匹配给定的文件名
                if isinstance(handler, (logging.FileHandler, RotatingFileHandler)):
                    # handler.baseFilename 为绝对路径
                    if handler.baseFilename == os.path.abspath(file_name):
                        # 从logger的handlers列表中移除handler
                        self.removeHandler(handler)
                        # 关闭handler以释放资源
                        handler.close()
                        # 删除对它的引用
                        del handler
                        break  # 如果只期望移除一个匹配的handler，则退出循环
        except Exception as e:
            print(f"移除文件处理器时出错: {e}")


# 创建默认的全局logger
log = Logger.get_instance(name='default_pq_logger')

# ---------------------------------------------------------
# 外部可以访问的列表
# ---------------------------------------------------------
__all__ = ["log", "Logger"]
__all__.extend([name for name in globals().keys() if name.startswith("get")])
