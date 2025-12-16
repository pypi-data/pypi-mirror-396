from typing import *
from pydantic import BaseModel, Field
from .TaskStatus import TaskStatus
from .AssigneeType import AssigneeType
from .CodingAgentType import CodingAgentType

class TaskUpdate(BaseModel):
    """
    TaskUpdate model
        Fields that can be updated (all optional).
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    title : Optional[Union[str,None]] = Field(validation_alias="title" , default = None )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    phase : Optional[Union[str,None]] = Field(validation_alias="phase" , default = None )
    
    status : Optional[Union[TaskStatus,None]] = Field(validation_alias="status" , default = None )
    
    priority : Optional[Union[int,None]] = Field(validation_alias="priority" , default = None )
    
    owner_id : Optional[Union[str,None]] = Field(validation_alias="owner_id" , default = None )
    
    assignee_type : Optional[Union[AssigneeType,None]] = Field(validation_alias="assignee_type" , default = None )
    
    assigned_coding_agent : Optional[Union[CodingAgentType,None]] = Field(validation_alias="assigned_coding_agent" , default = None )
    
    project_id : Optional[Union[int,None]] = Field(validation_alias="project_id" , default = None )
    
    parent_id : Optional[Union[int,None]] = Field(validation_alias="parent_id" , default = None )
    
    implementation_plan : Optional[Union[str,None]] = Field(validation_alias="implementation_plan" , default = None )
    
    checklist : Optional[Union[str,None]] = Field(validation_alias="checklist" , default = None )
    