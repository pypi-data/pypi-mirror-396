from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequest(CtyunOpenAPIRequest):
    boardID: str  # 监控大盘ID
    views: List['V4MonitorHybridBoardCreateViewRequestViews']  # 监控视图
    viewsQueryParams: Optional['V4MonitorHybridBoardCreateViewRequestViewsQueryParams'] = None  # 视图查询参数
    defaultDatasource: Optional['V4MonitorHybridBoardCreateViewRequestDefaultDatasource'] = None  # 默认数据源，如果views中datasource下的namespace配置了$namespace，则会自动替换为本配置值

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequestViewsQueryParams:
    job: Optional[List[str]] = None  # 任务，默认查询所有


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequestDefaultDatasource:
    type: str  # 数据类型。取值范围:<br>prometheus<br>根据以上范围取值。
    namespace: str  # 指标仓库名称，支持使用$namespace来自动替换为defaultDatasource的仓库名称


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequestViews:
    name: str  # 监控大盘视图名称
    type: str  # 视图类型。取值范围:<br>timeSeries：折线图。<br>barChart：柱状图。<br>table：表格。<br>根据以上范围取值。
    datasource: 'V4MonitorHybridBoardCreateViewRequestViewsDatasource'  # 数据源
    fieldConfig: 'V4MonitorHybridBoardCreateViewRequestViewsFieldConfig'  # 字段配置
    targets: List['V4MonitorHybridBoardCreateViewRequestViewsTargets']
    description: Optional[str] = None  # 视图描述


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequestViewsDatasource:
    type: str  # 数据类型。取值范围:<br>prometheus<br>根据以上范围取值。
    namespace: str  # 指标仓库名称，支持使用$namespace来自动替换为defaultDatasource的仓库名称


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequestViewsFieldConfig:
    defaults: 'V4MonitorHybridBoardCreateViewRequestViewsFieldConfigDefaults'  # 默认配置


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequestViewsFieldConfigDefaults:
    unit: str  # 单位


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewRequestViewsTargets:
    expr: str  # prometheus表达式
    legendFormat: Optional[str] = None  # 图例格式化
    period: Optional[int] = None  # 周期


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorHybridBoardCreateViewReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardCreateViewReturnObj:
    viewIDs: Optional[List[str]] = None  # 视图ID
