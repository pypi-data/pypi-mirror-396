from typing import *
from pydantic import BaseModel, Field
from .DependencyGraphNode import DependencyGraphNode
from .DependencyGraphEdge import DependencyGraphEdge

class DependencyGraphResponse(BaseModel):
    """
    DependencyGraphResponse model
        Complete dependency graph response.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    nodes : List[DependencyGraphNode] = Field(validation_alias="nodes" )
    
    edges : List[DependencyGraphEdge] = Field(validation_alias="edges" )
    