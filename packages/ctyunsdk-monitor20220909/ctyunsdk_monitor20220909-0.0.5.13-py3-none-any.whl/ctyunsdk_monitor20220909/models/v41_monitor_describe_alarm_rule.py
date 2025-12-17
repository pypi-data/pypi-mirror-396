from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    alarmRuleID: str  # 告警规则ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V41MonitorDescribeAlarmRuleReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleReturnObj:
    alarmRule: Optional['V41MonitorDescribeAlarmRuleReturnObjAlarmRule'] = None  # 告警规则


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleReturnObjAlarmRule:
    regionID: Optional[str] = None  # 资源池ID
    alarmRuleID: Optional[str] = None  # 告警规则ID
    name: Optional[str] = None  # 规则名
    desc: Optional[str] = None  # 描述
    repeatTimes: Optional[int] = None  # 重复告警通知次数
    service: Optional[str] = None  # 服务
    dimension: Optional[str] = None  # 维度
    silenceTime: Optional[int] = None  # 静默时间，单位：秒
    recoverNotify: Optional[int] = None  # 本参数表示恢复是否通知。取值范围：<br>0：否。<br>1：是。<br>根据以上范围取值。
    notifyType: Optional[List[str]] = None  # 本参数表示告警接收策略。取值范围：<br>email：邮件告警。<br>sms：短信告警。<br>根据以上范围取值。
    contactGroupList: Optional[List['V41MonitorDescribeAlarmRuleReturnObjAlarmRuleContactGroupList']] = None  # 告警联系组
    notifyWeekdays: Optional[List[int]] = None  # 本参数表示通知周期。取值范围：<br>0：周日。<br>1：周一。<br>2：周二。<br>3：周三。<br>4：周四。<br>5：周五。<br>6：周六。<br>根据以上范围取值。
    notifyStart: Optional[str] = None  # 通知起始时段
    notifyEnd: Optional[str] = None  # 通知结束时段
    status: Optional[int] = None  # 本参数表示告警规则启用状态。取值范围：<br>0：启用。<br>1：停用。<br>根据以上范围取值。
    webhookUrl: Optional[List[str]] = None  # webhook消息推送url
    resGroupID: Optional[str] = None  # 资源分组ID
    createTime: Optional[int] = None  # 创建时间
    updateTime: Optional[int] = None  # 更新时间
    projectID: Optional[str] = None  # 项目ID
    resources: Optional[List['V41MonitorDescribeAlarmRuleReturnObjAlarmRuleResources']] = None  # 具体匹配资源
    condition: Optional[List['V41MonitorDescribeAlarmRuleReturnObjAlarmRuleCondition']] = None  # 触发规则的条件
    dimensions: Optional[List['V41MonitorDescribeAlarmRuleReturnObjAlarmRuleDimensions']] = None  # 自定义监控信息，仅支持部分资源池
    conditionType: Optional[int] = None  # 本参数表示告警策略触发类型。取值范围：<br>0：或，任一条件触发。<br>1：全部条件满足触发。<br>根据以上范围取值。
    alarmStatus: Optional[str] = None  # 本参数表示告警规则是否告警。取值范围：<br>0：未触发告警。<br>1：触发告警。<br>2：无数据（仅部分资源池支持）。<br>根据以上范围取值。
    alarmType: Optional[str] = None  # 告警规则类型。取值范围：<br>series：时序类监控。<br>event：事件类。<br>根据以上范围取值。
    project: Optional[str] = None  # 告警规则来源
    resourceScope: Optional[int] = None  # 规则的资源范围，取值范围：<br>0：实例资源类型。<br>1：资源分组类型。<br>2：全部资源类型 。 <br>根据以上范围取值。
    defaultContact: Optional[int] = None  # 是否使用天翼云默认联系人接收通知，取值范围：<br>0：否。<br>1：是。 <br>根据以上范围取值。
    noticeStrategyID: Optional[str] = None  # 通知策略ID
    test: Optional[object] = None


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleReturnObjAlarmRuleContactGroupList:
    groupID: Optional[str] = None  # 联系组ID
    name: Optional[str] = None  # 联系组名称


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleReturnObjAlarmRuleResources:
    resource: Optional[List['V41MonitorDescribeAlarmRuleReturnObjAlarmRuleResourcesResource']] = None  # 资源信息


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleReturnObjAlarmRuleResourcesResource:
    name: Optional[str] = None  # 资源实例标签键
    value: Optional[str] = None  # 资源实例标签值


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleReturnObjAlarmRuleCondition:
    evaluationCount: Optional[int] = None  # 持续次数，当规则执行结果持续多久符合条件时报警（防抖），默认2次
    metric: Optional[str] = None  # 监控指标
    metricCnName: Optional[str] = None  # 监控指标中文名
    fun: Optional[str] = None  # 本参数表示告警采用算法。取值范围：<br>last：原始值算法。<br>avg：平均值算法。<br>max：最大值算法。<br>min：最小值算法。<br>根据以上范围取值。
    operator: Optional[str] = None  # 本参数表示比较符。取值范围：<br>eq：等于。<br>gt：大于。<br>ge：大于等于。<br>lt：小于。<br>le：小于等于。<br>rg：环比上升。<br>cf：环比下降。<br>rc：环比变化。<br>根据以上范围取值。
    value: Optional[str] = None  # 告警阈值，可以是整数、小数或百分数格式字符串
    period: Optional[str] = None  # 本参数表示算法统计周期。默认值5m。<br>本参数格式为“数字+单位”。单位取值范围：<br>m：分钟。<br>h：小时。<br>d：天。<br>根据以上范围取值。
    unit: Optional[str] = None  # 监控指标单位
    level: Optional[int] = None  # 本参数表示告警等级。 取值范围：<br>1：紧急。<br>2：警示。<br>3：普通。<br>根据以上范围取值。


@dataclass_json
@dataclass
class V41MonitorDescribeAlarmRuleReturnObjAlarmRuleDimensions:
    name: Optional[str] = None  # 自定义监控资源实例标签键
    value: Optional[List[str]] = None  # 自定义监控资源实例标签值
