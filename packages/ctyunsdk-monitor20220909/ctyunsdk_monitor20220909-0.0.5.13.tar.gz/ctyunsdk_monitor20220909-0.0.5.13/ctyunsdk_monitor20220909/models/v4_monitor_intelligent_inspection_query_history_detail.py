from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryDetailRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    taskID: str  # 巡检任务ID
    inspectionItem: int  # 本参数表示巡检项，见巡检项查询接口返回。
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 页大小，默认为10，不超过100
    isSolve: Optional[bool] = None  # 本参数表示是否处理记录的异常，默认false。取值范围：<br>true：是。<br>false：不是。<br>根据以上范围取值。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryDetailResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorIntelligentInspectionQueryHistoryDetailReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryDetailReturnObj:
    anomalyDetail: Optional[List['V4MonitorIntelligentInspectionQueryHistoryDetailReturnObjAnomalyDetail']] = None  # 异常详情列表
    totalCount: Optional[int] = None  # 获取对象数据条数
    totalPage: Optional[int] = None  # 总页数
    currentCount: Optional[int] = None  # 当前页记录数


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryDetailReturnObjAnomalyDetail:
    anomalyID: Optional[str] = None  # 异常ID
    anomalyName: Optional[str] = None  # 异常名称
    anomalyItem: Optional[str] = None  # 异常项
    anomalyValue: Optional[str] = None  # 异常值
