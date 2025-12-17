from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    service: str  # 服务
    dimension: str  # 维度
    viewID: str  # 视图ID
    resources: List['V4MonitorCanvasQueryViewDataRequestResources']  # 监控资源实例
    fun: Optional[str] = None  # 本参数表示数据聚合采用算法。取值范围：<br>raw：原始值算法。<br>avg：平均值算法。<br>max：最大值算法。<br>min：最小值算法。<br>variance：方差算法。<br>sum：求和算法。<br>根据以上范围取值。
    startTime: Optional[int] = None  # 查询起始时间戳
    endTime: Optional[int] = None  # 查询结束时间戳
    timestamp: Optional[int] = None  # TOP图查询时间戳
    period: Optional[int] = None  # 聚合周期，单位：秒，默认300，不小于60

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataRequestResources:
    resource: List['V4MonitorCanvasQueryViewDataRequestResourcesResource']  # 资源


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataRequestResourcesResource:
    key: str  # 资源实例标签键
    value: str  # 资源实例标签值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorCanvasQueryViewDataReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObj:
    viewID: Optional[str] = None  # 视图ID
    viewType: Optional[int] = None  # 视图类型。取值范围:<br>0：小图。<br>1：大图。<br>2：TOP图。<br>根据以上范围取值。
    viewData: Optional['V4MonitorCanvasQueryViewDataReturnObjViewData'] = None  # 数据


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObjViewData:
    timeSeriesData: Optional[List['V4MonitorCanvasQueryViewDataReturnObjViewDataTimeSeriesData']] = None  # 小图或者大图数据
    topData: Optional[List['V4MonitorCanvasQueryViewDataReturnObjViewDataTopData']] = None  # TOP数据


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObjViewDataTimeSeriesData:
    itemName: Optional[str] = None  # 监控项名称
    itemDesc: Optional[str] = None  # 监控项中文介绍
    itemUnit: Optional[str] = None  # 监控项单位
    itemData: Optional[List['V4MonitorCanvasQueryViewDataReturnObjViewDataTimeSeriesDataItemData']] = None  # 折线图数据
    dimensions: Optional[List['V4MonitorCanvasQueryViewDataReturnObjViewDataTimeSeriesDataDimensions']] = None  # 监控项标签


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObjViewDataTimeSeriesDataItemData:
    value: Optional[float] = None  # 监控项值，具体请参考对应监控项文档
    timestamp: Optional[int] = None  # 监控数据Unix时间戳


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObjViewDataTimeSeriesDataDimensions:
    name: Optional[str] = None  # 监控项标签键
    value: Optional[str] = None  # 监控项标签键对应的值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObjViewDataTopData:
    itemName: Optional[str] = None  # 监控项名称，具体设备对应监控项参见[监控项列表：查询](https://www.ctyun.cn/document/10032263/10039882)
    itemDesc: Optional[str] = None  # 监控项中文介绍
    itemUnit: Optional[str] = None  # 监控项单位
    itemData: Optional[List['V4MonitorCanvasQueryViewDataReturnObjViewDataTopDataItemData']] = None  # 监控项内容


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObjViewDataTopDataItemData:
    value: Optional[float] = None  # 监控项值，具体请参考对应监控项文档
    dimensions: Optional[List['V4MonitorCanvasQueryViewDataReturnObjViewDataTopDataItemDataDimensions']] = None  # 监控项标签


@dataclass_json
@dataclass
class V4MonitorCanvasQueryViewDataReturnObjViewDataTopDataItemDataDimensions:
    name: Optional[str] = None  # 监控项标签键
    value: Optional[str] = None  # 监控项标签键对应的值
