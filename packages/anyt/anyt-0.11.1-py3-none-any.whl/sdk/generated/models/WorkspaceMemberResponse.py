from typing import *
from pydantic import BaseModel, Field

class WorkspaceMemberResponse(BaseModel):
    """
    WorkspaceMemberResponse model
        Workspace member information.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    user_id : str = Field(validation_alias="user_id" )
    
    role : str = Field(validation_alias="role" )
    
    created_at : str = Field(validation_alias="created_at" )
    