from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorMonitorBoardListRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    boardType: Optional[str] = None  # 看板类型。默认all。取值范围：<br>all：查询所有。<br>system：系统默认看板。<br>custom：自定义看板。<br>根据以上范围取值。
    name: Optional[str] = None  # 名称模糊搜索
    service: Optional[str] = None  # 视图中包含指定云监控服务的看板，仅当boardType为system时有效。取值范围参见[监控看板：查询系统看板支持服务维度](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15782&data=90&isNormal=1&vid=84)
    dimension: Optional[str] = None  # 视图中包含指定云监控维度的看板，仅当boardType为system时有效。取值范围参见[监控看板：查询系统看板支持服务维度](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15782&data=90&isNormal=1&vid=84)
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 页大小，默认为10

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorMonitorBoardListReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardListReturnObj:
    boardList: Optional[List['V4MonitorMonitorBoardListReturnObjBoardList']] = None  # 监控看板列表
    currentCount: Optional[int] = None  # 当前页记录数
    totalCount: Optional[int] = None  # 总记录数
    totalPage: Optional[int] = None  # 总页数
    boardQuota: Optional[int] = None  # 监控看板配额剩余数量


@dataclass_json
@dataclass
class V4MonitorMonitorBoardListReturnObjBoardList:
    boardID: Optional[str] = None  # 监控看板ID
    type: Optional[str] = None  # 看板类型。取值范围：<br>system：系统默认看板。<br>custom：自定义看板。<br>根据以上范围取值。
    name: Optional[str] = None  # 监控看板名称
    createTime: Optional[int] = None  # 创建时间，时间戳，精确到秒
    updateTime: Optional[int] = None  # 最近更新时间, 时间戳，精确到秒
