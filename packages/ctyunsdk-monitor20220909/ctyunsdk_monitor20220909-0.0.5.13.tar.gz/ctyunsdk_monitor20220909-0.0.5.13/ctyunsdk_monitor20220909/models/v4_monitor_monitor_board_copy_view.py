from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorMonitorBoardCopyViewRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    viewID: str  # 要复制的监控视图ID
    destBoardID: str  # 目标监控看板ID
    viewName: Optional[str] = None  # 监控视图副本名称，默认为原监控视图名称加"_copy"

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardCopyViewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorMonitorBoardCopyViewReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardCopyViewReturnObj:
    viewID: Optional[str] = None  # 复制的新viewID
