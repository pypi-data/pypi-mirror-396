from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateViewRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    viewID: str  # 监控视图ID
    view: 'V4MonitorMonitorBoardUpdateViewRequestView'  # 监控视图更新内容

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateViewRequestView:
    name: str  # 监控视图名称
    service: str  # 本参数表示云监控服务。取值范围：<br>ecs：云主机。<br>...<br>具体服务参见[云监控：查询服务维度及监控项](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15746&data=90&isNormal=1&vid=84)
    dimension: str  # 本参数表示云监控维度。取值范围：<br>ecs：云主机。<br>...<br>具体服务参见[云监控：查询服务维度及监控项](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15746&data=90&isNormal=1&vid=84)
    viewType: str  # 视图类型。取值范围:<br>timeSeries：折线图。<br>gauge：仪表盘。<br>barChart：柱状图。<br>table：表格。<br>pieChart：饼状图。<br>根据以上范围取值。
    itemNameList: List[str]  # 监控指标，指标项最多支持20个，当viewType为gauge和pieChart时，仅支持单监控指标
    resources: List['V4MonitorMonitorBoardUpdateViewRequestViewResources']  # 监控资源实例，监控资源实例最多支持20个，当viewType为gauge时，仅支持单资源实例
    orderIndex: Optional[int] = None  # 视图排序次数。默认值为0。
    compares: Optional[List[str]] = None  # 同比环比比较时间配置，格式为“数字+单位”，单位为空时默认为秒。<br>当前只支持1d和7d。<br>单位取值范围：<br>m：分钟。<br>h：小时。<br>d：天。<br>根据以上范围取值。
    gaugePattern: Optional['V4MonitorMonitorBoardUpdateViewRequestViewGaugePattern'] = None  # 仪表盘配置，仅当viewType为gauge时生效


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateViewRequestViewResources:
    resource: List['V4MonitorMonitorBoardUpdateViewRequestViewResourcesResource']  # 资源


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateViewRequestViewResourcesResource:
    key: str  # 资源实例标签键
    value: str  # 资源实例标签值


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateViewRequestViewGaugePattern:
    minVal: Optional[int] = None  # 仪表盘最小值。默认值为0
    maxVal: Optional[int] = None  # 仪表盘最大值。默认值为100
    threshold: Optional[List[int]] = None  # 仪表盘中间分段取值，长度必须为2。默认值为[30,80]


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateViewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorMonitorBoardUpdateViewReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorMonitorBoardUpdateViewReturnObj:
    success: Optional[bool] = None  # 是否更新成功
