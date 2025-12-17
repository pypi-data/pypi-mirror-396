from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesRequest(CtyunOpenAPIRequest):
    pageNo: Optional[int] = None  # 页码，默认为1
    pageSize: Optional[int] = None  # 页大小，默认为10
    name: Optional[str] = None  # 模板名称模糊搜索
    showDetail: Optional[bool] = None  # 展示模板详细信息，默认为false不展示
    sort: Optional[List['V4MonitorHybridBoardViewTemplatesRequestSort']] = None  # 排序

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesRequestSort:
    sortKey: Optional[str] = None  # 搜索关键词
    sortType: Optional[str] = None  # 搜索排序方式。取值范围：<br>ASC：正序。<br>DESC：倒序。<br>根据以上范围取值。


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorHybridBoardViewTemplatesReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesReturnObj:
    currentCount: Optional[int] = None  # 当前页记录数
    totalCount: Optional[int] = None  # 总记录数
    totalPage: Optional[int] = None  # 总页数
    viewTemplates: Optional[List['V4MonitorHybridBoardViewTemplatesReturnObjViewTemplates']] = None  # 监控大盘模板内容，仅当showDetail为true时有该字段


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesReturnObjViewTemplates:
    name: Optional[str] = None  # 大盘模板名称
    description: Optional[str] = None  # 大盘模板描述
    viewTemplateID: Optional[str] = None  # 大盘模板ID
    views: Optional[List['V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViews']] = None  # 模板视图内容


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViews:
    name: Optional[str] = None  # 模板视图名称
    type: Optional[str] = None  # 视图类型。取值范围:<br>timeSeries：折线图。<br>barChart：柱状图。<br>根据以上范围取值。
    description: Optional[str] = None  # 视图描述
    datasource: Optional['V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsDatasource'] = None  # 数据源
    fieldConfig: Optional['V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsFieldConfig'] = None  # 字段配置
    targets: Optional[List['V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsTargets']] = None


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsDatasource:
    type: Optional[str] = None  # 数据类型。取值范围:<br>prometheus<br>根据以上范围取值。
    namespace: Optional[str] = None  # 指标仓库名称


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsFieldConfig:
    defaults: Optional['V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsFieldConfigDefaults'] = None  # 默认配置


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsFieldConfigDefaults:
    unit: Optional[str] = None  # 单位


@dataclass_json
@dataclass
class V4MonitorHybridBoardViewTemplatesReturnObjViewTemplatesViewsTargets:
    expr: Optional[str] = None  # prometheus表达式
    legendFormat: Optional[str] = None  # 图例格式化
    period: Optional[int] = None  # 周期
