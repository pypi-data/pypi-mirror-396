from typing import *
from pydantic import BaseModel, Field
from .AssigneeUser import AssigneeUser
from .AssigneeCodingAgent import AssigneeCodingAgent

class AssigneesData(BaseModel):
    """
    AssigneesData model
        Data structure for assignees with users and coding_agents arrays.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    users : Optional[List[Optional[AssigneeUser]]] = Field(validation_alias="users" , default = None )
    
    coding_agents : Optional[List[Optional[AssigneeCodingAgent]]] = Field(validation_alias="coding_agents" , default = None )
    