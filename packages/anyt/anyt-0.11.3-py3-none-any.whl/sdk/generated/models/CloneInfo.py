from typing import *
from pydantic import BaseModel, Field

class CloneInfo(BaseModel):
    """
    CloneInfo model
        Response containing authenticated clone URL and repository info.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    clone_url : str = Field(validation_alias="clone_url" )
    
    branch : str = Field(validation_alias="branch" )
    
    project_id : int = Field(validation_alias="project_id" )
    
    external_repo_id : int = Field(validation_alias="external_repo_id" )
    