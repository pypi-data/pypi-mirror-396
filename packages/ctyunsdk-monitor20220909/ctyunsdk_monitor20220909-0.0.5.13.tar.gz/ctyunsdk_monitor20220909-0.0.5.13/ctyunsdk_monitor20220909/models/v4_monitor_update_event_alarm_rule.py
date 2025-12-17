from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorUpdateEventAlarmRuleRequest(CtyunOpenAPIRequest):
    alarmRuleID: str  # 告警规则ID
    regionID: str  # 资源池ID
    name: str  # 规则名
    service: str  # 本参数表示服务。取值范围：<br>ecs：云主机。<br>evs：云硬盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    dimension: str  # 本参数表示告警维度。取值范围：<br>ecs：云主机。<br>disk：磁盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    conditions: List[object]  # 具体匹配策略
    resources: List['V4MonitorUpdateEventAlarmRuleRequestResources']  # 资源信息列表
    desc: Optional[str] = None  # 描述
    repeatTimes: Optional[int] = None  # 重复告警通知次数，默认为0，当repeatTimes值为-1，代表无限重复。
    silenceTime: Optional[int] = None  # 告警接收策略静默时间，多久重复通知一次，单位为秒
    recoverNotify: Optional[int] = None  # 本参数表示恢复是否通知。默认值0。取值范围：<br>0：否。<br>1：是。<br>根据以上范围取值。
    notifyType: Optional[List[str]] = None  # 本参数表示告警接收策略。取值范围：<br>email：邮件告警。<br>sms：短信告警。<br>根据以上范围取值。
    contactGroupList: Optional[List[str]] = None  # 告警联系人组
    notifyWeekdays: Optional[List[int]] = None  # 本参数表示通知周期。默认值[0,1,2,3,4,5,6]。取值范围：<br>0：周日。<br>1：周一。<br>2：周二。<br>3：周三。<br>4：周四。<br>5：周五。<br>6：周六。<br>根据以上范围取值。
    notifyStart: Optional[str] = None  # 通知起始时段，默认为00:00:00
    notifyEnd: Optional[str] = None  # 通知结束时段，默认为23:59:59
    webhookUrl: Optional[List[str]] = None  # 告警状态变更webhook推送地址
    projectID: Optional[str] = None  # 项目ID
    resourceScope: Optional[int] = None  # 规则的资源范围，默认值0，取值范围：<br>0：实例资源类型。<br>1：资源分组类型。<br>2：全部资源类型 。 <br>根据以上范围取值。
    defaultContact: Optional[int] = None  # 是否使用天翼云默认联系人接收通知，默认值0，取值范围：<br>0：否。<br>1：是。 <br>根据以上范围取值。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorUpdateEventAlarmRuleRequestResources:
    resource: List[object]  # 资源信息


@dataclass_json
@dataclass
class V4MonitorUpdateEventAlarmRuleResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorUpdateEventAlarmRuleReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorUpdateEventAlarmRuleReturnObj:
    success: Optional[bool] = None  # 是否成功
