from typing import *
from pydantic import BaseModel, Field
from .GitHubRepo import GitHubRepo

class InstallationReposResponse(BaseModel):
    """
    InstallationReposResponse model
        Response for listing installation repositories.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    total_count : int = Field(validation_alias="total_count" )
    
    repositories : Optional[List[Optional[GitHubRepo]]] = Field(validation_alias="repositories" , default = None )
    
    page : int = Field(validation_alias="page" )
    
    per_page : int = Field(validation_alias="per_page" )
    
    has_more : bool = Field(validation_alias="has_more" )
    