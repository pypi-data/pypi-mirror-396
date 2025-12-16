from typing import *
from pydantic import BaseModel, Field

class CreateRepositoryRequest(BaseModel):
    """
    CreateRepositoryRequest model
        Request to create a new GitHub repository.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    private : Optional[bool] = Field(validation_alias="private" , default = None )
    
    auto_init : Optional[bool] = Field(validation_alias="auto_init" , default = None )
    
    project_id : Optional[Union[int,None]] = Field(validation_alias="project_id" , default = None )
    