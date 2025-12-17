from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorEventsQueryDetailRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池 ID
    startTime: int  # 查询起始时间戳
    endTime: int  # 查询截止时间戳
    eventName: str  # 本参数表示事件指标，事件指标见查询事件接口返回。
    service: str  # 服务，见事件监控：查询服务维度接口返回。
    dimension: str  # 维度，见事件监控：查询服务维度接口返回。
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 页大小，默认为20
    resGroupID: Optional[str] = None  # 资源分组ID，在资源分组事件时传入

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorEventsQueryDetailResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorEventsQueryDetailReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorEventsQueryDetailReturnObj:
    totalCount: Optional[int] = None  # 获取对象数据条数
    totalPage: Optional[int] = None  # 总页数
    currentCount: Optional[int] = None  # 当前页记录数
    eventDetail: Optional[List[object]] = None  # 事件详情列表
