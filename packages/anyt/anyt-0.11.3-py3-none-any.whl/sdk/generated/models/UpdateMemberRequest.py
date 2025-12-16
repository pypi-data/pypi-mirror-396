from typing import *
from pydantic import BaseModel, Field

class UpdateMemberRequest(BaseModel):
    """
    UpdateMemberRequest model
        Request to update a member&#39;s role.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    role : str = Field(validation_alias="role" )
    