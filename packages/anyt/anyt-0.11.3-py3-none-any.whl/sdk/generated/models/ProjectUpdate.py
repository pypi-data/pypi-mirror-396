from typing import *
from pydantic import BaseModel, Field
from .ProjectStatus import ProjectStatus

class ProjectUpdate(BaseModel):
    """
    ProjectUpdate model
        Fields that can be updated (all optional).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : Optional[Union[str,None]] = Field(validation_alias="name" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    status : Optional[Union[ProjectStatus,None]] = Field(validation_alias="status" , default = None )
    
    lead_id : Optional[Union[str,None]] = Field(validation_alias="lead_id" , default = None )
    
    start_date : Optional[Union[str,None]] = Field(validation_alias="start_date" , default = None )
    
    target_date : Optional[Union[str,None]] = Field(validation_alias="target_date" , default = None )
    
    color : Optional[Union[str,None]] = Field(validation_alias="color" , default = None )
    
    icon : Optional[Union[str,None]] = Field(validation_alias="icon" , default = None )
    
    external_repo_id : Optional[Union[int,None]] = Field(validation_alias="external_repo_id" , default = None )
    