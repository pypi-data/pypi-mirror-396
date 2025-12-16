from typing import *
from pydantic import BaseModel, Field

class ProjectDeleteResponse(BaseModel):
    """
    ProjectDeleteResponse model
        Response for project deletion with cascade statistics.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    deleted : bool = Field(validation_alias="deleted" )
    
    project_id : int = Field(validation_alias="project_id" )
    
    tasks_deleted : int = Field(validation_alias="tasks_deleted" )
    
    failed_tasks : int = Field(validation_alias="failed_tasks" )
    