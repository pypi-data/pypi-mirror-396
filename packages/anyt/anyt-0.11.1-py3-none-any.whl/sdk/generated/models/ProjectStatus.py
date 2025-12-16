from enum import Enum

class ProjectStatus(str, Enum):
    
        ACTIVE = 'active'
        
        PAUSED = 'paused'
        
        COMPLETED = 'completed'
        
        CANCELED = 'canceled'
        