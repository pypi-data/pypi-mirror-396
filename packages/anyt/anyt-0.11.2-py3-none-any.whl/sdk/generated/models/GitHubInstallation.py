from typing import *
from pydantic import BaseModel, Field

class GitHubInstallation(BaseModel):
    """
    GitHubInstallation model
        Domain model for GitHub installation.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    user_id : str = Field(validation_alias="user_id" )
    
    installation_id : int = Field(validation_alias="installation_id" )
    
    github_account_login : str = Field(validation_alias="github_account_login" )
    
    github_account_type : str = Field(validation_alias="github_account_type" )
    
    github_account_id : int = Field(validation_alias="github_account_id" )
    
    github_avatar_url : Optional[Union[str,None]] = Field(validation_alias="github_avatar_url" , default = None )
    
    permissions : Optional[Dict[str, Any]] = Field(validation_alias="permissions" , default = None )
    
    repository_selection : Optional[Union[str,None]] = Field(validation_alias="repository_selection" , default = None )
    
    suspended_at : Optional[Union[str,None]] = Field(validation_alias="suspended_at" , default = None )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    