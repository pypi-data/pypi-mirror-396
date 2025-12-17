from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    service: Optional[str] = None  # 服务
    dimension: Optional[str] = None  # 维度
    resource: Optional[List['V4MonitorCanvasQueryRegionDeployRequestResource']] = None  # 资源
    enumFilter: Optional[str] = None  # 筛选信息

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployRequestResource:
    key: str  # 资源实例标签键
    value: str  # 资源实例标签值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorCanvasQueryRegionDeployReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployReturnObj:
    regionCanvasList: Optional[List['V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasList']] = None  # 画布信息


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasList:
    status: Optional[int] = None  # 本参数表示画布状态。取值范围：<br>0：上线画布。<br>1：缺省画布。<br>根据以上范围取值。
    categroyID: Optional[int] = None  # 大类ID
    categoryName: Optional[str] = None  # 大类名称
    subCategoryID: Optional[int] = None  # 小类ID
    subCategoryName: Optional[str] = None  # 小类名称
    canvasID: Optional[str] = None  # 画布ID
    canvasName: Optional[str] = None  # 画布名称
    canvasObj: Optional[List['V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasListCanvasObj']] = None  # 页签信息


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasListCanvasObj:
    tableTitle: Optional[str] = None  # 页签名称
    isMulti: Optional[int] = None  # 本参数表示是否有下拉框。取值范围：<br>0：没有。<br>1：有。<br>根据以上范围取值。
    filterType: Optional[int] = None  # 本参数表示下拉框类型。取值范围：<br>0：子设备下拉框。<br>1：视图筛选下拉框。<br>根据以上范围取值。
    dimensions: Optional[List[str]] = None  # 页签对应的查询标签
    viewList: Optional[List['V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasListCanvasObjViewList']] = None  # 视图列表


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasListCanvasObjViewList:
    viewID: Optional[str] = None  # 视图ID
    viewName: Optional[str] = None  # 视图名称
    viewDesc: Optional[str] = None  # 视图描述
    metricList: Optional[int] = None  # 监控项ID列表
    graphType: Optional[int] = None  # 本参数表示视图类型。取值范围：<br>0：小图。<br>1：大图。<br>2：TOP图。<br>根据以上范围取值。
    chartType: Optional[int] = None  # 本参数表示图表类型。取值范围：<br>0：折线图。<br>根据以上范围取值。
    recommendUnit: Optional[str] = None  # 推荐单位
    unitChange: Optional[int] = None  # 本参数表示是否支持单位切换。取值范围：<br>0：不支持。<br>1：支持。<br>根据以上范围取值。
    topType: Optional[int] = None  # 本参数表示TOP的数量。取值范围：<br>0：top5。<br>1：top10。<br>2：top15。<br>3：top20。<br>根据以上范围取值。
    orderType: Optional[int] = None  # 本参数表示排序顺序。取值范围：<br>0：升序。<br>1：降序。<br>根据以上范围取值。
    displayLabel: Optional[List['V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasListCanvasObjViewListDisplayLabel']] = None  # TOP图映射标签


@dataclass_json
@dataclass
class V4MonitorCanvasQueryRegionDeployReturnObjRegionCanvasListCanvasObjViewListDisplayLabel:
    key: Optional[str] = None  # TOP图映射键
    value: Optional[str] = None  # TOP图映射键对应的值
