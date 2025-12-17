from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorEventsQueryServicesRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    service: Optional[str] = None  # 服务
    monitorType: Optional[str] = None  # 用于选择监控类型，如果为event则表示事件类型

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorEventsQueryServicesResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorEventsQueryServicesReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorEventsQueryServicesReturnObj:
    services: Optional[List[object]] = None  # 服务列表
