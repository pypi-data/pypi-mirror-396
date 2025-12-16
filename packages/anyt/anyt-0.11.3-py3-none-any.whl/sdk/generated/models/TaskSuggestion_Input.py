from typing import *
from pydantic import BaseModel, Field
from .Task import Task

class TaskSuggestion_Input(BaseModel):
    """
    TaskSuggestion model
        Single task suggestion with readiness and dependency information.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task : Task = Field(validation_alias="task" )
    
    is_ready : bool = Field(validation_alias="is_ready" )
    
    blocked_by : Optional[List[str]] = Field(validation_alias="blocked_by" , default = None )
    
    blocks : Optional[List[str]] = Field(validation_alias="blocks" , default = None )
    