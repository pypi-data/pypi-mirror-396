from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorQueryCustomEventsRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    customEventID: Optional[str] = None  # 自定义事件ID
    name: Optional[str] = None  # 事件名称，支持模糊搜索
    pageNo: Optional[int] = None  # 页码，不传默认为1
    pageSize: Optional[int] = None  # 每页大小，不传默认为20

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryCustomEventsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorQueryCustomEventsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryCustomEventsReturnObj:
    customEventList: Optional[List['V4MonitorQueryCustomEventsReturnObjCustomEventList']] = None  # 自定义事件列表
    totalCount: Optional[int] = None  # 总记录数
    totalPage: Optional[int] = None  # 总页数
    currentCount: Optional[int] = None  # 当前记录数


@dataclass_json
@dataclass
class V4MonitorQueryCustomEventsReturnObjCustomEventList:
    regionID: Optional[str] = None  # 资源池ID
    customEventID: Optional[str] = None  # 自定义事件ID
    name: Optional[str] = None  # 事件名称
    description: Optional[str] = None  # 事件描述
    createTime: Optional[int] = None  # 创建时间戳，精确到毫秒
    updateTime: Optional[int] = None  # 修改时间戳，精确到毫秒
