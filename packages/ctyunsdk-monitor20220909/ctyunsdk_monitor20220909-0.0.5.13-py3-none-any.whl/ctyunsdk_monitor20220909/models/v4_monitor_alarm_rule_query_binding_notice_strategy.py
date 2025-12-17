from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorAlarmRuleQueryBindingNoticeStrategyRequest(CtyunOpenAPIRequest):
    regionID: str  # ctyun资源池ID
    noticeStrategyID: str  # 通知策略ID
    service: str  # 本参数表示服务。取值范围：<br>ecs：云主机。<br>evs：云硬盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    dimension: str  # 云监控维度。取值范围： <br />ecs：云主机。 <br />disk：云硬盘。 <br />pms：物理机。 <br />... <br />具体服务参见[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 页大小，默认为20
    alarmRuleName: Optional[str] = None  # 告警规则名称，支持模糊查询

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorAlarmRuleQueryBindingNoticeStrategyResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorAlarmRuleQueryBindingNoticeStrategyReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorAlarmRuleQueryBindingNoticeStrategyReturnObj:
    alarmRules: Optional[List['V4MonitorAlarmRuleQueryBindingNoticeStrategyReturnObjAlarmRules']] = None  # 告警规则
    totalCount: Optional[int] = None  # 总记录数
    currentCount: Optional[int] = None  # 当前页记录数
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4MonitorAlarmRuleQueryBindingNoticeStrategyReturnObjAlarmRules:
    alarmRuleID: Optional[str] = None  # 告警规则ID
    alarmRuleName: Optional[str] = None  # 规则名
    service: Optional[str] = None  # 服务
    status: Optional[int] = None  # 本参数表示告警规则启用状态。取值范围：<br>0：启用。<br>1：停用。<br>根据以上范围取值。
