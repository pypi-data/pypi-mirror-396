import requests
import time
from ..logger import log


class RequestHandler:
    request_attempt_count = 3

    def __init__(self):
        """session管理器"""
        self.session = requests.session()

    def request(self, method, url, params=None, data=None, json=None, headers=None, **kwargs):
        """
        统一的请求函数
        :param method:
        :param url:
        :param params:
        :param data:
        :param json:
        :param headers:
        :param kwargs:
        :return:
        """
        error, response = None, None
        for _ in range(self.request_attempt_count):
            try:
                response = self.session.request(method, url,
                                                params=params,
                                                data=data,
                                                json=json,
                                                headers=headers,
                                                **kwargs)
            except Exception as ex:
                error = ex
                time.sleep(0.5)
                response = None
                log.error(f"访问失败，重试")
                continue
        else:
            if error:
                raise error

        return response

    def post(self, url, params=None, data=None, json=None, headers=None, **kwargs):
        """
        post请求

        :param url:
        :param params:
        :param data:
        :param json:
        :param headers:
        :param kwargs:
        :return:
        """
        return self.request("post", url, params=params, data=data, json=json, headers=headers, **kwargs)

    def get(self, url, params=None, data=None, json=None, headers=None, **kwargs):
        """
        get请求

        :param url:
        :param params:
        :param data:
        :param json:
        :param headers:
        :param kwargs:
        :return:
        """
        return self.request("get", url, params=params, data=data, json=json, headers=headers, **kwargs)

    def close_session(self):
        """关闭session"""
        self.session.close()
