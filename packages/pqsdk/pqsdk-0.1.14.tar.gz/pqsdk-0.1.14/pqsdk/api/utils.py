# coding=utf-8
from functools import wraps
from ..utils import file_util as fu
import json
import os


def get_mac_address():
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:])


def assert_auth(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        from .client import PQDataClient
        # 如果未登录，登录远端并初始化
        if not PQDataClient.instance() or not PQDataClient.instance().inited:
            # client未初始化，尝试从环境变量或者配置文件登录并初始化
            config_file = 'config.sdk.json'
            if "AUTH_TOKEN" in os.environ:
                # 从环境变量的token登录
                PQDataClient.set_auth_params(token=os.environ.get("AUTH_TOKEN"),
                                             host=os.environ.get("AUTH_HOST"),
                                             port=os.environ.get("AUTH_PORT"),
                                             audience=os.environ.get("AUTH_AUDIENCE"))
            elif fu.check_path_exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    sdk_config = json.loads(f.read())
                # 从配置文件的token登录
                PQDataClient.set_auth_params(host=sdk_config['host'],
                                             token=sdk_config['token'],
                                             audience=sdk_config['audience'])

        # 检查是否登录成功
        if not PQDataClient.instance() or not PQDataClient.instance().inited:
            # 登录失败
            raise Exception("请先进行登录认证")
        else:
            return func(*args, **kwargs)

    return _wrapper
