from typing import *
from pydantic import BaseModel, Field

class AssigneeUser(BaseModel):
    """
    AssigneeUser model
        User assignee for tasks.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : str = Field(validation_alias="id" )
    
    type : Optional[str] = Field(validation_alias="type" , default = None )
    