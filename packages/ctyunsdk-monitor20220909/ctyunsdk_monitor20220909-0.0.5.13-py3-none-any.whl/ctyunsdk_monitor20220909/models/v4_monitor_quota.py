from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorQuotaRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    quotaKeys: Optional[List[str]] = None  # 用户配额标签，不传默认查询云监控所有配额标签

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQuotaResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[List['V4MonitorQuotaReturnObj']] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQuotaReturnObj:
    quotaList: Optional[List['V4MonitorQuotaReturnObjQuotaList']] = None  # 用户配额清单


@dataclass_json
@dataclass
class V4MonitorQuotaReturnObjQuotaList:
    quotaKey: Optional[str] = None  # 配额标签
    quotaName: Optional[str] = None  # 配额名
    quota: Optional[int] = None  # 用户配额值
    usedQuota: Optional[int] = None  # 用户已使用配额
