from typing import *
from pydantic import BaseModel, Field

class DependencyResponse(BaseModel):
    """
    DependencyResponse model
        Response for adding a dependency.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_id : str = Field(validation_alias="task_id" )
    
    depends_on : str = Field(validation_alias="depends_on" )
    
    blocked_by_status : str = Field(validation_alias="blocked_by_status" )
    
    created_at : str = Field(validation_alias="created_at" )
    