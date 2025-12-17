from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    service: str  # 服务，见事件监控：查询服务维度接口返回。
    dimension: str  # 维度，见事件监控：查询服务维度接口返回。
    tableName: str  # 页签名称
    fun: str  # 本参数表示数据聚合采用算法。取值范围：<br>raw：原始值算法。<br>avg：平均值算法。<br>max：最大值算法。<br>min：最小值算法。<br>variance：方差算法。<br>sum：求和算法。<br>根据以上范围取值。
    startTime: int  # 查询起始时间戳
    endTime: int  # 查询结束时间戳
    dimensions: List['V4MonitorCanvasQueryHistoryDataRequestDimensions']  # 查询设备标签列表，用于定位目标设备，多标签查询取交集。
    period: Optional[int] = None  # 聚合周期，单位：秒，默认300，不小于60

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataRequestDimensions:
    name: str  # 设备标签键
    value: List[str]  # 设备标签键所对应的值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorCanvasQueryHistoryDataReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataReturnObj:
    tables: Optional[List['V4MonitorCanvasQueryHistoryDataReturnObjTables']] = None  # 页签


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataReturnObjTables:
    tableName: Optional[str] = None  # 页签名称
    charts: Optional[List['V4MonitorCanvasQueryHistoryDataReturnObjTablesCharts']] = None  # 图表


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataReturnObjTablesCharts:
    chartName: Optional[str] = None  # 图表名称
    chartDesc: Optional[str] = None  # 图表描述
    unit: Optional[str] = None  # 数据单位
    unitRelations: Optional[List['V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsUnitRelations']] = None  # 单位转换字典
    dataPoints: Optional[List['V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsDataPoints']] = None  # 图表数据点
    graphType: Optional[int] = None  # 本参数表示图表类型。取值范围：<br>0：小图。<br>1：小图+大图。<br>根据以上范围取值。
    chartType: Optional[int] = None  # 本参数表示图表样式。取值范围：<br>0：折线图。<br>根据以上范围取值。
    recommendUnit: Optional[str] = None  # 期望单位
    unitChange: Optional[int] = None  # 本参数表示是否支持单位切换。取值范围：<br>0：不支持。<br>1：支持。<br>根据以上范围取值。


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsUnitRelations:
    unit: Optional[str] = None  # 单位
    weight: Optional[float] = None  # 权重


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsDataPoints:
    linePoints: Optional[List['V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsDataPointsLinePoints']] = None  # 图线
    labels: Optional[List['V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsDataPointsLabels']] = None  # 图例


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsDataPointsLinePoints:
    value: Optional[float] = None  # 数据值
    timestamp: Optional[int] = None  # 数据采样时间


@dataclass_json
@dataclass
class V4MonitorCanvasQueryHistoryDataReturnObjTablesChartsDataPointsLabels:
    name: Optional[str] = None  # 数据标签键
    value: Optional[str] = None  # 数据标签键对应的值
