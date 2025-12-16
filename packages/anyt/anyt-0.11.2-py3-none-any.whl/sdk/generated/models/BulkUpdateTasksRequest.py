from typing import *
from pydantic import BaseModel, Field
from .TaskUpdate import TaskUpdate

class BulkUpdateTasksRequest(BaseModel):
    """
    BulkUpdateTasksRequest model
        Request for bulk updating tasks.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_ids : List[str] = Field(validation_alias="task_ids" )
    
    updates : TaskUpdate = Field(validation_alias="updates" )
    