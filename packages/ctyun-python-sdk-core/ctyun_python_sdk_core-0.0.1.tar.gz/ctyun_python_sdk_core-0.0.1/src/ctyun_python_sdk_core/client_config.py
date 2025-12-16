class ClientConfig:
    def __init__(self, endpoint: str, access_key_id: str, access_key_secret: str, verify_tls: bool = True):
        """
        初始化客户端配置
        Args:
            endpoint (str): 服务端点地址
            access_key_id (str): ak
            access_key_secret (str): sk
            verify_tls (bool): 是否校验TLS证书，默认为True
        """
        self.endpoint = endpoint
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.verify_tls = verify_tls
