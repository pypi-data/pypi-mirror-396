from typing import *
from pydantic import BaseModel, Field

class CreateAPIKeyRequest(BaseModel):
    """
    CreateAPIKeyRequest model
        Request to create a new API key.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    permissions : Optional[List[str]] = Field(validation_alias="permissions" , default = None )
    
    expires_at : Optional[Union[str,None]] = Field(validation_alias="expires_at" , default = None )
    