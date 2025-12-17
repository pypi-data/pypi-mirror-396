from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorMonitorBoardDescribeViewRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    viewID: str  # 监控视图ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardDescribeViewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorMonitorBoardDescribeViewReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardDescribeViewReturnObj:
    viewID: Optional[str] = None  # 监控视图ID
    name: Optional[str] = None  # 监控视图名称
    service: Optional[str] = None  # 云监控服务，具体含义参见[云监控：查询服务维度及监控项](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15746&data=90&isNormal=1&vid=84)
    dimension: Optional[str] = None  # 云监控维度，具体含义参见[云监控：查询服务维度及监控项](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15746&data=90&isNormal=1&vid=84)
    viewType: Optional[str] = None  # 视图类型。取值范围:<br>timeSeries：折线图。<br>gauge：仪表盘。<br>barChart：柱状图。<br>table：表格。<br>pieChart：饼状图。<br>根据以上范围取值。
    orderIndex: Optional[int] = None  # 排序次序，相同则按照updateTime降序。
    itemNameList: Optional[List[str]] = None  # 监控指标，指标项最多支持20个
    compares: Optional[List[str]] = None  # 同比环比比较时间配置，格式为“数字+单位”，单位为空时默认为秒。<br>单位取值范围：<br>m：分钟。<br>h：小时。<br>d：天。<br>根据以上范围取值。
    resources: Optional[List['V4MonitorMonitorBoardDescribeViewReturnObjResources']] = None  # 监控资源实例 ,监控资源实例最多支持20个
    gaugePattern: Optional['V4MonitorMonitorBoardDescribeViewReturnObjGaugePattern'] = None  # 仪表盘配置，仅当viewType为gaugePattern时有效
    createTime: Optional[int] = None  # 创建时间，时间戳，精确到秒
    updateTime: Optional[int] = None  # 最近更新时间, 时间戳，精确到秒


@dataclass_json
@dataclass
class V4MonitorMonitorBoardDescribeViewReturnObjResources:
    resource: Optional[List['V4MonitorMonitorBoardDescribeViewReturnObjResourcesResource']] = None  # 资源


@dataclass_json
@dataclass
class V4MonitorMonitorBoardDescribeViewReturnObjResourcesResource:
    key: Optional[str] = None  # 资源实例标签键
    value: Optional[str] = None  # 资源实例标签值


@dataclass_json
@dataclass
class V4MonitorMonitorBoardDescribeViewReturnObjGaugePattern:
    minVal: Optional[int] = None  # 仪表盘最小值
    maxVal: Optional[int] = None  # 仪表盘最大值
    threshold: Optional[List[int]] = None  # 仪表盘中间分段取值
