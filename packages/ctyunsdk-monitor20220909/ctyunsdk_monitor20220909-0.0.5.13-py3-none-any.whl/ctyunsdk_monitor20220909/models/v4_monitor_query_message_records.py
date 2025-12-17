from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorQueryMessageRecordsRequest(CtyunOpenAPIRequest):
    receiver: Optional[str] = None  # 通知对象
    recordType: Optional[int] = None  # 本参数表示通知类型。取值范围：<br>0：监控告警通知。<br>1：外部告警通知。<br>根据以上范围取值。
    method: Optional[str] = None  # 本参数表示通知方式。取值范围：<br>email：邮件。<br>sms：短信。<br>voice：语音。<br>webhook。<br>根据以上范围取值。
    recordStatus: Optional[int] = None  # 本参数表示通知状态。取值范围：<br>0：通知发送成功。<br>1：通知发送失败。<br>根据以上范围取值。
    packID: Optional[str] = None  # 套餐包ID
    subject: Optional[str] = None  # 通知主题模糊查询
    recvStatus: Optional[int] = None  # 此参数表示接收状态，取值范围：<br>1：成功。<br>2：失败。<br>&#32;根据以上范围取值。
    startTime: Optional[int] = None  # 创建通知起始时间，精确到毫秒，默认值：当时时间前31天的时间戳。
    endTime: Optional[int] = None  # 创建通知截止时间，精确到毫秒（截止时间与起始时间间隔不超过31天），默认值：当时时间戳。
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 每页大小，默认为20

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryMessageRecordsResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorQueryMessageRecordsReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorQueryMessageRecordsReturnObj:
    MessageRecords: Optional[List['V4MonitorQueryMessageRecordsReturnObjMessageRecords']] = None  # 通知记录列表
    totalCount: Optional[int] = None  # 总记录数
    currentCount: Optional[int] = None  # 当前页记录数
    totalPage: Optional[int] = None  # 总页数


@dataclass_json
@dataclass
class V4MonitorQueryMessageRecordsReturnObjMessageRecords:
    recordID: Optional[str] = None  # 通知记录ID
    receiver: Optional[str] = None  # 通知对象
    recordType: Optional[int] = None  # 本参数表示通知类型。取值范围：<br>0：监控告警通知。<br>1：外部告警通知。<br>根据以上范围取值。
    method: Optional[str] = None  # 本参数表示通知方式。取值范围：<br>email：邮件。<br>sms：短信。<br>webhook。<br>根据以上范围取值。
    recordStatus: Optional[int] = None  # 本参数表示通知状态。取值范围：<br>0：通知发送成功。<br>1：通知发送失败。<br>根据以上范围取值。
    subject: Optional[str] = None  # 通知主题
    content: Optional[str] = None  # 通知内容
    errMessage: Optional[str] = None  # 通知发送错误信息
    createTime: Optional[int] = None  # 创建时间，时间戳，精确到毫秒
    recvStatus: Optional[int] = None  # 此参数表示接收状态，取值范围：<br>1：成功。<br>2：失败。<br>&#32;根据以上范围取值。
    costFrom: Optional[str] = None  # 套餐包ID，costFrom值为空字符表示免费套餐包。
    cost: Optional[int] = None  # 实际消耗套餐包短信条数
