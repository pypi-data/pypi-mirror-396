from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateSysResourcesRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    boardID: str  # 系统监控看板ID
    resources: List['V4MonitorMonitorBoardUpdateSysResourcesRequestResources']  # 监控资源实例， 监控资源实例最多支持20个

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateSysResourcesRequestResources:
    resource: List['V4MonitorMonitorBoardUpdateSysResourcesRequestResourcesResource']  # 资源


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateSysResourcesRequestResourcesResource:
    key: str  # 资源实例标签键
    value: str  # 资源实例标签值


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateSysResourcesResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorMonitorBoardUpdateSysResourcesReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateSysResourcesReturnObj:
    success: Optional[bool] = None  # 是否更新成功
