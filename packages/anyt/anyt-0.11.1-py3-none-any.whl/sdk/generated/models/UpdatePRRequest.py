from typing import *
from pydantic import BaseModel, Field
from .PRStatus import PRStatus
from .ReviewStatus import ReviewStatus
from .CIStatus import CIStatus
from .CIConclusion import CIConclusion

class UpdatePRRequest(BaseModel):
    """
    UpdatePRRequest model
        Request for updating an existing pull request record.
            """
    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }
    
    pr_status : Optional[Union[PRStatus,None]] = Field(validation_alias="pr_status" , default = None )
    
    review_status : Optional[Union[ReviewStatus,None]] = Field(validation_alias="review_status" , default = None )
    
    review_count : Optional[Union[int,None]] = Field(validation_alias="review_count" , default = None )
    
    approved_count : Optional[Union[int,None]] = Field(validation_alias="approved_count" , default = None )
    
    changes_requested_count : Optional[Union[int,None]] = Field(validation_alias="changes_requested_count" , default = None )
    
    ci_status : Optional[Union[CIStatus,None]] = Field(validation_alias="ci_status" , default = None )
    
    ci_conclusion : Optional[Union[CIConclusion,None]] = Field(validation_alias="ci_conclusion" , default = None )
    
    ci_check_runs_total : Optional[Union[int,None]] = Field(validation_alias="ci_check_runs_total" , default = None )
    
    ci_check_runs_completed : Optional[Union[int,None]] = Field(validation_alias="ci_check_runs_completed" , default = None )
    
    ci_check_runs_failed : Optional[Union[int,None]] = Field(validation_alias="ci_check_runs_failed" , default = None )
    
    mergeable : Optional[Union[bool,None]] = Field(validation_alias="mergeable" , default = None )
    
    mergeable_state : Optional[Union[str,None]] = Field(validation_alias="mergeable_state" , default = None )
    
    merge_commit_sha : Optional[Union[str,None]] = Field(validation_alias="merge_commit_sha" , default = None )
    
    head_sha : Optional[Union[str,None]] = Field(validation_alias="head_sha" , default = None )
    
    extra_metadata : Optional[Union[Dict[str, Any],None]] = Field(validation_alias="extra_metadata" , default = None )
    