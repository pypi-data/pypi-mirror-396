from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorPublicNetworkProbingQueryTableDataRequest(CtyunOpenAPIRequest):
    itemName: str  # 监控项名称
    sourceRegion: str  # 源资源池ID
    sourceProvider: str  # 源运营商
    startTime: int  # 查询起始Unix时间戳，秒级
    endTime: int  # 查询结束Unix时间戳，秒级
    targetProvince: Optional[str] = None  # 目的省

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorPublicNetworkProbingQueryTableDataResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorPublicNetworkProbingQueryTableDataReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorPublicNetworkProbingQueryTableDataReturnObj:
    data: Optional[List['V4MonitorPublicNetworkProbingQueryTableDataReturnObjData']] = None  # 表格数据列表


@dataclass_json
@dataclass
class V4MonitorPublicNetworkProbingQueryTableDataReturnObjData:
    value: Optional[float] = None  # 监控项值
    targetProvince: Optional[str] = None  # 目的省
    targetCity: Optional[str] = None  # 目的市
    targetProvider: Optional[str] = None  # 目的省
