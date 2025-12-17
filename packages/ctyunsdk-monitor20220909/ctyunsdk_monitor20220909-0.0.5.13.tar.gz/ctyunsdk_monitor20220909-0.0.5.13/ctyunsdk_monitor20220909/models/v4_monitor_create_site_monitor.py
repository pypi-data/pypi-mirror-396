from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4MonitorCreateSiteMonitorRequest(CtyunOpenAPIRequest):
    taskName: str  # 站点监控任务名称，2-40个字符
    protocol: str  # 本参数表示探测类型。取值范围：<br>http：http探测。<br>ping：ping探测。<br>tcp：tcp探测。<br>udp：udp探测。<br>pagehttp：浏览器探测。<br>根据以上范围取值。
    address: str  # 站点地址。<br>ping示例：www.ctyun.cn<br>tcp/udp示例：www.ctyun.cn:80<br>http示例：http://www.ctyun.cn或https://www.ctyun.cn
    evalInterval: int  # 本参数表示探测间隔，单位秒。取值范围：<br>60：60s。<br>300：300s。<br>1200：1200s。<br>1800：1800s。<br>根据以上范围取值。
    probePoint: List[str]  # 探测节点ID列表，如['1','2']，可用探测节点ID可通过探测节点：查询列表接口获取
    options: Optional['V4MonitorCreateSiteMonitorRequestOptions'] = None  # 拨测参数

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCreateSiteMonitorRequestOptions:
    httpMethod: Optional[str] = None  # 本参数表示HTTP方法，默认GET。取值范围：<br>GET：GET方法。<br>POST：POST方法。<br>HEAD：HEAD方法。<br>根据以上范围取值。
    headers: Optional[str] = None  # 请求头信息，多个换行分隔
    cookies: Optional[str] = None  # 请求Cookies，多个用逗号分隔
    redirectLimit: Optional[int] = None  # 重定向次数限制，默认5，最大10
    verifySkip: Optional[bool] = None  # 本参数表示是否跳过验证校验，默认false。取值范围：<br>true：跳过。<br>false：不跳过。<br>根据以上范围取值。
    timeout: Optional[int] = None  # 超时时间，单位毫秒，最大为30000ms，protocol为http或pagehttp时，默认10000ms，protocol为ping或tcp时，默认2000ms，protocol为udp时，默认5000ms
    authUser: Optional[str] = None  # 用户名
    authPwd: Optional[str] = None  # 加密后的密码
    bodyContent: Optional[str] = None  # 请求体内容，json字符串
    dnsServer: Optional[str] = None  # DNS服务器，空为默认
    dnsHijackWhiteList: Optional[str] = None  # DNS劫持白名单，冒号前为要判断的域名，冒号后为白名单ip地址，多个ip用竖线分隔
    weekdays: Optional[List[int]] = None  # 本参数表示拨测日。默认值[0,1,2,3,4,5,6]。取值范围：<br>0：周日。<br>1：周一。<br>2：周二。<br>3：周三。<br>4：周四。<br>5：周五。<br>6：周六。<br>根据以上范围取值。
    startTime: Optional[str] = None  # 拨测起始时段，默认为00:00:00
    endTime: Optional[str] = None  # 拨测结束时段，默认为23:59:59
    responseAssertions: Optional[List['V4MonitorCreateSiteMonitorRequestOptionsResponseAssertions']] = None  # Response断言，当条件均满足时，则判断为正常，默认空不做断言
    deviceType: Optional[str] = None  # 本参数表示设备类型，默认PC。取值范围：<br>PC：PC端。<br>根据以上范围取值。
    browserType: Optional[str] = None  # 本参数表示浏览器，默认Chrome。取值范围：<br>Chrome：Chrome浏览器。<br>根据以上范围取值。
    autoScrolling: Optional[bool] = None  # 本参数表示自动滚屏是否启动，默认false。取值范围：<br>false：不启动。<br>根据以上范围取值。


@dataclass_json
@dataclass
class V4MonitorCreateSiteMonitorRequestOptionsResponseAssertions:
    assertionType: str  # 断言方式，取值范围：<br>statusCode：状态码。<br>bodyJson：body的json字段。<br>firstScreenTime：首屏用时。<br>totalTime：整体性能。<br>根据以上范围取值。
    operator: str  # 断言方式，其中大于小于判断会尝试将结果转为浮点数，如转换失败则断言不通过。取值范围：<br>lessThan：小于。<br>greatThan：大于。<br>equal：等于。<br>notEqual：不等于。<br>contains：包含。<br>notContains: 不包含。<br>regexMatch：正则匹配。<br>regexNotMatch：正则不匹配。<br>根据以上范围取值。
    value: str  # 匹配值
    jsonPath: Optional[str] = None  # jsonPath,当断言方式为bodyJson时，此字段必填。


@dataclass_json
@dataclass
class V4MonitorCreateSiteMonitorResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4MonitorCreateSiteMonitorReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4MonitorCreateSiteMonitorReturnObj:
    taskID: Optional[str] = None  # 站点监控任务ID
