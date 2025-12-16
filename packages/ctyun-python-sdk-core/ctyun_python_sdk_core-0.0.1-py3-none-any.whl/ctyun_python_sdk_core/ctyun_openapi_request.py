from typing import Dict, Any


class CtyunOpenAPIRequest:
    """天翼云OpenAPI请求基类"""

    def __init__(self):
        # 业务自定义headers，非签名相关headers
        self._custom_headers: Dict[str, str] = {}

    def set_header(self, key: str, value: str) -> 'CtyunOpenAPIRequest':
        """设置单个Header"""
        if key and value is not None:
            self._custom_headers[key] = str(value)
        return self

    def set_headers(self, headers: Dict[str, str]) -> 'CtyunOpenAPIRequest':
        """批量设置Headers"""
        if headers:
            for k, v in headers.items():
                self.set_header(k, v)
        return self

    def set_multi_value_header(self, key: str, *values: str) -> 'CtyunOpenAPIRequest':
        """设置多值Header的推荐方法"""
        if key and values:
            # 按照RFC 7230规范，使用逗号+空格分隔
            formatted_value = ", ".join(str(v) for v in values if v is not None)
            if formatted_value:
                self._custom_headers[key] = formatted_value
        return self

    def get_headers(self) -> Dict[str, str]:
        """获取所有业务自定义headers"""
        return self._custom_headers.copy()

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """将请求对象转换为字典，排除_custom_headers"""
        return {
            k: v for k, v in self.__dict__.items()
            if k != '_custom_headers'
        }
