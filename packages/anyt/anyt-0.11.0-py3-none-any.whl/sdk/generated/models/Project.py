from typing import *
from pydantic import BaseModel, Field
from .ProjectStatus import ProjectStatus
from .ExternalRepo import ExternalRepo

class Project(BaseModel):
    """
    Project model
        Full project schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    status : Optional[ProjectStatus] = Field(validation_alias="status" , default = None )
    
    lead_id : Optional[Union[str,None]] = Field(validation_alias="lead_id" , default = None )
    
    start_date : Optional[Union[str,None]] = Field(validation_alias="start_date" , default = None )
    
    target_date : Optional[Union[str,None]] = Field(validation_alias="target_date" , default = None )
    
    color : Optional[Union[str,None]] = Field(validation_alias="color" , default = None )
    
    icon : Optional[Union[str,None]] = Field(validation_alias="icon" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    external_repo_id : Optional[Union[int,None]] = Field(validation_alias="external_repo_id" , default = None )
    
    external_repo : Optional[Union[ExternalRepo,None]] = Field(validation_alias="external_repo" , default = None )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    
    deleted_at : Optional[Union[str,None]] = Field(validation_alias="deleted_at" , default = None )
    