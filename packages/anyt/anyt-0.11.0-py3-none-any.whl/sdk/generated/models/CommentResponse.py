from typing import *
from pydantic import BaseModel, Field

class CommentResponse(BaseModel):
    """
    CommentResponse model
        Enhanced comment response with author info and metadata.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    id : int = Field(validation_alias="id" )
    
    task_id : str = Field(validation_alias="task_id" )
    
    author_id : str = Field(validation_alias="author_id" )
    
    author_name : Optional[Union[str,None]] = Field(validation_alias="author_name" , default = None )
    
    author_avatar : Optional[Union[str,None]] = Field(validation_alias="author_avatar" , default = None )
    
    content : str = Field(validation_alias="content" )
    
    mentioned_users : List[str] = Field(validation_alias="mentioned_users" )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : Optional[Union[str,None]] = Field(validation_alias="updated_at" , default = None )
    
    is_edited : bool = Field(validation_alias="is_edited" )
    
    is_own : bool = Field(validation_alias="is_own" )
    