from typing import *
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    """
    HealthResponse model
        Health check response data.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    status : str = Field(validation_alias="status" )
    
    timestamp : str = Field(validation_alias="timestamp" )
    
    version : str = Field(validation_alias="version" )
    
    database : str = Field(validation_alias="database" )
    