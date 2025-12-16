from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CtyunOpenAPIResponse:
    """天翼云OpenAPI响应基类"""
    traceId: Optional[str] = None

    def __init__(self, traceId: Optional[str] = None):
        self.traceId = traceId
