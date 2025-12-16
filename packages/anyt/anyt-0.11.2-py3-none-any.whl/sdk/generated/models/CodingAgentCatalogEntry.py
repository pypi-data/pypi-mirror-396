from typing import *
from pydantic import BaseModel, Field
from .CodingAgentType import CodingAgentType

class CodingAgentCatalogEntry(BaseModel):
    """
    CodingAgentCatalogEntry model
        A single coding agent entry in the catalog.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    agent_type : CodingAgentType = Field(validation_alias="agent_type" )
    
    name : str = Field(validation_alias="name" )
    
    description : str = Field(validation_alias="description" )
    
    website_url : Optional[Union[str,None]] = Field(validation_alias="website_url" , default = None )
    
    documentation_url : Optional[Union[str,None]] = Field(validation_alias="documentation_url" , default = None )
    
    supported_models : Optional[List[str]] = Field(validation_alias="supported_models" , default = None )
    
    features : Optional[List[str]] = Field(validation_alias="features" , default = None )
    