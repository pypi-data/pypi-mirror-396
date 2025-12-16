from typing import *
from pydantic import BaseModel, Field
from .ProjectStatus import ProjectStatus

class CreateProjectRequest(BaseModel):
    """
    CreateProjectRequest model
        Request for creating a new project.

Note: workspace_id is not included as it&#39;s derived from the URL path parameter.
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
    