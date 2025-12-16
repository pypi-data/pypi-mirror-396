from typing import *
from pydantic import BaseModel, Field

class CodingAgentSettings(BaseModel):
    """
    CodingAgentSettings model
        Settings schema for the config JSONB field.

These are agent-specific configuration options that control how
the coding agent behaves when executing tasks.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    model : Optional[Union[str,None]] = Field(validation_alias="model" , default = None )
    
    custom_system_prompt : Optional[Union[str,None]] = Field(validation_alias="custom_system_prompt" , default = None )
    
    additional_args : Optional[List[str]] = Field(validation_alias="additional_args" , default = None )
    
    timeout_seconds : Optional[Union[int,None]] = Field(validation_alias="timeout_seconds" , default = None )
    
    max_retries : Optional[Union[int,None]] = Field(validation_alias="max_retries" , default = None )
    
    environment_vars : Optional[Dict[str, Any]] = Field(validation_alias="environment_vars" , default = None )
    