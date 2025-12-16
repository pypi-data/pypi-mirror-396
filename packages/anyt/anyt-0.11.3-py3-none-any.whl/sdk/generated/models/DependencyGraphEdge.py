from typing import *
from pydantic import BaseModel, Field

class DependencyGraphEdge(BaseModel):
    """
    DependencyGraphEdge model
        An edge in the dependency graph representing a dependency relationship.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    from_task : str = Field(validation_alias="from_task" )
    
    to_task : str = Field(validation_alias="to_task" )
    
    blocking : bool = Field(validation_alias="blocking" )
    