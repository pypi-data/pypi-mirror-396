from typing import Annotated, List, Optional
from pydantic import BaseModel, BeforeValidator
import re

def coercive_float(v: any) -> float:
    if isinstance(v, (float, int)):
        return float(v)

    match = re.search(r'-?[\d,]+(?:\.\d+)?', str(v))
    if match:
        clean_str = match.group().replace(",", "")
        return float(clean_str)
    raise ValueError(f"No number found in {v}")

def coercive_bool(v: any) -> bool:
    if isinstance(v, bool):
        return v
    s = str(v).lower().strip()
    if s in ('yes', 'y', 'on', '1', 'true', 't'):
        return True
    if s in ('no', 'n', 'off', '0', 'false', 'f'):
        return False
 
    raise ValueError(f"Could not coerce {v} to bool")

def promote_to_list(v: any) -> list:
    if isinstance(v, list):
        return v

    if isinstance(v, str) and "," in v:
        return [item.strip() for item in v.split(",")]
    return [v]

ForceFloat = Annotated[float, BeforeValidator(coercive_float)]
ForceBool = Annotated[bool, BeforeValidator(coercive_bool)]
ForceList = Annotated[List[str], BeforeValidator(promote_to_list)]