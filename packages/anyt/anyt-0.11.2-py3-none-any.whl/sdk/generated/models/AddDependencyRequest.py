from typing import *
from pydantic import BaseModel, Field

class AddDependencyRequest(BaseModel):
    """
    AddDependencyRequest model
        Request for adding a dependency to a task.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    depends_on : str = Field(validation_alias="depends_on" )
    