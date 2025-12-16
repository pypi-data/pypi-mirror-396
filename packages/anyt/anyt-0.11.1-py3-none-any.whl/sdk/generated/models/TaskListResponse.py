from typing import *
from pydantic import BaseModel, Field
from .Task import Task

class TaskListResponse(BaseModel):
    """
    TaskListResponse model
        Response for paginated task list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    items : List[Task] = Field(validation_alias="items" )
    
    total : int = Field(validation_alias="total" )
    