import requests
from typing import Generator


class Request:
    def __init__(self, trust_env: bool = False):
        """
        description:
            初始化请求客户端
        parameters:
            trust_env(bool): 是否信任环境变量中的代理设置，默认为False
        """
        self.session = requests.Session()
        self.session.trust_env = trust_env

    def _post(
        self,
        url: str,
        data: dict = {},
        headers: dict = {"Content-Type": "application/json"},
        timeout: int = 0,
    ):
        """
        description:
            内部POST请求方法
        parameters:
            url(str): 请求URL
            data(dict): 请求数据
            headers(dict): 请求头
            timeout(int): 请求超时时间（秒），0表示不设置超时
        return:
            response(requests.Response): 响应对象
        """
        kwargs = {
            "url": url,
            "json": data,
            "headers": headers,
        }
        if timeout:
            kwargs["timeout"] = timeout
        response = self.session.post(**kwargs)
        return response

    def _get(self, url: str, params: dict = {}, headers: dict = {}, timeout: int = 0):
        """
        description:
            内部GET请求方法
        parameters:
            url(str): 请求URL
            params(dict): 请求参数
            headers(dict): 请求头
            timeout(int): 请求超时时间（秒），0表示不设置超时
        return:
            response(requests.Response): 响应对象
        """
        kwargs = {
            "url": url,
            "params": params,
            "headers": headers,
        }
        if timeout:
            kwargs["timeout"] = timeout
        response = self.session.get(**kwargs)
        return response

    def post(
        self,
        url: str,
        data: dict = {},
        headers: dict = {"Content-Type": "application/json"},
        timeout: int = 0,
    ) -> tuple[dict, bool]:
        """
        description:
            发送 POST 请求
        parameters:
            url(str): 请求 URL
            data(dict): 请求数据
            headers(dict): 请求头
            timeout(int): 请求超时时间
        return:
            response(dict): 响应数据
            flag(bool): 请求是否成功
        """
        response = self._post(url, data, headers, timeout)

        if response.status_code == 200:
            return response.json(), True
        else:
            print(response.status_code, response.text)
            return {
                "status_code": response.status_code,
                "message": response.text,
            }, False

    def get(
        self,
        url: str,
        params: dict = {},
        headers: dict = {},
        timeout: int = 0,
    ) -> tuple[dict, bool]:
        """
        description:
            发送 GET 请求
        parameters:
            url(str): 请求 URL
            params(dict): 请求参数
            headers(dict): 请求头
            timeout(int): 请求超时时间
        return:
            response(dict): 响应数据
            flag(bool): 请求是否成功
        """
        response = self._get(url, params, headers, timeout)

        if response.status_code == 200:
            return response.json(), True
        else:
            print(response.status_code, response.text)
            return {
                "status_code": response.status_code,
                "message": response.text,
            }, False

    def post_stream(
        self,
        url: str,
        data: dict = {},
        headers: dict = {"Content-Type": "application/json"},
        timeout: int = 0,
    ) -> Generator[str, None, None]:
        """
        description:
            发送 POST 流式请求
        parameters:
            url(str): 请求 URL
            data(dict): 请求数据
            headers(dict): 请求头
            timeout(int): 请求超时时间
        return:
            response(generator): 响应数据生成器
        """
        response = self._post(url, data, headers, timeout)
        if response.status_code == 200:
            return response.iter_lines()

    def get_stream(
        self,
        url: str,
        params: dict = {},
        headers: dict = {},
        timeout: int = 0,
    ) -> Generator[str, None, None]:
        """
        description:
            发送 GET 流式请求
        parameters:
            url(str): 请求 URL
            params(dict): 请求参数
            headers(dict): 请求头
            timeout(int): 请求超时时间
        return:
            response(generator): 响应数据生成器
        """
        response = self._get(url, params, headers, timeout)
        if response.status_code == 200:
            return response.iter_lines()

    def __del__(self):
        """
        description:
            析构函数，关闭会话连接
        """
        self.session.close()
