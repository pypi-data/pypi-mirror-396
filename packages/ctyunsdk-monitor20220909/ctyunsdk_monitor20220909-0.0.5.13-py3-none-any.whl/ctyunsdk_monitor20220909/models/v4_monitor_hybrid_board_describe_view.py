from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorHybridBoardDescribeViewRequest(CtyunOpenAPIRequest):
    viewID: str  # 监控视图ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardDescribeViewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorHybridBoardDescribeViewReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardDescribeViewReturnObj:
    viewID: Optional[str] = None  # 监控视图ID
    boardID: Optional[str] = None  # 所属监控大盘ID
    name: Optional[str] = None  # 监控视图名称
    type: Optional[str] = None  # 视图类型。取值范围:<br>timeSeries：折线图。<br>barChart：柱状图。<br>根据以上范围取值。
    description: Optional[str] = None  # 视图描述
    createTime: Optional[int] = None  # 创建时间，时间戳，精确到秒
    updateTime: Optional[int] = None  # 最近更新时间, 时间戳，精确到秒
    datasource: Optional['V4MonitorHybridBoardDescribeViewReturnObjDatasource'] = None  # 数据源
    fieldConfig: Optional['V4MonitorHybridBoardDescribeViewReturnObjFieldConfig'] = None  # 字段配置
    targets: Optional[List['V4MonitorHybridBoardDescribeViewReturnObjTargets']] = None
    job: Optional[List[str]] = None  # 任务


@dataclass_json
@dataclass
class V4MonitorHybridBoardDescribeViewReturnObjDatasource:
    type: Optional[str] = None  # 数据类型。取值范围:<br>prometheus<br>根据以上范围取值。
    namespace: Optional[str] = None  # 指标仓库名称


@dataclass_json
@dataclass
class V4MonitorHybridBoardDescribeViewReturnObjFieldConfig:
    defaults: Optional['V4MonitorHybridBoardDescribeViewReturnObjFieldConfigDefaults'] = None  # 默认配置


@dataclass_json
@dataclass
class V4MonitorHybridBoardDescribeViewReturnObjFieldConfigDefaults:
    unit: Optional[str] = None  # 单位


@dataclass_json
@dataclass
class V4MonitorHybridBoardDescribeViewReturnObjTargets:
    expr: Optional[str] = None  # prometheus表达式
    legendFormat: Optional[str] = None  # 图例格式化
    period: Optional[int] = None  # 周期
