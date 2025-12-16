from typing import *
from pydantic import BaseModel, Field
from .TaskSuggestion_Output import TaskSuggestion_Output

class TaskSuggestionsResponse(BaseModel):
    """
    TaskSuggestionsResponse model
        Response for task suggestions endpoint.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    suggestions : List[TaskSuggestion_Output] = Field(validation_alias="suggestions" )
    
    total_ready : int = Field(validation_alias="total_ready" )
    
    total_blocked : int = Field(validation_alias="total_blocked" )
    