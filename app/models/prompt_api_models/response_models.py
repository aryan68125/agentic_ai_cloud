from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional 

class APIResponse(BaseModel):
    status: int = Field(default=None)
    message : str = Field(default=None)
    data : Optional[Dict[str , Any]] = Field(default_factory=dict)

class APIResponseMultipleData(BaseModel):
    status: int = Field(default=None)
    message : str = Field(default=None)
    data : Optional[Any] = Field(default_factory=list)
