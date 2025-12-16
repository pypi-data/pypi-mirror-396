import itertools
import random
import threading
from thriftpy2 import transport, protocol
from thriftpy2.rpc import make_client
from .thrift_client import thrift
from .utils import get_mac_address
from ..version import __version__ as current_version
import platform
import time
import socket
import six
import msgpack
import zlib
from .exceptions import ResponseError
import pandas as pd
from .compat import pickle_compat as pc
import json
from ..logger import log
from .request import RequestHandler

if platform.system().lower() != "windows":
    socket_error = (transport.TTransportException, socket.error, protocol.cybin.ProtocolError)
else:
    socket_error = (transport.TTransportException, socket.error)


class PQDataClient(object):
    _lock = threading.Lock()  # 类级别的锁，用于线程安全
    _instances = {}  # 类级别的字典，用于存储单例实例
    _auth_params = {}

    _default_host = "api.pinkquant.com"
    _default_port = 7500

    request_timeout = 300
    request_attempt_count = 3

    def __init__(self,
                 host=None,
                 port=None,
                 username="",
                 password="",
                 token="",
                 token_type="",
                 audience="resource-client"):
        self.host = host or self._default_host
        self.port = int(port or self._default_port)
        self.username = username
        self.password = password
        self.token = token
        self.audience = audience
        self.token_type = token_type

        assert self.host, "host is required"
        assert self.port, "port is required"
        assert self.username or self.token, "username is required"
        assert self.password or self.token, "password is required"

        self.client = None
        self.inited = False
        self.not_auth = True
        self.compress = True
        self.data_api_url = ""
        self._http_token = ""
        self.request_handler = RequestHandler()

        self._request_id_generator = itertools.count(random.choice(range(0, 1000, 10)))

    @classmethod
    def set_auth_params(cls, **params):
        if params != cls._auth_params and cls.instance():
            cls.instance()._reset()
            cls._instances['_instance'] = None
        cls._auth_params = params
        cls.instance().ensure_auth()

    def _reset(self):
        if self.client:
            self.client.close()
            self.client = None
        self.inited = False
        self.http_token = ""

    def _create_client(self):
        self.client = make_client(
            thrift.DataService,
            self.host,
            self.port,
            timeout=(self.request_timeout * 1000)
        )
        return self.client

    def ensure_auth(self):
        if self.inited:
            return

        if not self.username and not self.token:
            raise RuntimeError("未初始化")

        error, response = None, None
        for _ in range(self.request_attempt_count):
            try:
                self._create_client()  # 创建Thrift客户端
                if self.username:
                    # 用户名+密码登录
                    response = self.client.auth(self.username,
                                                self.password,
                                                self.compress,
                                                get_mac_address(),
                                                current_version, )
                else:
                    # Token登录
                    response = self.client.auth_by_token(self.token, self.audience)
                    break
            except socket_error as ex:
                error = ex
                time.sleep(0.5)
                if self.client:
                    self.client.close()
                    self.client = None
                continue
        else:
            if error and not response:
                raise error

        auth_message = zlib.decompress(response.msg).decode('utf-8')

        if not response.status:
            self._instances['_instance'] = None
            raise self.get_error(response)
        else:
            if self.not_auth:
                # log.debug("账号认证成功: %s" % auth_message)
                log.debug("账号认证成功")
                self.not_auth = False
        # 保存token
        self.token = json.loads(auth_message)['token']
        self.token_type = json.loads(auth_message)['token_type']
        self.inited = True

    def get_error(self, response):
        err = None
        if six.PY2:
            system = platform.system().lower()
            if system == "windows":
                err = Exception(response.error.encode("gbk"))
            else:
                err = Exception(response.error.encode("utf-8"))
        else:
            err = Exception(response.error)
        return err

    @classmethod
    def instance(cls):
        with cls._lock:
            _instance = cls._instances.get('_instance', None)
            if _instance is None:
                if cls._auth_params:
                    _instance = PQDataClient(**cls._auth_params)
                cls._instances['_instance'] = _instance
            return _instance

    def query(self, method, params):
        params["timeout"] = self.request_timeout
        params["request_id"] = next(self._request_id_generator)
        request = thrift.Query_Request()
        request.method_name = method
        request.params = msgpack.packb(params)
        request.token = self.token  # 每次请求都要带上token
        request.audience = self.audience  # 每次请求都要带上audience
        buffer = six.BytesIO()
        result = None
        try:
            self.ensure_auth()
            response = self.client.query(request)
            if response.status:
                msg = response.msg
                if six.PY3 and isinstance(msg, str):
                    try:
                        msg = msg.encode("ascii")
                    except UnicodeError:
                        raise ResponseError("bad msg {!r}".format(msg))
                msg = zlib.decompress(msg)
                buffer.write(msg)
                pickle_encoding = None
                if six.PY3:
                    pickle_encoding = "latin1"
                result = pc.load(buffer, encoding=pickle_encoding)
            else:
                raise self.get_error(response)
        finally:
            buffer.close()

        if not isinstance(result, dict) or "request_id" not in result:
            return result

        if params["request_id"] != result["request_id"]:
            raise ResponseError("request_id {!r} != {!r}".format(
                params["request_id"], result["request_id"]
            ))
        return result["msg"]

    def __call__(self, method, *args, **kwargs):
        err, result = None, None
        retry_count = 0
        for _ in range(self.request_attempt_count):
            retry_count += 1
            try:
                result = self.query(method, kwargs)
                break
            except socket_error as ex:
                # 达到最大重试次数，返回异常时的默认结果
                if retry_count >= self.request_attempt_count:
                    log.warning(f"达到最大重试次数，重试 {retry_count}/{self.request_attempt_count}. result={result}")

                if not self._ping_server():
                    self._reset()
                err = ex
                time.sleep(0.6)
            except ResponseError as ex:
                err = ex

        if result is None and isinstance(err, Exception):
            raise err

        return self.convert_message(result)

    def __getattr__(self, method):
        # 创建一个闭包来捕获 name，并返回一个新的函数，该函数接受 *args 和 **kwargs
        def method_wrapper(*args, **kwargs):
            return self(method, *args, **kwargs)

            # 返回闭包
        return method_wrapper

    def _ping_server(self):
        if not self.client or not self.inited:
            return False
        for _ in range(self.request_attempt_count):
            try:
                msg = self.query("ping", {})
                return msg == "pong"
            except ResponseError:
                msg = None
                continue
            except Exception:
                return False

    @classmethod
    def convert_message(cls, msg):
        if isinstance(msg, dict):
            data_type = msg.get("data_type", None)
            data_value = msg.get("data_value", None)
            if data_type is not None and data_value is not None:
                params = data_value
                if data_type.startswith("pandas"):
                    data_index_type = params.pop("index_type", None)
                    if data_index_type == "Index":
                        params["index"] = pd.Index(params["index"])
                    elif data_index_type == "MultiIndex":
                        params["index"] = (
                            pd.MultiIndex.from_tuples(params["index"])
                            if len(params["index"]) > 0 else None
                        )
                    if data_type == "pandas_dataframe":
                        dtypes = params.pop("dtypes", None)
                        msg = pd.DataFrame(**params)
                        if dtypes:
                            msg = msg.astype(dtypes, copy=False)
                    elif data_type == "pandas_series":
                        msg = pd.Series(**params)
            else:
                msg = {key: cls.convert_message(val) for key, val in msg.items()}
        return msg

    def request(self, method, url, params=None, data=None, json=None, **kwargs):
        headers = {
            "username": self.username,
            "Authorization": f"{self.token_type} {self.token}"
        }
        return self.request_handler.request(method, url, params=params, data=data, json=json, headers=headers, **kwargs)

