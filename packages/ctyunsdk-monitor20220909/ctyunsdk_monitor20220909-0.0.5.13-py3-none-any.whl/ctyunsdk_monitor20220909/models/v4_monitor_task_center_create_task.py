from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorTaskCenterCreateTaskRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    task: 'V4MonitorTaskCenterCreateTaskRequestTask'  # 任务的具体参数

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorTaskCenterCreateTaskRequestTask:
    name: str  # 任务名称，必须4-20个字符，支持中英文、数字、下划线
    service: str  # 云监控服务。取值范围： <br />ecs：云主机。 <br />evs：云硬盘。 <br />pms：物理机。 <br />... <br />具体服务参见[云监控：查询服务维度及监控项](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15746&data=90&isNormal=1&vid=84)
    dimension: str  # 云监控维度。取值范围： <br />ecs：云主机。 <br />disk：云硬盘。 <br />pms：物理机。 <br />... <br />具体服务参见[云监控：查询服务维度及监控项](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15746&data=90&isNormal=1&vid=84)
    dimensions: List['V4MonitorTaskCenterCreateTaskRequestTaskDimensions']  # 查询设备标签列表，用于定位目标设备，多标签查询取交集，不传默认全量
    itemNameList: List[str]  # 待查的监控项名称，具体设备对应监控项参见[云监控：查询服务维度及监控项](https://eop.ctyun.cn/ebp/ctapiDocument/search?sid=22&api=15746&data=90&isNormal=1&vid=84)
    aggregateType: List[str]  # 本参数表示数据聚合类型。取值范围：<br>raw：原始值。<br>avg：平均值。<br>max：最大值。<br>min：最小值。<br>根据以上范围取值。
    startTime: int  # 数据起始时间，秒级
    endTime: int  # 数据截止时间，秒级
    description: Optional[str] = None  # 任务描述，最多50个字符
    period: Optional[int] = None  # 聚合周期（除raw外其他聚合类型必传），单位：秒
    reportTemplate: Optional[int] = None  # 本参数表示报表模板。默认值为0。取值范围：<br>0：默认报表模板。<br>1：基础报表模板。<br>根据以上范围取值。
    isSecond: Optional[bool] = None  # 本参数表示是否秒级监控。默认值false。取值范围：<br>true：是。<br>false：不是。<br>根据以上范围取值。


@dataclass_json
@dataclass
class V4MonitorTaskCenterCreateTaskRequestTaskDimensions:
    name: str  # 设备标签键
    value: List[str]  # 设备标签键所对应的值


@dataclass_json
@dataclass
class V4MonitorTaskCenterCreateTaskResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorTaskCenterCreateTaskReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorTaskCenterCreateTaskReturnObj:
    taskID: Optional[str] = None  # 数据导出任务ID
