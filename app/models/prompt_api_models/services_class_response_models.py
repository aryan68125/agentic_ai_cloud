from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional 

class ProcessPromptServiceClassResponse(BaseModel):
    status : bool = Field(default_factory=False)
    message : str = Field(default=None)
    data : Optional[Dict[str , Any]] = Field(default_factory=dict)
