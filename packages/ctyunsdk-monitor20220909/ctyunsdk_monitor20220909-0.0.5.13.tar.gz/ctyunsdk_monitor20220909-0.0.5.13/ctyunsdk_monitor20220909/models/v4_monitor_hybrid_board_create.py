from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequest(CtyunOpenAPIRequest):
    name: str  # 监控大盘名称
    viewsQueryParams: Optional['V4MonitorHybridBoardCreateRequestViewsQueryParams'] = None  # 视图查询参数
    defaultDatasource: Optional['V4MonitorHybridBoardCreateRequestDefaultDatasource'] = None  # 默认数据源，如果views中datasource下的namespace配置了$namespace，则会自动替换为本配置值
    views: Optional[List['V4MonitorHybridBoardCreateRequestViews']] = None  # 视图内容

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequestViewsQueryParams:
    job: Optional[List[str]] = None  # 任务，默认查询所有


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequestDefaultDatasource:
    type: str  # 数据类型。取值范围:<br>prometheus<br>根据以上范围取值。
    namespace: str  # 指标仓库名称，支持使用$namespace来自动替换为defaultDatasource的仓库名称


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequestViews:
    name: str  # 监控大盘视图名称
    type: str  # 视图类型。取值范围:<br>timeSeries：折线图。<br>barChart：柱状图。<br>table：表格。<br>根据以上范围取值。
    datasource: 'V4MonitorHybridBoardCreateRequestViewsDatasource'  # 数据源
    fieldConfig: 'V4MonitorHybridBoardCreateRequestViewsFieldConfig'  # 字段配置
    targets: List['V4MonitorHybridBoardCreateRequestViewsTargets']
    description: Optional[str] = None  # 视图描述


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequestViewsDatasource:
    type: str  # 数据类型。取值范围:<br>prometheus<br>根据以上范围取值。
    namespace: str  # 指标仓库名称，支持使用$namespace来自动替换为defaultDatasource的仓库名称


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequestViewsFieldConfig:
    defaults: 'V4MonitorHybridBoardCreateRequestViewsFieldConfigDefaults'  # 默认配置


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequestViewsFieldConfigDefaults:
    unit: str  # 单位


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateRequestViewsTargets:
    expr: str  # prometheus表达式
    legendFormat: Optional[str] = None  # 图例格式化
    period: Optional[int] = None  # 周期


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorHybridBoardCreateReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateReturnObj:
    boardID: Optional[str] = None  # 监控大盘ID
    viewIDs: Optional[List[str]] = None  # 视图ID
