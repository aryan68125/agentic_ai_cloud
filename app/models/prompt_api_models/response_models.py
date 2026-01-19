from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional 

class PromptResponse(BaseModel):
    status: str = Field(default=None)
    message : str = Field(default="")
    data : Dict[str : Any] = Field(default={})
