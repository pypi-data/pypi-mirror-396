from typing import *
from pydantic import BaseModel, Field

class DependencyTaskInfo(BaseModel):
    """
    DependencyTaskInfo model
        Minimal task info for dependency responses.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    identifier : str = Field(validation_alias="identifier" )
    
    title : str = Field(validation_alias="title" )
    
    status : str = Field(validation_alias="status" )
    
    priority : int = Field(validation_alias="priority" )
    