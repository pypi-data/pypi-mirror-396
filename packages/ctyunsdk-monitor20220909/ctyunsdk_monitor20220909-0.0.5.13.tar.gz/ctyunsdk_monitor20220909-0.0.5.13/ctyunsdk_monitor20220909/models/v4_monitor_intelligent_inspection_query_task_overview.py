from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskOverviewRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskOverviewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorIntelligentInspectionQueryTaskOverviewReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskOverviewReturnObj:
    taskID: Optional[str] = None  # 巡检任务ID
    inspectionTime: Optional[int] = None  # 巡检时间，秒级。
    totalScore: Optional[int] = None  # 巡检任务的巡检得分。
    inspectionTypeResults: Optional[List['V4MonitorIntelligentInspectionQueryTaskOverviewReturnObjInspectionTypeResults']] = None  # 巡检类型结果


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryTaskOverviewReturnObjInspectionTypeResults:
    status: Optional[int] = None  # 本参数表示任务状态码，取值范围：<br>1：运行中。<br>2：已完成。<br>&#32;3：失败。<br>根据以上范围取值。
    inspectionType: Optional[int] = None  # 本参数表示巡检类型。
    inspectionScore: Optional[int] = None  # 巡检类型的巡检得分。
    inspectionItemCount: Optional[int] = None  # 巡检项数量
    anomalyCount: Optional[int] = None  # 异常数量
    errorMessage: Optional[str] = None  # 错误信息
