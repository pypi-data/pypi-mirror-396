from typing import *
from pydantic import BaseModel, Field
from .BulkTaskResult import BulkTaskResult

class BulkUpdateTasksResponse(BaseModel):
    """
    BulkUpdateTasksResponse model
        Response for bulk task updates.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    results : List[BulkTaskResult] = Field(validation_alias="results" )
    
    updated : int = Field(validation_alias="updated" )
    
    total : Optional[Union[int,None]] = Field(validation_alias="total" , default = None )
    
    succeeded : Optional[Union[int,None]] = Field(validation_alias="succeeded" , default = None )
    
    failed : Optional[Union[int,None]] = Field(validation_alias="failed" , default = None )
    