from typing import *
from pydantic import BaseModel, Field

class DependencyGraphNode(BaseModel):
    """
    DependencyGraphNode model
        A node in the dependency graph representing a task.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : str = Field(validation_alias="id" )
    
    title : str = Field(validation_alias="title" )
    
    status : str = Field(validation_alias="status" )
    
    priority : int = Field(validation_alias="priority" )
    