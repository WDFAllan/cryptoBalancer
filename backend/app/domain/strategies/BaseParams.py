from pydantic import BaseModel
from typing import Any, Dict

class BaseParams(BaseModel):
    params: Dict[str, Any]
