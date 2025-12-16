from typing import *
from pydantic import BaseModel, Field

class CreateWorkspaceRequest(BaseModel):
    """
    CreateWorkspaceRequest model
        Request for creating a new workspace.

Note: owner_id is not included as it&#39;s derived from the authenticated actor.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    identifier : str = Field(validation_alias="identifier" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    