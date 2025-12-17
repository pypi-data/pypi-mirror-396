from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorHybridBoardQueryViewMonitorDataRequest(CtyunOpenAPIRequest):
    viewID: str  # 视图ID
    startTime: int  # 查询起始Unix时间戳,  startTime和endTime成对使用，且时间间隔不超过31天
    endTime: int  # 查询结束Unix时间戳，  startTime和endTime成对使用，且时间间隔不超过31天

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardQueryViewMonitorDataResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorHybridBoardQueryViewMonitorDataReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardQueryViewMonitorDataReturnObj:
    viewID: Optional[str] = None  # 视图ID
    viewType: Optional[str] = None  # 视图类型。取值范围:<br>timeSeries：折线图。<br>barChart：柱状图。<br>根据以上范围取值。
    viewData: Optional['V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewData'] = None  # 数据
    unit: Optional[str] = None  # 单位


@dataclass_json
@dataclass
class V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewData:
    expr: Optional[str] = None  # promQL查询表达式
    legendFormat: Optional[str] = None  # 图例
    period: Optional[int] = None  # 周期
    metricList: Optional[List['V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewDataMetricList']] = None  # 指标列表


@dataclass_json
@dataclass
class V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewDataMetricList:
    metricName: Optional[str] = None  # 指标名称
    lengend: Optional[str] = None  # 图例值
    metricData: Optional[List['V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewDataMetricListMetricData']] = None  # 指标数据
    dimensions: Optional[List['V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewDataMetricListDimensions']] = None  # 指标标签


@dataclass_json
@dataclass
class V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewDataMetricListMetricData:
    value: Optional[float] = None  # 监控项值，具体请参考对应监控项文档
    timestamp: Optional[int] = None  # 监控数据Unix时间戳


@dataclass_json
@dataclass
class V4MonitorHybridBoardQueryViewMonitorDataReturnObjViewDataMetricListDimensions:
    name: Optional[str] = None  # 监控项标签键
    value: Optional[str] = None  # 监控项标签键对应的值
