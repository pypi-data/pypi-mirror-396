from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorDescribeProbePointRequest(CtyunOpenAPIRequest):
    taskID: str  # 站点任务ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorDescribeProbePointResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorDescribeProbePointReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorDescribeProbePointReturnObj:
    result: Optional[List['V4MonitorDescribeProbePointReturnObjResult']] = None  # 统计结果列表


@dataclass_json
@dataclass
class V4MonitorDescribeProbePointReturnObjResult:
    pointID: Optional[str] = None  # 探测节点ID
    data: Optional[List['V4MonitorDescribeProbePointReturnObjResultData']] = None  # 探测点异常统计信息


@dataclass_json
@dataclass
class V4MonitorDescribeProbePointReturnObjResultData:
    value: Optional[int] = None  # 事件统计数量
    samplingTime: Optional[int] = None  # 事件统计采样时间,秒级
