from typing import *
from pydantic import BaseModel, Field
from .TaskStatus import TaskStatus
from .AssigneeType import AssigneeType

class CreateTaskRequest(BaseModel):
    """
    CreateTaskRequest model
        Request for creating a new task in a workspace.

Tasks are workspace-scoped and optionally belong to a project.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    project_id : int = Field(validation_alias="project_id" )
    
    title : str = Field(validation_alias="title" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    phase : Optional[Union[str,None]] = Field(validation_alias="phase" , default = None )
    
    status : Optional[TaskStatus] = Field(validation_alias="status" , default = None )
    
    priority : Optional[int] = Field(validation_alias="priority" , default = None )
    
    owner_id : Optional[Union[str,None]] = Field(validation_alias="owner_id" , default = None )
    
    assignee_type : Optional[AssigneeType] = Field(validation_alias="assignee_type" , default = None )
    
    parent_id : Optional[Union[int,None]] = Field(validation_alias="parent_id" , default = None )
    
    depends_on : Optional[Union[List[str],None]] = Field(validation_alias="depends_on" , default = None )
    
    implementation_plan : Optional[Union[str,None]] = Field(validation_alias="implementation_plan" , default = None )
    
    checklist : Optional[Union[str,None]] = Field(validation_alias="checklist" , default = None )
    