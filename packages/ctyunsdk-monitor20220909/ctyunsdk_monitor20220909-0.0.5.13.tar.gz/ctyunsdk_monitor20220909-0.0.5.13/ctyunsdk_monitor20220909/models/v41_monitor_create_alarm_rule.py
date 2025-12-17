from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V41MonitorCreateAlarmRuleRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    name: str  # 规则名
    service: str  # 本参数表示服务。取值范围：<br>ecs：云主机。<br>evs：云硬盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    dimension: str  # 本参数表示告警维度。取值范围：<br>ecs：云主机。<br>disk：磁盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    conditions: List['V41MonitorCreateAlarmRuleRequestConditions']  # 具体告警匹配策略
    resources: List['V41MonitorCreateAlarmRuleRequestResources']  # 具体告警匹配资源
    desc: Optional[str] = None  # 规则描述
    repeatTimes: Optional[int] = None  # 重复告警通知次数，默认为0，当repeatTimes值为-1，代表无限重复。
    silenceTime: Optional[int] = None  # 告警接收策略静默时间，多久重复通知一次，单位：秒
    recoverNotify: Optional[int] = None  # 本参数表示恢复是否通知。默认值0。取值范围：<br>0：否。<br>1：是。<br>根据以上范围取值。
    notifyType: Optional[List[str]] = None  # 本参数表示告警接收策略。取值范围：<br>email：邮件告警。<br>sms：短信告警。<br>根据以上范围取值。
    contactGroupList: Optional[List[str]] = None  # 告警联系组
    notifyWeekdays: Optional[List[int]] = None  # 本参数表示通知周期。默认值[0,1,2,3,4,5,6]。取值范围：<br>0：周日。<br>1：周一。<br>2：周二。<br>3：周三。<br>4：周四。<br>5：周五。<br>6：周六。<br>根据以上范围取值。
    notifyStart: Optional[str] = None  # 通知起始时段，默认为00:00:00
    notifyEnd: Optional[str] = None  # 通知结束时段，默认为23:59:59
    webhookUrl: Optional[List[str]] = None  # webhook消息推送url
    resGroupID: Optional[str] = None  # 资源分组ID，与resources字段互斥。<br>&#32;1.以资源分组为资源对象的告警规则，不需要传入resources。<br>2\.非资源分组为资源对象的告警规则，resources为必填项。
    projectID: Optional[str] = None  # 项目ID
    conditionType: Optional[int] = None  # 本参数表示告警策略触发类型。默认值0。取值范围：<br>0：或，任一条件触发。<br>1：全部条件满足触发。<br>根据以上范围取值。
    resourceScope: Optional[int] = None  # 规则的资源范围，默认值0，取值范围：<br>0：实例资源类型。<br>1：资源分组类型。<br>2：全部资源类型 。 <br>根据以上范围取值。
    defaultContact: Optional[int] = None  # 是否使用天翼云默认联系人接收通知，默认值0，取值范围：<br>0：否。<br>1：是。 <br>根据以上范围取值。
    noticeStrategyID: Optional[str] = None  # 通知策略ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorCreateAlarmRuleRequestConditions:
    evaluationCount: int  # 持续次数，当规则执行结果持续多久符合条件时报警（防抖），默认2次
    metric: str  # 监控指标
    fun: str  # 本参数表示告警采用算法。取值范围：<br>last：原始值算法。<br>avg：平均值算法。<br>max：最大值算法。<br>min：最小值算法。<br>sum：求和算法。<br>根据以上范围取值。
    operator: str  # 本参数表示比较符。取值范围：<br>eq：等于。<br>gt：大于。<br>ge：大于等于。<br>lt：小于。<br>le：小于等于。<br>rg：环比上升。<br>cf：环比下降。<br>rc：环比变化。<br>根据以上范围取值。
    value: str  # 告警阈值，可以是整数、小数或百分数格式字符串
    unit: str  # 单位，部分资源池不支持，默认为空
    period: Optional[str] = None  # 本参数表示算法统计周期。默认值5m。<br>参数fun为last时不可传。<br>参数fun为avg、max、min均需填此参数。<br>本参数格式为“数字+单位”。单位取值范围：<br>m：分钟。<br>h：小时。<br>d：天。<br>根据以上范围取值。
    level: Optional[int] = None  # 本参数表示告警等级。默认值：3。 取值范围：<br>1：紧急。<br>2：警示。<br>3：普通。<br>根据以上范围取值。


@dataclass_json
@dataclass
class V41MonitorCreateAlarmRuleRequestResources:
    resource: List['V41MonitorCreateAlarmRuleRequestResourcesResource']  # 资源信息


@dataclass_json
@dataclass
class V41MonitorCreateAlarmRuleRequestResourcesResource:
    name: str  # 资源实例标签键
    value: str  # 资源实例标签值


@dataclass_json
@dataclass
class V41MonitorCreateAlarmRuleResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V41MonitorCreateAlarmRuleReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorCreateAlarmRuleReturnObj:
    alarmRuleIDList: Optional[List[str]] = None  # 告警规则ID列表
