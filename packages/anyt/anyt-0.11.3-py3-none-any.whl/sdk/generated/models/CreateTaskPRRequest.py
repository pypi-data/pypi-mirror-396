from typing import *
from pydantic import BaseModel, Field
from .PRStatus import PRStatus

class CreateTaskPRRequest(BaseModel):
    """
    CreateTaskPRRequest model
        Request for creating a pull request for a task.

The task is identified via the URL path parameter (task identifier).
Pull requests are workspace-scoped and linked to tasks.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    pr_number : int = Field(validation_alias="pr_number" )
    
    pr_url : str = Field(validation_alias="pr_url" )
    
    head_branch : str = Field(validation_alias="head_branch" )
    
    base_branch : str = Field(validation_alias="base_branch" )
    
    head_sha : str = Field(validation_alias="head_sha" )
    
    pr_status : Optional[PRStatus] = Field(validation_alias="pr_status" , default = None )
    