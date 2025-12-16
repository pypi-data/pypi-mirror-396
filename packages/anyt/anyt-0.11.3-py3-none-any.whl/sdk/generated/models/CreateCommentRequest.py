from typing import *
from pydantic import BaseModel, Field

class CreateCommentRequest(BaseModel):
    """
    CreateCommentRequest model
        Request model for creating a comment - only client-provided fields.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    content : str = Field(validation_alias="content" )
    
    mentioned_users : Optional[Union[List[str],None]] = Field(validation_alias="mentioned_users" , default = None )
    
    parent_id : Optional[Union[int,None]] = Field(validation_alias="parent_id" , default = None )
    