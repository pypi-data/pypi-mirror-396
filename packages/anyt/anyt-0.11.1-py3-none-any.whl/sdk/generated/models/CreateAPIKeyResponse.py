from typing import *
from pydantic import BaseModel, Field
from .APIKeyResponse import APIKeyResponse

class CreateAPIKeyResponse(BaseModel):
    """
    CreateAPIKeyResponse model
        Response when creating a new API key (includes full key once).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    key : str = Field(validation_alias="key" )
    
    api_key : APIKeyResponse = Field(validation_alias="api_key" )
    