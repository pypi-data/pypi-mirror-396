class CtyunRequestException(Exception):
    """天翼云请求异常"""
    
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
    
    def __str__(self) -> str:
        error_msg = self.message
        if self.status_code:
            error_msg = f"{error_msg} (Status Code: {self.status_code})"
        if self.response:
            error_msg = f"{error_msg}\nResponse: {self.response}"
        return error_msg

class CtyunCredentialException(Exception):
    """天翼云认证异常"""
    pass

class CtyunConfigException(Exception):
    """天翼云配置异常"""
    pass

class CtyunValidationException(Exception):
    """天翼云参数验证异常"""
    pass 