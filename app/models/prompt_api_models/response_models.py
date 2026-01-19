from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional 

class PromptResponse(BaseModel):
    status: int = Field(default=None)
    message : str = Field(default=None)
    data : Optional[Dict[str , Any]] = Field(default_factory=dict)
