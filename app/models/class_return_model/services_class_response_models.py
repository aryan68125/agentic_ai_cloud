from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional 

class ServiceClassResponse(BaseModel):
    status : bool = Field(default_factory = False)
    message : str = Field(default = None)
    data : Optional[Dict[str , Any]] = Field(default_factory=dict)

class RepositoryClassResponse(BaseModel):
    status : bool = Field(default_factory = False)
    status_code : Optional[int] = Field(default_factory=None)
    message : str = Field(default = None)
    data : Optional[Any] = Field(default_factory=dict)

class ToolControlsignalResponse(BaseModel):
    status : bool = Field(default_factory = False)
    status_code : Optional[int] = Field(default_factory=None)
    message : str = Field(default = None)
    data : Optional[Any] = Field(default_factory=dict)
    response_type : str