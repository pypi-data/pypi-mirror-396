from typing import *
from pydantic import BaseModel, Field
from .CodingAgentType import CodingAgentType

class AssigneeCodingAgent(BaseModel):
    """
    AssigneeCodingAgent model
        Coding agent assignee for tasks - platform-supported AI coding tools.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    agent_type : CodingAgentType = Field(validation_alias="agent_type" )
    
    name : str = Field(validation_alias="name" )
    
    type : Optional[str] = Field(validation_alias="type" , default = None )
    
    is_enabled : Optional[bool] = Field(validation_alias="is_enabled" , default = None )
    