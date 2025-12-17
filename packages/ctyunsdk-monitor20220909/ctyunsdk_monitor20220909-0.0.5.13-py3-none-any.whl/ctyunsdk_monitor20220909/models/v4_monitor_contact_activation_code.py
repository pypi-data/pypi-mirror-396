from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorContactActivationCodeRequest(CtyunOpenAPIRequest):
    contactID: str  # 告警联系人ID
    media: str  # 本参数表示媒介。取值范围：<br>sms：手机短信。<br>email：邮箱。<br>根据以上范围取值。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorContactActivationCodeResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorContactActivationCodeReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorContactActivationCodeReturnObj:
    success: Optional[bool] = None  # 是否成功
