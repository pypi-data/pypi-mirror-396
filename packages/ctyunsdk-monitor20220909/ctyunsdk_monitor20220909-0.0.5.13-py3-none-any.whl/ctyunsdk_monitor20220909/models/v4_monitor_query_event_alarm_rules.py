from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorQueryEventAlarmRulesRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    service: Optional[str] = None  # 本参数表示服务。取值范围：<br>ecs：云主机。<br>evs：云硬盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    dimension: Optional[str] = None  # 本参数表示告警维度。取值范围：<br>ecs：云主机。<br>disk：磁盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    status: Optional[int] = None  # 本参数表示告警规则启用状态。取值范围：<br>0：启用。<br>1：停用。<br>根据以上范围取值。
    alarmStatus: Optional[int] = None  # 本参数表示告警规则告警状态。取值范围：<br>0：正常。<br>1：正在告警。<br>根据以上范围取值。
    name: Optional[str] = None  # 规则名称
    projectID: Optional[str] = None  # 项目ID
    sort: Optional[str] = None  # 本参数表示排序条件，-表示降序。支持的排序字段：<br>updateTime：更新时间。<br>根据以上范围取值。
    pageNo: Optional[int] = None  # 页码，默认值1
    pageSize: Optional[int] = None  # 页大小，默认值20

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryEventAlarmRulesResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorQueryEventAlarmRulesReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryEventAlarmRulesReturnObj:
    alarmRules: Optional[List[object]] = None  # 告警规则
    totalCount: Optional[int] = None  # 总记录数
    currentCount: Optional[int] = None  # 当前页记录数
    totalPage: Optional[int] = None  # 总页数
