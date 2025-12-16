from typing import *
from pydantic import BaseModel, Field

class ConflictProblemDetail(BaseModel):
    """
    ConflictProblemDetail model
        Problem detail for version conflicts (optimistic locking).

Used for 409 Conflict responses when a resource has been modified
since the client last read it.

Attributes:
    current_version: The current version of the resource in the database
    provided_version: The version provided in the update request
    conflicts: Optional list of conflicting fields with their values
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    type : Optional[Union[str,str]] = Field(validation_alias="type" , default = None )
    
    title : str = Field(validation_alias="title" )
    
    status : int = Field(validation_alias="status" )
    
    detail : Optional[Union[str,None]] = Field(validation_alias="detail" , default = None )
    
    instance : Optional[Union[str,None]] = Field(validation_alias="instance" , default = None )
    
    current_version : int = Field(validation_alias="current_version" )
    
    provided_version : int = Field(validation_alias="provided_version" )
    
    conflicts : Optional[Union[List[Dict[str, Any]],None]] = Field(validation_alias="conflicts" , default = None )
    