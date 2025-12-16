from enum import Enum

class TaskStatus(str, Enum):
    
        BACKLOG = 'backlog'
        
        TODO = 'todo'
        
        ACTIVE = 'active'
        
        BLOCKED = 'blocked'
        
        CANCELED = 'canceled'
        
        DONE = 'done'
        
        ARCHIVED = 'archived'
        