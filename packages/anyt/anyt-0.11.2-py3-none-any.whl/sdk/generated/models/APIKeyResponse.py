from typing import *
from pydantic import BaseModel, Field

class APIKeyResponse(BaseModel):
    """
    APIKeyResponse model
        API key information (without sensitive data).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    name : str = Field(validation_alias="name" )
    
    key_prefix : str = Field(validation_alias="key_prefix" )
    
    permissions : List[str] = Field(validation_alias="permissions" )
    
    is_active : bool = Field(validation_alias="is_active" )
    
    last_used_at : Union[str,None] = Field(validation_alias="last_used_at" )
    
    expires_at : Union[str,None] = Field(validation_alias="expires_at" )
    
    created_by : str = Field(validation_alias="created_by" )
    
    created_at : str = Field(validation_alias="created_at" )
    