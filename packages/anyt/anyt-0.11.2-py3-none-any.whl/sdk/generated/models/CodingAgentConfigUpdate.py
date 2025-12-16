from typing import *
from pydantic import BaseModel, Field
from .CodingAgentSettings import CodingAgentSettings

class CodingAgentConfigUpdate(BaseModel):
    """
    CodingAgentConfigUpdate model
        Fields that can be updated (all optional).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    display_name : Optional[Union[str,None]] = Field(validation_alias="display_name" , default = None )
    
    is_enabled : Optional[Union[bool,None]] = Field(validation_alias="is_enabled" , default = None )
    
    config : Optional[Union[CodingAgentSettings,None]] = Field(validation_alias="config" , default = None )
    