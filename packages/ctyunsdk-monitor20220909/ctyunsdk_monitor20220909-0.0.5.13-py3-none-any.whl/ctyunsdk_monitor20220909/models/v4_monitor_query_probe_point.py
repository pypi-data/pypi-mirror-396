from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorQueryProbePointRequest(CtyunOpenAPIRequest):
    def __post_init__(self):
        super().__init__()



@dataclass_json
@dataclass
class V4MonitorQueryProbePointResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorQueryProbePointReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryProbePointReturnObj:
    pointList: Optional[List['V4MonitorQueryProbePointReturnObjPointList']] = None  # 探测节点列表
    totalCount: Optional[int] = None  # 总记录数


@dataclass_json
@dataclass
class V4MonitorQueryProbePointReturnObjPointList:
    pointID: Optional[str] = None  # 探测节点唯一ID
    pointName: Optional[str] = None  # 探测节点名称
    position: Optional[str] = None  # 探测节点区域
    status: Optional[bool] = None  # 探测节点心跳状态
    longitude: Optional[str] = None  # 探测节点经度
    latitude: Optional[str] = None  # 探测节点纬度
