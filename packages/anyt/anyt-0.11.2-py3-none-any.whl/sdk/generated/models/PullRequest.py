from typing import *
from pydantic import BaseModel, Field
from .PRStatus import PRStatus
from .ReviewStatus import ReviewStatus
from .CIStatus import CIStatus
from .CIConclusion import CIConclusion

class PullRequest(BaseModel):
    """
    PullRequest model
        Full pull request schema with all fields.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    pr_number : int = Field(validation_alias="pr_number" )
    
    pr_url : str = Field(validation_alias="pr_url" )
    
    head_branch : str = Field(validation_alias="head_branch" )
    
    base_branch : str = Field(validation_alias="base_branch" )
    
    head_sha : str = Field(validation_alias="head_sha" )
    
    pr_status : Optional[PRStatus] = Field(validation_alias="pr_status" , default = None )
    
    review_status : Optional[ReviewStatus] = Field(validation_alias="review_status" , default = None )
    
    review_count : Optional[int] = Field(validation_alias="review_count" , default = None )
    
    approved_count : Optional[int] = Field(validation_alias="approved_count" , default = None )
    
    changes_requested_count : Optional[int] = Field(validation_alias="changes_requested_count" , default = None )
    
    ci_status : Optional[CIStatus] = Field(validation_alias="ci_status" , default = None )
    
    ci_conclusion : Optional[Union[CIConclusion,None]] = Field(validation_alias="ci_conclusion" , default = None )
    
    ci_check_runs_total : Optional[int] = Field(validation_alias="ci_check_runs_total" , default = None )
    
    ci_check_runs_completed : Optional[int] = Field(validation_alias="ci_check_runs_completed" , default = None )
    
    ci_check_runs_failed : Optional[int] = Field(validation_alias="ci_check_runs_failed" , default = None )
    
    mergeable : Optional[Union[bool,None]] = Field(validation_alias="mergeable" , default = None )
    
    mergeable_state : Optional[Union[str,None]] = Field(validation_alias="mergeable_state" , default = None )
    
    merge_commit_sha : Optional[Union[str,None]] = Field(validation_alias="merge_commit_sha" , default = None )
    
    extra_metadata : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="extra_metadata" , default = None )
    
    id : int = Field(validation_alias="id" )
    
    task_id : int = Field(validation_alias="task_id" )
    
    workspace_id : int = Field(validation_alias="workspace_id" )
    
    project_id : int = Field(validation_alias="project_id" )
    
    opened_at : str = Field(validation_alias="opened_at" )
    
    merged_at : Optional[Union[str,None]] = Field(validation_alias="merged_at" , default = None )
    
    closed_at : Optional[Union[str,None]] = Field(validation_alias="closed_at" , default = None )
    
    created_at : str = Field(validation_alias="created_at" )
    
    updated_at : str = Field(validation_alias="updated_at" )
    