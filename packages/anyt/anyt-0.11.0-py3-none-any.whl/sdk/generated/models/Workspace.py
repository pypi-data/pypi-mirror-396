from typing import *
from pydantic import BaseModel, Field

class Workspace(BaseModel):
    """
    Workspace model
        Full workspace schema.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : str = Field(validation_alias="name" )
    
    identifier : str = Field(validation_alias="identifier" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    owner_id : str = Field(validation_alias="owner_id" )
    
    task_counter : int = Field(validation_alias="task_counter" )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    
    deleted_at : Optional[Union[str,None]] = Field(validation_alias="deleted_at" , default = None )
    