from typing import *
from pydantic import BaseModel, Field
from .CodingAgentType import CodingAgentType
from .CodingAgentSettings import CodingAgentSettings

class CodingAgentConfig(BaseModel):
    """
    CodingAgentConfig model
        Full coding agent config schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    agent_type : CodingAgentType = Field(validation_alias="agent_type" )
    
    display_name : Optional[Union[str,None]] = Field(validation_alias="display_name" , default = None )
    
    is_enabled : Optional[bool] = Field(validation_alias="is_enabled" , default = None )
    
    config : Optional[Union[CodingAgentSettings,None]] = Field(validation_alias="config" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    user_id : Optional[Union[str,None]] = Field(validation_alias="user_id" , default = None )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    