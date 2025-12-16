from typing import *
from pydantic import BaseModel, Field

class AddMemberRequest(BaseModel):
    """
    AddMemberRequest model
        Request to add a member to a workspace.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    user_id : str = Field(validation_alias="user_id" )
    
    role : str = Field(validation_alias="role" )
    