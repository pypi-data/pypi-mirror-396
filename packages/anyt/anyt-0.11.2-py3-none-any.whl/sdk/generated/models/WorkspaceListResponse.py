from typing import *
from pydantic import BaseModel, Field
from .Workspace import Workspace

class WorkspaceListResponse(BaseModel):
    """
    WorkspaceListResponse model
        Response for paginated workspace list.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    items : List[Workspace] = Field(validation_alias="items" )
    
    total : int = Field(validation_alias="total" )
    
    page : int = Field(validation_alias="page" )
    
    per_page : int = Field(validation_alias="per_page" )
    
    total_pages : int = Field(validation_alias="total_pages" )
    