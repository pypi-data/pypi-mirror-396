from typing import *
from pydantic import BaseModel, Field

class GitHubRepo(BaseModel):
    """
    GitHubRepo model
        Repository info from GitHub API.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    name : str = Field(validation_alias="name" )
    
    full_name : str = Field(validation_alias="full_name" )
    
    private : bool = Field(validation_alias="private" )
    
    html_url : str = Field(validation_alias="html_url" )
    
    clone_url : str = Field(validation_alias="clone_url" )
    
    default_branch : Optional[str] = Field(validation_alias="default_branch" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    language : Optional[Union[str,None]] = Field(validation_alias="language" , default = None )
    
    updated_at : str = Field(validation_alias="updated_at" )
    