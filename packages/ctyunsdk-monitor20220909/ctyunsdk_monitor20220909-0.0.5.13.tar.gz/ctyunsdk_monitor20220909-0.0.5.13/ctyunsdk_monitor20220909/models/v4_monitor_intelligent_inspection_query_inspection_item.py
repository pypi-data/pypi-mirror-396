from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryInspectionItemRequest(CtyunOpenAPIRequest):
    inspectionType: Optional[int] = None  # 本参数表示巡检类型，见巡检项查询接口返回。
    search: Optional[str] = None  # 模糊搜索

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryInspectionItemResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorIntelligentInspectionQueryInspectionItemReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryInspectionItemReturnObj:
    inspectionItemList: Optional[List['V4MonitorIntelligentInspectionQueryInspectionItemReturnObjInspectionItemList']] = None  # 巡检项列表


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryInspectionItemReturnObjInspectionItemList:
    productType: Optional[str] = None  # 本参数表示产品类型。
    inspectionType: Optional[int] = None  # 本参数表示巡检类型。
    inspectionItem: Optional[int] = None  # 本参数表示巡检项。
    inspectionName: Optional[str] = None  # 本参数表示巡检项名称
    level: Optional[int] = None  # 本参数表示重要等级。取值范围：<br>1：低。<br>2：中。<br>3：高。<br>根据以上范围取值。
    description: Optional[str] = None  # 巡检项描述
    status: Optional[bool] = None  # 本参数表示巡检项状态。取值范围：<br>true：启用。<br>false：停用。<br>根据以上范围取值。
    inspectionRules: Optional[List['V4MonitorIntelligentInspectionQueryInspectionItemReturnObjInspectionItemListInspectionRules']] = None  # 巡检规则列表


@dataclass_json
@dataclass
class V4MonitorIntelligentInspectionQueryInspectionItemReturnObjInspectionItemListInspectionRules:
    item: Optional[str] = None  # 监控项
    period: Optional[int] = None  # 巡检周期，在不同巡检项中对应巡检天数或预计未来天数
    fun: Optional[str] = None  # 本参数表示巡检算法。取值范围：<br>avg：平均值算法。<br>max：最大值算法。<br>min：最小值算法。<br>根据以上范围取值。
    operator: Optional[str] = None  # 本参数表示比较符。取值范围：<br>eq：等于。<br>gt：大于。<br>ge：大于等于。<br>lt：小于。<br>le：小于等于。<br>根据以上范围取值。
    value: Optional[float] = None  # 阈值
