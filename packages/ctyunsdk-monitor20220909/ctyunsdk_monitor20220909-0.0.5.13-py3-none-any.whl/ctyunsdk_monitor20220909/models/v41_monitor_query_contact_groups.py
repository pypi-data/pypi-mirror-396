from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V41MonitorQueryContactGroupsRequest(CtyunOpenAPIRequest):
    name: Optional[str] = None  # 组名
    search: Optional[str] = None  # 模糊搜索，可搜索字段为联系人的：告警联系组组名（name）、告警联系人姓名（name）、告警联系人手机号（phone）、告警联系人邮箱（email）
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 每页大小

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorQueryContactGroupsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V41MonitorQueryContactGroupsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorQueryContactGroupsReturnObj:
    contactGroupList: Optional[List['V41MonitorQueryContactGroupsReturnObjContactGroupList']] = None  # 告警联系人组列表
    totalCount: Optional[int] = None  # 总记录数
    currentCount: Optional[int] = None  # 当前页记录数
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V41MonitorQueryContactGroupsReturnObjContactGroupList:
    contactGroupID: Optional[str] = None  # 告警联系人组ID
    name: Optional[str] = None  # 组名
    desc: Optional[str] = None  # 组备注
    contactList: Optional[List['V41MonitorQueryContactGroupsReturnObjContactGroupListContactList']] = None  # 告警联系人列表
    updateTime: Optional[int] = None  # 最近更新时间, 时间戳，精确到毫秒
    createTime: Optional[int] = None  # 创建时间，时间戳，精确到毫秒


@dataclass_json
@dataclass
class V41MonitorQueryContactGroupsReturnObjContactGroupListContactList:
    contactID: Optional[str] = None  # 告警联系人ID
    name: Optional[str] = None  # 用户名
    phone: Optional[str] = None  # 手机号
    email: Optional[str] = None  # 邮箱
    updateTime: Optional[int] = None  # 最近更新时间, 时间戳，精确到毫秒
    createTime: Optional[int] = None  # 创建时间，时间戳，精确到毫秒
    phoneActivation: Optional[int] = None  # 本参数表示手机号码是否激活。取值范围：<br>1：已激活。<br>0：未激活。<br>根据以上范围取值。
    emailActivation: Optional[int] = None  # 本参数表示邮箱是否激活。取值范围：<br>1：已激活。<br>0：未激活。<br>根据以上范围取值。
