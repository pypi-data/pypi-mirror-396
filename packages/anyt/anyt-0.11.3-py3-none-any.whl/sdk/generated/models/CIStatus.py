from enum import Enum

class CIStatus(str, Enum):
    
        PENDING = 'pending'
        
        SUCCESS = 'success'
        
        FAILURE = 'failure'
        
        ERROR = 'error'
        