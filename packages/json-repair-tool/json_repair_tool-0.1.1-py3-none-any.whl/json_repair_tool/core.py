from typing import Type, TypeVar, Any, Dict, Union
import json_repair
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

def repair_json(
    llm_output: str, 
    schema: Type[T], 
    strict: bool = False
) -> T:
    
    clean_text = llm_output
    if "```" in clean_text:
        parts = clean_text.split("```")
        for part in parts:
            if "{" in part:
                clean_text = part
                if clean_text.strip().startswith("json"):
                    clean_text = clean_text.strip()[4:]
                break

    try:
        decoded_dict = json_repair.repair_json(clean_text, return_objects=True)
    except Exception as e:
        raise ValueError(f"Failed to repair JSON: {e}") from e

    if isinstance(decoded_dict, list):
        if len(decoded_dict) > 0 and isinstance(decoded_dict[0], dict):
            decoded_dict = decoded_dict[0]
        else:
             raise ValueError("Parsed JSON is a list, but model expects a single object.")

    try:
        return schema.model_validate(decoded_dict)
    except ValidationError as e:
        raise e