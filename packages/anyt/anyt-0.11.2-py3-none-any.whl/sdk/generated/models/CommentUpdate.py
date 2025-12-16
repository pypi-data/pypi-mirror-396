from typing import *
from pydantic import BaseModel, Field

class CommentUpdate(BaseModel):
    """
    CommentUpdate model
        Fields that can be updated.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    content : Optional[Union[str,None]] = Field(validation_alias="content" , default = None )
    
    mentioned_users : Optional[Union[List[str],None]] = Field(validation_alias="mentioned_users" , default = None )
    