from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V41MonitorTaskCenterQueryTaskRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    taskID: Optional[str] = None  # 任务ID
    name: Optional[str] = None  # 任务名称，支持模糊搜索
    status: Optional[int] = None  # 本参数表示任务状态码。取值范围：<br>0：待处理。<br>1：处理中。<br>2：已完成。<br>3：失败。<br>4：过期。<br>根据以上范围取值。
    pageNo: Optional[int] = None  # 页码，不传默认为1
    pageSize: Optional[int] = None  # 每页大小，不传默认为20

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorTaskCenterQueryTaskResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V41MonitorTaskCenterQueryTaskReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V41MonitorTaskCenterQueryTaskReturnObj:
    taskList: Optional[List['V41MonitorTaskCenterQueryTaskReturnObjTaskList']] = None  # 任务列表
    totalCount: Optional[int] = None  # 总记录数
    totalPage: Optional[int] = None  # 总页数
    currentCount: Optional[int] = None  # 当前记录数


@dataclass_json
@dataclass
class V41MonitorTaskCenterQueryTaskReturnObjTaskList:
    taskID: Optional[str] = None  # 数据导出任务ID
    name: Optional[str] = None  # 任务名称
    description: Optional[str] = None  # 任务描述
    service: Optional[str] = None  # 云监控服务
    dimension: Optional[str] = None  # 云监控维度
    dimensions: Optional[List['V41MonitorTaskCenterQueryTaskReturnObjTaskListDimensions']] = None  # 查询设备标签列表，用于定位目标设备，多标签查询取交集
    itemNameList: Optional[List[str]] = None  # 待查的监控项名称，具体设备对应监控项参见[监控项列表：查询](https://www.ctyun.cn/document/10032263/10039882)
    aggregateType: Optional[List[str]] = None  # 本参数表示数据聚合类型。取值范围：<br>raw：原始值。<br>avg：平均值。<br>max：最大值。<br>min：最小值。<br>根据以上范围取值。
    startTime: Optional[int] = None  # 数据起始时间，秒级
    endTime: Optional[int] = None  # 数据截止时间，秒级
    period: Optional[int] = None  # 数据点间隔，秒级
    createTime: Optional[int] = None  # 创建时间,精确至毫秒
    updateTime: Optional[int] = None  # 更新时间,精确至毫秒
    status: Optional[int] = None  # 本参数表示任务状态码。取值范围：<br>0：待处理。<br>1：处理中。<br>2：已完成。<br>3：失败。<br>4：过期。<br>根据以上范围取值。
    process: Optional[int] = None  # 百分比进度，当status为1时有意义，范围 0-100
    msg: Optional[str] = None  # 任务详情，可用于展示报错信息


@dataclass_json
@dataclass
class V41MonitorTaskCenterQueryTaskReturnObjTaskListDimensions:
    name: Optional[str] = None  # 设备标签键
    value: Optional[List[str]] = None  # 设备标签键所对应的值
