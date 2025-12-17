from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryListRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    startTime: int  # 查询起始时间戳，不超过31天
    endTime: int  # 查询截止时间戳
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 页大小，默认为10，不超过100

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorIntelligentInspectionQueryHistoryListReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryListReturnObj:
    inspectionHistoryList: Optional[List['V4MonitorIntelligentInspectionQueryHistoryListReturnObjInspectionHistoryList']] = None  # 巡检历史列表
    totalCount: Optional[int] = None  # 获取对象数据条数
    totalPage: Optional[int] = None  # 总页数
    currentCount: Optional[int] = None  # 当前页记录数


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryListReturnObjInspectionHistoryList:
    taskID: Optional[str] = None  # 巡检任务ID
    inspectionTime: Optional[int] = None  # 巡检时间，秒级。
    inspectionScore: Optional[int] = None  # 巡检任务的巡检得分。
    inspectionItemList: Optional[List['V4MonitorIntelligentInspectionQueryHistoryListReturnObjInspectionHistoryListInspectionItemList']] = None  # 巡检项列表


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryHistoryListReturnObjInspectionHistoryListInspectionItemList:
    productType: Optional[str] = None  # 本参数表示产品类型。
    inspectionType: Optional[int] = None  # 本参数表示巡检类型。
    inspectionItem: Optional[int] = None  # 本参数表示巡检项。
    inspectionName: Optional[str] = None  # 本参数表示巡检项名称
    level: Optional[int] = None  # 本参数表示重要等级。取值范围：<br>1：低。<br>2：中。<br>3：高。<br>根据以上范围取值。
    description: Optional[str] = None  # 巡检项描述
    status: Optional[bool] = None  # 本参数表示巡检结果。取值范围：<br>true：正常。<br>false：异常。<br>根据以上范围取值。
    anomalyCount: Optional[int] = None  # 巡检项的异常数量
    solveTime: Optional[int] = None  # 治理时间，秒级。
