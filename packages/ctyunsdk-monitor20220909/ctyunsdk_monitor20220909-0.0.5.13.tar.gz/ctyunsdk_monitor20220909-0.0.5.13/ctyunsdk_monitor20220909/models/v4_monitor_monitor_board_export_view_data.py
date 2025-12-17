from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorMonitorBoardExportViewDataRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    viewID: str  # 视图ID
    startTime: Optional[int] = None  # 查询起始Unix时间戳,  startTime和endTime成对使用，且时间间隔不超过90天
    endTime: Optional[int] = None  # 查询结束Unix时间戳，  startTime和endTime成对使用，且时间间隔不超过90天
    fun: Optional[str] = None  # 本参数表示聚合类型。默认值为avg。取值范围:<br>raw：原始值。<br>avg：平均值。<br>min：最小值。<br>max：最大值。<br>variance：方差。<br>sum：求和。<br>根据以上范围取值。
    period: Optional[int] = None  # 聚合周期，单位：秒，默认300，需不小于60，推荐使用60的整倍数。当fun为raw时本参数无效。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardExportViewDataResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


