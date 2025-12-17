import re
from typing import Any, List, Optional, Union
from pydantic import BeforeValidator
from typing_extensions import Annotated

def _coerce_float(v: Any) -> float:
    if isinstance(v, (float, int)):
        return float(v)
    
    s = str(v)
    match = re.search(r'-?[\d,]+(?:\.\d+)?', s)
    if not match:
        raise ValueError(f"Could not find a valid number in '{v}'")
    
    clean_num = match.group().replace(",", "")
    return float(clean_num)

def _coerce_int(v: Any) -> int:
    return int(_coerce_float(v))

def _coerce_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    
    s = str(v).strip().lower()
    
    if s in {'yes', 'y', 'on', 'true', 't', '1', 'enable', 'active', 'ok', 'correct'}:
        return True
    
    if s in {'no', 'n', 'off', 'false', 'f', '0', 'disable', 'inactive', 'wrong'}:
        return False
        
    raise ValueError(f"Could not interpret '{v}' as a boolean.")

def _coerce_list(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    
    if isinstance(v, str) and "," in v:
        return [item.strip() for item in v.split(",") if item.strip()]
        
    return [v]

def _coerce_none(v: Any) -> Optional[Any]:
    if v is None:
        return None
    
    s = str(v).strip().lower()
    if s in {'n/a', 'null', 'none', 'unknown', 'undefined', 'not provided', '-', '?'}:
        return None
    return v

ForceFloat = Annotated[float, BeforeValidator(_coerce_float)]
ForceInt = Annotated[int, BeforeValidator(_coerce_int)]
ForceBool = Annotated[bool, BeforeValidator(_coerce_bool)]
ForceList = Annotated[List[Any], BeforeValidator(_coerce_list)]

def ForceOptional(inner_type: Any) -> Any:
    return Annotated[Optional[inner_type], BeforeValidator(_coerce_none)]