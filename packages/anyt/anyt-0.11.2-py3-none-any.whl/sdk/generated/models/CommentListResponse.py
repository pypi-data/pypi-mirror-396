from typing import *
from pydantic import BaseModel, Field
from .CommentResponse import CommentResponse

class CommentListResponse(BaseModel):
    """
    CommentListResponse model
        Response for paginated comment list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    comments : List[CommentResponse] = Field(validation_alias="comments" )
    
    total : int = Field(validation_alias="total" )
    