from enum import Enum

class ReviewStatus(str, Enum):
    
        PENDING = 'pending'
        
        APPROVED = 'approved'
        
        CHANGES_REQUESTED = 'changes_requested'
        
        DISMISSED = 'dismissed'
        