from typing import *
from pydantic import BaseModel, Field
from .WorkspaceMemberResponse import WorkspaceMemberResponse

class WorkspaceMemberListResponse(BaseModel):
    """
    WorkspaceMemberListResponse model
        Response for paginated workspace member list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    items : List[WorkspaceMemberResponse] = Field(validation_alias="items" )
    
    total : int = Field(validation_alias="total" )
    
    page : int = Field(validation_alias="page" )
    
    per_page : int = Field(validation_alias="per_page" )
    
    total_pages : int = Field(validation_alias="total_pages" )
    