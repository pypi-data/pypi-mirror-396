from typing import *
from pydantic import BaseModel, Field

class CreateInstallationRequest(BaseModel):
    """
    CreateInstallationRequest model
        Request to store a GitHub App installation.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    installation_id : int = Field(validation_alias="installation_id" )
    
    setup_action : Optional[str] = Field(validation_alias="setup_action" , default = None )
    