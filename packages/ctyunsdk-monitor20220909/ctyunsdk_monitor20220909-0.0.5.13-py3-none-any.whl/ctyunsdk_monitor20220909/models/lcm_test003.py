from typing import Optional, List
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class LcmTest003Request:
    testString: str
    requiredBaseArray: List[str]
    requiredObjArray: List['LcmTest003RequestRequiredObjArray']
    requiredObj: 'LcmTest003RequestRequiredObj'
    testInt: Optional[int] = None
    notRequiredBaseArray: Optional[List[int]] = None
    notRequiredObjArray: Optional[List['LcmTest003RequestNotRequiredObjArray']] = None
    notRequiredObj: Optional['LcmTest003RequestNotRequiredObj'] = None


@dataclass_json
@dataclass
class LcmTest003RequestRequiredObjArray:
    test1: str
    test2: Optional[int] = None


@dataclass_json
@dataclass
class LcmTest003RequestNotRequiredObjArray:
    test3: Optional[str] = None
    test4: Optional[int] = None


@dataclass_json
@dataclass
class LcmTest003RequestRequiredObj:
    test5: str
    requiredObjNestedObj: 'LcmTest003RequestRequiredObjRequiredObjNestedObj'
    test6: Optional[int] = None
    notRequiredObjNestedObj: Optional['LcmTest003RequestRequiredObjNotRequiredObjNestedObj'] = None
    requiredObjNestedArray: Optional[List[str]] = None


@dataclass_json
@dataclass
class LcmTest003RequestRequiredObjRequiredObjNestedObj:
    test7: str
    requiredObjNestedObjArray: List[int]
    test8: Optional[bool] = None


@dataclass_json
@dataclass
class LcmTest003RequestRequiredObjNotRequiredObjNestedObj:
    test9: Optional[str] = None
    test10: Optional[int] = None


@dataclass_json
@dataclass
class LcmTest003RequestNotRequiredObj:
    test11: Optional[str] = None
    test12: Optional[str] = None



@dataclass_json
@dataclass
class LcmTest003Response:
    statusCode: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None
    description: Optional[str] = None
    errorCode: Optional[str] = None
    returnObj: Optional['LcmTest003ReturnObj'] = None


@dataclass_json
@dataclass
class LcmTest003ReturnObj:
    id: Optional[int] = None
    baseArray: Optional[List[str]] = None
    objArray: Optional[List['LcmTest003ReturnObjObjArray']] = None
    obj: Optional['LcmTest003ReturnObjObj'] = None


@dataclass_json
@dataclass
class LcmTest003ReturnObjObjArray:
    test1: Optional[str] = None
    test2: Optional[int] = None
    nestedObj: Optional['LcmTest003ReturnObjObjArrayNestedObj'] = None
    nestedArray: Optional[List[int]] = None
    nestedObjArray: Optional[List['LcmTest003ReturnObjObjArrayNestedObjArray']] = None


@dataclass_json
@dataclass
class LcmTest003ReturnObjObjArrayNestedObj:
    test3: Optional[str] = None
    test4: Optional[int] = None


@dataclass_json
@dataclass
class LcmTest003ReturnObjObjArrayNestedObjArray:
    test8: Optional[str] = None
    test9: Optional[int] = None


@dataclass_json
@dataclass
class LcmTest003ReturnObjObj:
    test5: Optional[str] = None
    test6: Optional[int] = None



