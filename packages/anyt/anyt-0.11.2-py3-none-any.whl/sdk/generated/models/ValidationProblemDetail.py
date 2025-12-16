from typing import *
from pydantic import BaseModel, Field

class ValidationProblemDetail(BaseModel):
    """
    ValidationProblemDetail model
        Problem detail with validation error information.

Extends ProblemDetail to include field-level validation errors.

Attributes:
    errors: List of field-level validation errors
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
    
    errors : Optional[List[Dict[str, Any]]] = Field(validation_alias="errors" , default = None )
    