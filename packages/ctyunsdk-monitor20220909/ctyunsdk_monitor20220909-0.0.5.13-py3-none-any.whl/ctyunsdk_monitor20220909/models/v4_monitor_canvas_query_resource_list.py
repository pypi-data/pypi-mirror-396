from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListRequest(CtyunOpenAPIRequest):
    dimension: str  # 维度
    regionID: str  # 资源池ID
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 页大小，默认为10
    enumFilter: Optional[List['V4MonitorCanvasQueryResourceListRequestEnumFilter']] = None  # 筛选列表
    searchFilter: Optional[List['V4MonitorCanvasQueryResourceListRequestSearchFilter']] = None  # 模糊匹配列表

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListRequestEnumFilter:
    key: str  # 筛选关键字
    value: str  # 筛选值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListRequestSearchFilter:
    key: str  # 模糊匹配关键字
    value: str  # 模糊匹配值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorCanvasQueryResourceListReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObj:
    totalPage: Optional[int] = None  # 总页数
    currentCount: Optional[int] = None  # 当前页记录数
    totalCount: Optional[int] = None  # 资源总记录数
    pageSizeUpper: Optional[int] = None  # 分页上限
    pageSupport: Optional[bool] = None  # 是否支持分页
    items: Optional[List['V4MonitorCanvasQueryResourceListReturnObjItems']] = None  # 资源列表
    enumFilter: Optional[List['V4MonitorCanvasQueryResourceListReturnObjEnumFilter']] = None  # 筛选列表
    searchFilter: Optional[List['V4MonitorCanvasQueryResourceListReturnObjSearchFilter']] = None  # 模糊匹配列表
    tableHeaders: Optional[List['V4MonitorCanvasQueryResourceListReturnObjTableHeaders']] = None  # 表头


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjItems:
    monitorDimensions: Optional[List['V4MonitorCanvasQueryResourceListReturnObjItemsMonitorDimensions']] = None  # 维度信息
    display: Optional[List['V4MonitorCanvasQueryResourceListReturnObjItemsDisplay']] = None  # 展示属性
    baseInfo: Optional['V4MonitorCanvasQueryResourceListReturnObjItemsBaseInfo'] = None  # 基础信息
    childInfo: Optional[List['V4MonitorCanvasQueryResourceListReturnObjItemsChildInfo']] = None  # 子设备查询信息


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjItemsMonitorDimensions:
    key: Optional[str] = None  # 维度字段
    data: Optional[List['V4MonitorCanvasQueryResourceListReturnObjItemsMonitorDimensionsData']] = None  # 维度信息


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjItemsMonitorDimensionsData:
    value: Optional[str] = None  # 维度值
    desc: Optional[str] = None  # 维度描述


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjItemsDisplay:
    key: Optional[str] = None  # 展示字段
    value: Optional[str] = None  # 展示字段的值
    description: Optional[str] = None  # 展示字段描述


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjItemsBaseInfo:
    instanceID: Optional[str] = None  # 实例ID
    instanceName: Optional[str] = None  # 实例名称


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjItemsChildInfo:
    childKey: Optional[str] = None  # 子设备查询标签
    childDimension: Optional[str] = None  # 子设备对应的维度
    childRequestInfo: Optional[List['V4MonitorCanvasQueryResourceListReturnObjItemsChildInfoChildRequestInfo']] = None  # 子设备查询信息


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjItemsChildInfoChildRequestInfo:
    key: Optional[str] = None  # 子设备查询键
    value: Optional[str] = None  # 子设备查询键对应的值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjEnumFilter:
    key: Optional[str] = None  # 筛选关键字
    desc: Optional[str] = None  # 筛选对应的名称
    enumValues: Optional[List['V4MonitorCanvasQueryResourceListReturnObjEnumFilterEnumValues']] = None  # 筛选枚举值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjEnumFilterEnumValues:
    key: Optional[str] = None  # 枚举关键字
    value: Optional[str] = None  # 枚举值


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjSearchFilter:
    key: Optional[str] = None  # 模糊查询关键字
    desc: Optional[str] = None  # 模糊查询对应的名称


@dataclass_json
@dataclass
class V4MonitorCanvasQueryResourceListReturnObjTableHeaders:
    key: Optional[str] = None  # 表头关键字
    description: Optional[str] = None  # 表头名称
