from typing import *
from pydantic import BaseModel, Field
from .TaskStatus import TaskStatus
from .AssigneeType import AssigneeType
from .CodingAgentType import CodingAgentType

class Task(BaseModel):
    """
    Task model
        Full task schema with relationships.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    title : str = Field(validation_alias="title" )
    
    description : Optional[Union[str,None]] = Field(validation_alias="description" , default = None )
    
    phase : Optional[Union[str,None]] = Field(validation_alias="phase" , default = None )
    
    status : Optional[TaskStatus] = Field(validation_alias="status" , default = None )
    
    priority : Optional[int] = Field(validation_alias="priority" , default = None )
    
    owner_id : Optional[Union[str,None]] = Field(validation_alias="owner_id" , default = None )
    
    assignee_type : Optional[AssigneeType] = Field(validation_alias="assignee_type" , default = None )
    
    assigned_coding_agent : Optional[Union[CodingAgentType,None]] = Field(validation_alias="assigned_coding_agent" , default = None )
    
    parent_id : Optional[Union[int,None]] = Field(validation_alias="parent_id" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    project_id : int = Field(validation_alias="project_id" )
    
    number : int = Field(validation_alias="number" )
    
    identifier : str = Field(validation_alias="identifier" )
    
    uid : str = Field(validation_alias="uid" )
    
    creator_id : str = Field(validation_alias="creator_id" )
    
    version : int = Field(validation_alias="version" )
    
    started_at : Optional[Union[str,None]] = Field(validation_alias="started_at" , default = None )
    
    completed_at : Optional[Union[str,None]] = Field(validation_alias="completed_at" , default = None )
    
    canceled_at : Optional[Union[str,None]] = Field(validation_alias="canceled_at" , default = None )
    
    archived_at : Optional[Union[str,None]] = Field(validation_alias="archived_at" , default = None )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    
    deleted_at : Optional[Union[str,None]] = Field(validation_alias="deleted_at" , default = None )
    
    implementation_plan : Optional[Union[str,None]] = Field(validation_alias="implementation_plan" , default = None )
    
    checklist : Optional[Union[str,None]] = Field(validation_alias="checklist" , default = None )
    