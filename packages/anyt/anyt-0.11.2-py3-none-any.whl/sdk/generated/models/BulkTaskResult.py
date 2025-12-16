from typing import *
from pydantic import BaseModel, Field

class BulkTaskResult(BaseModel):
    """
    BulkTaskResult model
        Result of a single task operation in a bulk update.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    identifier : str = Field(validation_alias="identifier" )
    
    task_id : Optional[Union[str,None]] = Field(validation_alias="task_id" , default = None )
    
    success : bool = Field(validation_alias="success" )
    
    message : Optional[Union[str,None]] = Field(validation_alias="message" , default = None )
    
    error : Optional[Union[str,None]] = Field(validation_alias="error" , default = None )
    