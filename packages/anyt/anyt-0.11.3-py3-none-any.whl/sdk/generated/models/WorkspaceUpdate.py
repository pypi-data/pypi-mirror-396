from typing import *
from pydantic import BaseModel, Field

class WorkspaceUpdate(BaseModel):
    """
    WorkspaceUpdate model
        Fields that can be updated.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    name : Optional[Union[str,None]] = Field(validation_alias="name" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    