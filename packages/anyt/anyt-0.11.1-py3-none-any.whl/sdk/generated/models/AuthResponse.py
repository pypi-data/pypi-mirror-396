from typing import *
from pydantic import BaseModel, Field

class AuthResponse(BaseModel):
    """
    AuthResponse model
        Authentication response model.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    user_id : str = Field(validation_alias="user_id" )
    
    email : Union[str,None] = Field(validation_alias="email" )
    
    role : str = Field(validation_alias="role" )
    
    authenticated : Optional[bool] = Field(validation_alias="authenticated" , default = None )
    