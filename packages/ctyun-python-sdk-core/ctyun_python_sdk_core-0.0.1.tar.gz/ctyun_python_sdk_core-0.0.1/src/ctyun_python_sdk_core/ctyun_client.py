import datetime
import json
import uuid
import requests
from typing import Dict, Any, TypeVar, Type
from ctyun_python_sdk_core import sign_util
from .constants import *

T = TypeVar('T')


class CtyunClient:
    def __init__(self, verify_tls: bool = True):
        """
        初始化天翼云客户端
        Args:
            verify_tls (bool): 是否验证TLS证书，默认为True
        """
        self.verify_tls = verify_tls if verify_tls is not None else True

    def request(self, url, method, headers=None, params=None, body=None, credential=None):
        # 过滤值为None的参数
        params_dict = {k: v for k, v in (params or {}).items() if v is not None}
        # 将请求对象转换为字典
        request_body = self._convert_to_dict(body) if body else None
        # 生成请求ID和时间
        request_id = str(uuid.uuid1())
        eop_date = datetime.datetime.now().strftime('%Y%m%dT%H%M%SZ')
        # 生成认证签名
        signature = sign_util.sign(
            credential=credential,
            params=params_dict,
            body=request_body,
            request_id=request_id,
            eop_date=eop_date
        )

        # 添加自定义header
        request_headers = headers or {}
        # 添加固定header
        request_headers.update({
            'User-Agent': 'ctyun-sdk-python',
            'Content-type': 'application/json;charset=UTF-8',
            'ctyun-eop-request-id': request_id.strip(),
            'Eop-Authorization': signature.strip(),
            'Eop-date': eop_date.strip()
        })

        # 构建查询字符串
        sorted_params_str = sign_util.get_sorted_params(params_dict)
        query = sign_util.params_to_query_string(sorted_params_str)

        # 打印请求信息
        print("Request URL: ", url)
        print("Request Headers: ", request_headers)
        if query:
            print("Request Query: ", query)
        if request_body is not None:
            print("Request Body: ", request_body)

        response = requests.request(
            method=method,
            url=url,
            headers=request_headers,
            params=query,
            json=request_body,
            verify=self.verify_tls
        )
        return response

    @staticmethod
    def handle_response(response: requests.Response, response_class: Type[T]) -> T:
        # 打印响应信息
        print("Response Status:", response.status_code)
        print("Response Headers:", dict(response.headers))
        print("Response Body:", response.text)
        # 检查状态码是否成功 (200-300)
        if 200 <= response.status_code <= 300:
            return response_class.from_dict(response.json())
        else:
            # 处理错误响应
            response_text = response.text if response.text else "{}"
            error_response = json.loads(response_text)
            # add httpCode
            error_response[HTTP_CODE] = response.status_code
            # add traceId
            error_response[TRACEID] = response.headers.get(X_TRACE_ID, '')
            # 兼容IT CTAPI网关的报错格式
            error_response[ERROR] = str(error_response.get(STATUS_CODE, ''))
            error_response[ERROR_CODE] = str(error_response.get(STATUS_CODE, ''))
            error_response[STATUS_CODE] = CTAPI_FAILURE_CODE
            error_response[DESCRIPTION] = error_response.get(MESSAGE, '')
            print("Exception error_response:", error_response)

            # 生成错误响应对象
            error_cls = response_class()
            for key, value in error_response.items():
                if hasattr(error_cls, key) or key in [HTTP_CODE]:
                    setattr(error_cls, key, value)

            return error_cls

    def _convert_to_dict(self, obj: Any) -> Dict:
        """将对象转换为可序列化的字典"""
        if hasattr(obj, '__dict__'):
            return {k: self._convert_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._convert_to_dict(v) for k, v in obj.items()}
        else:
            return obj
