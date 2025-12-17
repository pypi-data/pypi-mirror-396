from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionModifyInspectionItemRequest(CtyunOpenAPIRequest):
    inspectionItem: int  # 本参数表示巡检项，见巡检项查询接口返回。
    level: Optional[int] = None  # 本参数表示重要等级。取值范围：<br>1：低。<br>2：中。<br>3：高。<br>根据以上范围取值。
    inspectionRules: Optional[List['V4MonitorIntelligentInspectionModifyInspectionItemRequestInspectionRules']] = None  # 巡检规则列表

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionModifyInspectionItemRequestInspectionRules:
    item: str  # 监控项，见巡检项查询接口返回。
    period: Optional[int] = None  # 巡检周期，在不同巡检项中对应巡检天数或预计未来天数
    value: Optional[float] = None  # 阈值


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionModifyInspectionItemResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorIntelligentInspectionModifyInspectionItemReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionModifyInspectionItemReturnObj:
    success: Optional[bool] = None  # 修改成功标识
