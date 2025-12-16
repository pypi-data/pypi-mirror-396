# coding=utf-8
from .main import *  # noqa
from .client import PQDataClient
from ..version import __version__, version_info  # noqa
from .utils import *  # noqa


def auth(username, password, host=None, port=None):
    """账号认证"""
    PQDataClient.set_auth_params(host=host, port=port, username=username, password=password)


def auth_by_token(token, host=None, port=None, audience="resource-client"):
    """使用 token 认证账号"""
    PQDataClient.set_auth_params(host=host, port=port, token=token, audience=audience)


@assert_auth
def request(method, url, params=None, data=None, json=None, **kwargs):
    return PQDataClient.instance().request(method=method, url=url, params=params, data=data, json=json, **kwargs)


@assert_auth
def post(url, params=None, data=None, json=None, **kwargs):
    return PQDataClient.instance().request(method='post', url=url, params=params, data=data, json=json, **kwargs)


@assert_auth
def get(url, params=None, data=None, json=None, **kwargs):
    return PQDataClient.instance().request(method='get', url=url, params=params, data=data, json=json, **kwargs)


__all__ = [
    "auth",
    "auth_by_token",
    "request",
    "post",
    "get",
    "__version__"
]
__all__.extend(main.__all__)  # noqa
