from typing import *
from pydantic import BaseModel, Field

class CommentStatsResponse(BaseModel):
    """
    CommentStatsResponse model
        Statistics about task comments.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    task_id : str = Field(validation_alias="task_id" )
    
    total_comments : int = Field(validation_alias="total_comments" )
    
    unread_mentions : int = Field(validation_alias="unread_mentions" )
    
    last_comment_at : Optional[Union[str,None]] = Field(validation_alias="last_comment_at" , default = None )
    