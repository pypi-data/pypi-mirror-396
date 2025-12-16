from enum import Enum

class CIConclusion(str, Enum):
    
        SUCCESS = 'success'
        
        FAILURE = 'failure'
        
        NEUTRAL = 'neutral'
        
        CANCELLED = 'cancelled'
        
        SKIPPED = 'skipped'
        
        TIMED_OUT = 'timed_out'
        
        ACTION_REQUIRED = 'action_required'
        