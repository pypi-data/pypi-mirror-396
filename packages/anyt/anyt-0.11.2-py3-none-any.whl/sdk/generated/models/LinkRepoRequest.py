from typing import *
from pydantic import BaseModel, Field

class LinkRepoRequest(BaseModel):
    """
    LinkRepoRequest model
        Request to link a GitHub repository to a project.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    full_name : str = Field(validation_alias="full_name" )
    
    default_branch : Optional[str] = Field(validation_alias="default_branch" , default = None )
    