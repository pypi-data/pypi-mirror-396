from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskAnomalyRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    inspectionType: int  # 本参数表示巡检类型，见巡检项查询接口返回。
    taskID: str  # 巡检任务ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskAnomalyResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorIntelligentInspectionQueryTaskAnomalyReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskAnomalyReturnObj:
    inspectionAnomalyList: Optional[List['V4MonitorIntelligentInspectionQueryTaskAnomalyReturnObjInspectionAnomalyList']] = None  # 巡检异常列表


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskAnomalyReturnObjInspectionAnomalyList:
    inspectionItem: Optional[int] = None  # 本参数表示巡检项。
    inspectionName: Optional[str] = None  # 本参数表示巡检项名称
    anomalyCount: Optional[int] = None  # 巡检项的异常数量
    solveTime: Optional[int] = None  # 治理时间，秒级。
