from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorUnitQueryUnitsRequest(CtyunOpenAPIRequest):
    def __post_init__(self):
        super().__init__()



@dataclass_json
@dataclass
class V4MonitorUnitQueryUnitsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorUnitQueryUnitsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorUnitQueryUnitsReturnObj:
    data: Optional[List['V4MonitorUnitQueryUnitsReturnObjData']] = None  # 统计信息列表


@dataclass_json
@dataclass
class V4MonitorUnitQueryUnitsReturnObjData:
    unitGroupID: Optional[int] = None  # 单位组id
    unitGroup: Optional[str] = None  # 单位组的Key
    name: Optional[str] = None  # 单位组名称,<br>根据header参数中的Accept-Language的值返回中文名或者英文名,<br>zh-CN: 返回中文名 <br>en: 返回英文名<br>默认返回中文名
    comment: Optional[str] = None  # 单位组介绍
    units: Optional[List['V4MonitorUnitQueryUnitsReturnObjDataUnits']] = None  # 单位列表


@dataclass_json
@dataclass
class V4MonitorUnitQueryUnitsReturnObjDataUnits:
    unitID: Optional[int] = None  # 单位id
    unit: Optional[str] = None  # 单位的Key
    name: Optional[str] = None  # 单位名称,<br>根据header参数中的Accept-Language的值返回中文名或者英文名,<br>zh-CN: 返回中文名 <br>en: 返回英文名<br>默认返回中文名
    comment: Optional[str] = None  # 单位介绍
    unitTransfer: Optional[float] = None  # 单位换算
