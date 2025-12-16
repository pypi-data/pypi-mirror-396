from typing import *
from pydantic import BaseModel, Field

class ExternalRepo(BaseModel):
    """
    ExternalRepo model
        Full external repo schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    provider : Optional[str] = Field(validation_alias="provider" , default = None )
    
    owner : str = Field(validation_alias="owner" )
    
    name : str = Field(validation_alias="name" )
    
    full_name : str = Field(validation_alias="full_name" )
    
    html_url : str = Field(validation_alias="html_url" )
    
    clone_url : str = Field(validation_alias="clone_url" )
    
    default_branch : Optional[str] = Field(validation_alias="default_branch" , default = None )
    
    github_installation_id : Optional[Union[int,None]] = Field(validation_alias="github_installation_id" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    