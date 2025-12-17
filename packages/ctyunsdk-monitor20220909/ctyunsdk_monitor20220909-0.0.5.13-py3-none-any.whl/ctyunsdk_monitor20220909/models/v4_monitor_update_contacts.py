from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorUpdateContactsRequest(CtyunOpenAPIRequest):
    contactID: str  # 告警联系人ID
    name: str  # 用户名
    phone: Optional[str] = None  # 手机号，手机号和邮箱二选一必填，手机号填了，邮箱可不填，反之一样，二者不能全为空。
    email: Optional[str] = None  # 邮箱， 手机号和邮箱二选一必填，邮箱填了，手机号可不填，反之一样，二者不能全为空。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorUpdateContactsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorUpdateContactsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorUpdateContactsReturnObj:
    contactID: Optional[str] = None  # 告警联系人ID
