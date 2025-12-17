from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorQueryAlertHistoryRequest(CtyunOpenAPIRequest):
    regionID: str  # ctyun资源池ID
    status: int  # 本参数表示状态。取值范围：<br>0：正在告警。<br>1：告警历史。<br>根据以上范围取值。
    resourceGroupID: Optional[str] = None  # 资源分组ID。
    searchKey: Optional[str] = None  # 本参数表示搜索关键词。取值范围：<br>alarmRuleID：告警规则ID，精确查询。<br>name：告警规则名称，模糊查询。<br>根据以上范围取值。
    searchValue: Optional[str] = None  # 配合searchKey使用，对应的值
    service: Optional[List[str]] = None  # 本参数表示告警服务。取值范围：<br>ecs：云主机。<br>evs：云硬盘。<br>pms：物理机。<br>...<br>详见"[云监控：查询服务维度及监控项](https://www.ctyun.cn/document/10032263/10747790)"接口返回。
    startTime: Optional[int] = None  # 查询状态为告警历史（参数status=1）时的起始时间戳，  默认值：24小时前时间戳，startTime和endTime需同时传或同时不传
    endTime: Optional[int] = None  # 查询状态为告警历史（参数status=1）时的结束时间戳，默认值：当前时间戳， 配合startTime一起使用
    pageNo: Optional[int] = None  # 页码，默认为1
    page: Optional[int] = None  # 页码，默认为1，建议使用pageNo，该参数后续会下线
    pageSize: Optional[int] = None  # 页大小，默认为10

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryAlertHistoryResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorQueryAlertHistoryReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryAlertHistoryReturnObj:
    issues: Optional[List['V4MonitorQueryAlertHistoryReturnObjIssues']] = None  # 告警事件列表
    totalCount: Optional[int] = None  # 总记录数
    currentCount: Optional[int] = None  # 当前页记录数
    page: Optional[int] = None  # 页码
    pageSize: Optional[int] = None  # 页大小
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4MonitorQueryAlertHistoryReturnObjIssues:
    regionID: Optional[str] = None  # ctyun资源池ID
    issueID: Optional[str] = None  # 告警历史ID
    alarmRuleID: Optional[str] = None  # 告警规则ID
    name: Optional[str] = None  # 告警规则名称
    status: Optional[int] = None  # 本参数表示告警状态。取值范围：<br>0：正在告警。<br>1：告警历史。<br>根据以上范围取值。
    dataStatus: Optional[int] = None  # 本参数表示正在告警下的状态细分。取值范围：<br>0：有数据。<br>1：无数据。<br>根据以上范围取值。
    expiredStatus: Optional[int] = None  # 本参数表示告警历史下的状态细分。取值范围：<br>0：正常历史告警。<br>1：已失效（告警规则已删除或已禁用）<br>根据以上范围取值。
    alarmType: Optional[str] = None  # 本参数表示告警类型。取值范围：<br>series：指标类型。<br>event：事件类型。<br>根据以上范围取值。
    service: Optional[str] = None  # 服务
    dimension: Optional[str] = None  # 维度
    notifyType: Optional[List[str]] = None  # 本参数表示告警接收策略。取值范围：<br>email：邮件告警。<br>sms：短信告警。<br>根据以上范围取值。
    duration: Optional[int] = None  # 持续时间，单位秒
    contactGroupList: Optional[List['V4MonitorQueryAlertHistoryReturnObjIssuesContactGroupList']] = None  # 所属组信息
    createTime: Optional[int] = None  # 触发时间的时间戳
    updateTime: Optional[int] = None  # 更新时间的时间戳
    resGroupID: Optional[str] = None  # 资源分组ID
    resGroupName: Optional[str] = None  # 资源分组名称
    resources: Optional[List['V4MonitorQueryAlertHistoryReturnObjIssuesResources']] = None  # 告警资源
    defaultContact: Optional[int] = None  # 是否使用天翼云默认联系人发送通知。默认值：0<br />0：否<br />1：是


@dataclass_json
@dataclass
class V4MonitorQueryAlertHistoryReturnObjIssuesContactGroupList:
    contactGroupID: Optional[str] = None  # 联系人组ID
    name: Optional[str] = None  # 联系人组名称


@dataclass_json
@dataclass
class V4MonitorQueryAlertHistoryReturnObjIssuesResources:
    name: Optional[str] = None  # 资源实例标签键
    value: Optional[str] = None  # 资源实例标签值
