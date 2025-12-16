import base64
import hashlib
import hmac
import json
from typing import Optional, Set, Dict, Union, Any, Tuple, List
from urllib.parse import quote


def sign(credential, params, body, request_id, eop_date):
    """生成签名"""

    # 构建签名字符串
    header_str = f'ctyun-eop-request-id:{request_id}\neop-date:{eop_date}\n'
    query_str = get_sorted_str(params)
    body_digest = _calculate_body_digest(body)

    signature_str = f'{header_str}\n{query_str}\n{body_digest}'

    sign_date = eop_date.split('T')[0]
    k_time = _hmac_sha256(credential.sk, eop_date)
    k_ak = _hmac_sha256(k_time, credential.ak)
    k_date = _hmac_sha256(k_ak, sign_date)
    # 计算签名
    signature_base64 = base64.b64encode(_hmac_sha256(k_date, signature_str))
    sign_header = '%s Headers=ctyun-eop-request-id;eop-date Signature=%s' % (credential.ak, signature_base64.decode('utf8'))

    return sign_header

def _hmac_sha256(key, data):
    """HMAC-SHA256计算"""
    if isinstance(key, str):
        key = key.encode('utf-8')
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hmac.new(key, data, hashlib.sha256).digest()

def _calculate_body_digest(body):
    """计算请求体摘要"""
    if not body:
        return hashlib.sha256(b'').hexdigest()
    if isinstance(body, dict):
        body = json.dumps(body)
    return hashlib.sha256(body.encode('utf-8')).hexdigest()

def get_sorted_str(data):
    """获取排序后的字符串"""
    if not data:
        return ""
    if isinstance(data, str):
        data = json.loads(data)
    sorted_data = sorted(data.items(), key=lambda item: item[0])
    str_list = map(lambda x_y: '%s=%s' % (x_y[0], quote(str(x_y[1]), safe='')), sorted_data)
    return '&'.join(str_list)

def extract_header_params(
        header_params: Set[str],
        data: Optional[Union[Dict[str, Any], Set]],
        case_insensitive: bool = False,
        remove_none: bool = False
) -> Dict[str, Any]:
    """
    从 data 字典中提取 header_params 集合中指定的键值对，并从原始数据中移除这些键

    :param header_params: 需要提取的头部参数键名集合
    :param data: 原始数据字典（会被修改）或集合
    :param case_insensitive: 是否忽略键的大小写
    :param remove_none: 是否排除值为 None 的项
    :return: 只包含 header_params 中指定键的新字典
    """
    # 处理无效输入情况
    if data is None:
        return {}

    if header_params is None:
        return {}

    # 如果传入的是集合而不是字典，转换为字典
    if isinstance(data, set):
        # 将集合转换为字典，每个键的值设为 None
        data_dict = {item: None for item in data}
        # 创建一个空字典用于结果，因为集合没有键值对
        result = {}
    elif isinstance(data, dict):
        # 如果是字典，使用原始数据
        data_dict = data
        result = {}
    else:
        # 处理其他类型
        try:
            # 尝试转换为字典
            data_dict = dict(data)
            result = {}
        except TypeError:
            # 无法转换，返回空字典
            return {}

    keys_to_remove = set()  # 存储需要移除的键

    if case_insensitive:
        # 创建小写映射
        data_lower = {k.lower(): (k, v) for k, v in data_dict.items()}
        header_lower = {k.lower() for k in header_params}

        for key in header_lower:
            if key in data_lower:
                original_key, value = data_lower[key]

                # 如果需要，跳过 None 值
                if remove_none and value is None:
                    continue

                # 添加到结果字典
                result[original_key] = value

                # 标记需要移除
                keys_to_remove.add(original_key)
    else:
        for key in header_params:
            if key in data_dict:
                value = data_dict[key]

                if remove_none and value is None:
                    continue

                result[key] = value
                keys_to_remove.add(key)

    # 从原始数据中移除已提取的键（如果是字典）
    if isinstance(data, dict):
        for key in keys_to_remove:
            if key in data:
                del data[key]

    return result

def filter_header_params(header_params: Optional[Dict], params: Optional[Dict]) -> Dict:    # 检查是否任一为空
    # 检查params是否为空
    if params is None or len(params) == 0:
        # params为空，直接返回header_params
        return header_params

    # 检查header_params是否为空
    if header_params is None or len(header_params) == 0:
        # header_params为空，返回空字典
        return {}

    # 两者都不为空，执行过滤操作
    return {k: v for k, v in header_params.items() if k not in params}


def get_sorted_params(params: Optional[Dict] = None) -> List[Tuple]:
    if params is None:
        return []

    # 对字典的键值对进行排序
    return sorted(params.items(), key=lambda item: item[0])


def params_to_query_string(params: Optional[Dict] = None) -> str:
    if params is None or not params:
        return ""

    # 构建查询字符串
    query_parts = []
    for key, value in params:
        query_parts.append(f"{key}={value}")

    encoded_parts = [quote(part, safe='=&') for part in query_parts]
    str_list = "&".join(encoded_parts)

    return str_list