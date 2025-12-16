from typing import *
from pydantic import BaseModel, Field
from .Workspace import Workspace
from .Project import Project

class UserSetupResponse(BaseModel):
    """
    UserSetupResponse model
        Response schema for user setup.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    workspace : Workspace = Field(validation_alias="workspace" )
    
    project : Project = Field(validation_alias="project" )
    
    is_new_setup : bool = Field(validation_alias="is_new_setup" )
    